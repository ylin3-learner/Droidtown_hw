import os
import json
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

class Locator:
    def __init__(self):
        self.locators = {
            "default": {
                "title_xpath": '//h1[@class="article-content__title"]',
                "content_xpath": '//section[@class="article-content__editor"]/p | //section[@class="article-content__editor "]/p',
                "time_xpath": '//time[@class="article-content__time"]'
            },
            #"alternative1": {
                #"title_xpath": '//h1',
                #"content_xpath": '//section[@class="article-content__editor "]/p',
                #"time_xpath": '//time[@class="article-content__time"]'
            #},
            # Add more locator sets as needed
        }

class NewsParser:
    def __init__(self, driver):
        self.__driver = driver
        self.used_locators = set()  # Track used locator sets by their keys

    def parse(self, url, locator):
        self.__driver.get(url)
        for key, locator_set in locator.locators.items():
            if key in self.used_locators:
                logger.info(f"Skipping already used locator set: {key}")
                continue

            try:
                logger.info(f"Trying locator set: {key}")

                title = WebDriverWait(self.__driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, locator_set["title_xpath"]))
                ).text

                # content_elements: a list of WebElement objects
                content_elements = WebDriverWait(self.__driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, locator_set["content_xpath"]))
                )

                # extract all matching elements and then concatenate their text.
                content = "".join(
                    [element.text for element in content_elements])
                
                
                time_element = WebDriverWait(self.__driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, locator_set["time_xpath"]))
                ).text

                return {
                    'title': title,
                    'content': content,
                    'time': time_element
                }
            except (TimeoutException, WebDriverException) as e:
                logger.error(f"Failed to parse content with locator set: {key}. Error: {str(e)}")
                # If unsuccessful, mark this locator set as used
                self.used_locators.add(key)
                logger.info(f"Failed parsed_url: {url}")
                continue

        return None

    def save_results_to_json(self, results, filename, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)

            full_path = os.path.join(directory, f"{filename}.json")

            # If JSON file exists, load file content to existing_data first.
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as file:
                    existing_data = json.load(file)
            else:
                existing_data = []

            # Merge existing data with new results
            if isinstance(existing_data, list):
                existing_data.extend(results)
            else:
                existing_data.append(results)
    
            with open(full_path, 'w', encoding='utf-8') as file:
                json.dump(existing_data, file, ensure_ascii=False, indent=4)
    
            logger.info(f"Results saved to {full_path}")
            return full_path
        except Exception as e:
            logger.error(f"Failed to save results to JSON: {str(e)}")


# Example usage of the modified class
if __name__ == "__main__":
    from selenium import webdriver

    # Set up WebDriver (e.g., ChromeDriver)
    driver = webdriver.Chrome()

    # Initialize Locator and NewsParser
    locator = Locator()
    news_parser = NewsParser(driver)

    # Parse a specific URL
    url = 'https://house.udn.com/house/story/123591/8096515'
    parsed_data = news_parser.parse(url, locator)

    if parsed_data:
        # Save the parsed data to JSON
        news_parser.save_results_to_json([parsed_data], 'parsed_news', 'data')
    else:
        logger.error("Failed to parse the news article.")

    driver.quit()