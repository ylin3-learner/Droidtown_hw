import os
import logging
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from clicker import WebDriverInitializer, ClickerGenerator
from parser import NewsParser, Locator
from recorder import CrawledLinksLogger
from articut_manager import AccountManager, ArticutManager

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def main(target_url, filename, link_locator=None, limit=None, directory=None):
    try:
        logger.info(f"Initializing WebDriver for URL: {target_url}")
        target_initializer = WebDriverInitializer(url=target_url)
        target_driver = target_initializer.initialize()

        # Initialize AccountManager
        account_manager = AccountManager()

        # Initialize Locator
        locator = Locator()

        # Initialize CrawledLinksLogger instance
        crawled_links_logger = CrawledLinksLogger()

        if target_driver is None:
            logger.error(
                "Failed to initialize WebDriver for target URL. Exiting.")
            return None, None

        logger.info("WebDriver initialized successfully for target URL")

        # Create ClickerGenerator using the default locator
        clicker = ClickerGenerator(
            driver=target_driver, locator=link_locator)

        # Explicit wait for the presence of links
        wait = WebDriverWait(target_driver, 10)  # Wait up to 10 seconds
        element_present = EC.presence_of_all_elements_located(
            (By.XPATH, clicker.locator))
        wait.until(element_present)

        # Generate links and filter uncrawled ones
        links = clicker.generate(limit=limit)
        logger.info(f"Found {len(links)} links to click")

        # Filter out already crawled links
        links = crawled_links_logger.find_new_uncrawled_links(links)

        # Parse webpage
        news_parser = NewsParser(driver=target_driver)
        results = []
        for link in links:
            try:
                # Ensure correct locator_key is passed
                result = news_parser.parse(url=link, locator_key="default")
                if result:
                    results.append(result)
                    crawled_links_logger.write_crawled_link(link)
            except Exception as e:
                logger.error(f"Failed to parse content for {link}: {str(e)}")

        logger.info(f"Results collected for {filename}: {results}")
        full_path = news_parser.save_results_to_json(
            results, filename, directory=directory)

        # Initialize ArticutManager
        articut_manager = ArticutManager(
            json_filename=full_path, account_manager=account_manager, directory=directory)

        parsed_results = articut_manager.parse_content()
        for result in parsed_results:
            print(result)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return None, None
    finally:
        if target_driver:
            target_driver.quit()


if __name__ == "__main__":
    target_urls = [
        "https://house.udn.com/house/index",
        "https://udn.com/news/cate/2/7225"
    ]
    filenames = ["house", "international_media"]

    for target_url, filename in zip(target_urls, filenames):
        main(target_url, filename, limit=5)
