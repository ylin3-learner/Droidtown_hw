import os
import json
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from recorder import CrawledLinksLogger

logger = logging.getLogger(__name__)

class Locator:
    def __init__(self):
        self.locators = {
            "default": {
                "title_xpath": '//h1[@class="article-content__title"] | //h1[@class="story_art_title"]',
                "content_xpath": '//section[@class="article-content__editor"]/p | //section[@class="article-content__editor "]/p | //p',
                "time_xpath": '//time[@class="article-content__time"] | //div[@id="story_bady_info"]'
            },
            # "alternative1": {
            # "title_xpath": '//h1',
            # "content_xpath": '//section[@class="article-content__editor "]/p',
            # "time_xpath": '//time[@class="article-content__time"]'
            # },
            # Add more locator sets as needed
        }

class NewsParser:
    def __init__(self, driver):
        self.__driver = driver
        self.used_locators = set()  # Track used locator sets by their keys

class NewsParser:
    def __init__(self, driver):
        self.__driver = driver
        self.used_locators = set()  # Track used locator sets by their keys
        self.locator = Locator()  # Initialize Locator instance

    def parse(self, url, locator_key="default"):
        self.__driver.get(url)

        try:
            # Check if the locator_key is valid
            if locator_key not in self.locator.locators:
                raise ValueError(f"Locator key '{locator_key}' not found.")

            locators = self.locator.locators[locator_key]

            title = WebDriverWait(self.__driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, locators["title_xpath"]))
            ).text

            content_elements = WebDriverWait(self.__driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, locators["content_xpath"]))
            )
            content = "".join(element.text for element in content_elements)

            time_element = WebDriverWait(self.__driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, locators["time_xpath"]))
            ).text

            return {
                'title': title,
                'content': content,
                'time': time_element
            }

        except (TimeoutException, WebDriverException, ValueError) as e:
            logger.error(f"Failed to parse content from URL: {
                         url}. Error: {str(e)}")
            return None

    def save_results_to_json(self, results, filename, directory=None):
        try:
            if directory is None:
                directory = 'data'
            
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


if __name__ == "__main__":
    from selenium import webdriver

    # Set up WebDriver (e.g., ChromeDriver)
    driver = webdriver.Chrome()

    # Initialize Locator and NewsParser
    locator = Locator()
    news_parser = NewsParser(driver)

    # Parse a specific URL
    url = 'https://house.udn.com/house/story/123591/8096515'
    # Corrected to use locator_key instead of locator
    parsed_data = news_parser.parse(url, locator_key="default")

    if parsed_data:
        # Save the parsed data to JSON
        news_parser.save_results_to_json(
            [parsed_data], 'parsed_news', 'data')
    else:
        logger.error("Failed to parse the news article.")

    driver.quit()
