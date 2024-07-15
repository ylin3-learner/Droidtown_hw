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

def get_json_files(directory):
    json_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.json'):
                json_files.append(os.path.join(root, filename))
    return json_files

def process_target_url(target_url, link_locator, locator, filename, limit=3, directory='data', crawled_links_logger=None):
    try:
        logger.info(f"Initializing WebDriver for URL: {target_url}")
        target_initializer = WebDriverInitializer(url=target_url)
        target_driver = target_initializer.initialize()

        # Initialize AccountManager
        account_manager = AccountManager()      

        if target_driver is None:
            logger.error(
                "Failed to initialize WebDriver for target URL. Exiting.")
            return None, None

        logger.info("WebDriver initialized successfully for target URL")

        logger.info(f"Generating links using locator: {link_locator}")
        clicker = ClickerGenerator(driver=target_driver)

        # Explicit wait for the presence of links
        wait = WebDriverWait(target_driver, 10)  # Wait up to 10 seconds
        element_present = EC.presence_of_all_elements_located(
            (By.XPATH, link_locator))
        wait.until(element_present)
        
        links = clicker.generate(locator=link_locator, limit=limit)
        logger.info(f"Found {len(links)} links to click")

        crawled_links = crawled_links_logger.read_crawled_links()

        # parse webpage
        news_parser = NewsParser(driver=target_driver)
        results = []
        for link in links:
            if link in crawled_links:
                logger.info(f"Skipping already crawled link: {link}")
                continue

            try:
                result = news_parser.parse(url=link, locator=locator)
                if result:
                    results.append(result)
                    crawled_links_logger.write_crawled_link(link)
            except Exception as e:
                logger.error(f"Failed to parse content for {link}: {str(e)}")

        logger.info(f"Results collected for {filename}: {results}")
        full_path = news_parser.save_results_to_json(
            results, filename, directory="data")
        
        # Initialize ArticutManager
        articut_manager = ArticutManager(
            json_filename=full_path, account_manager=account_manager)

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
    link_locator = '//a[@data-content_level="開放閱讀"]'
    filenames = ["house", "international_media"]
    locator = Locator()
    crawled_links_logger = CrawledLinksLogger()

    for target_url, filename in zip(target_urls, filenames):
        process_target_url(
            target_url, link_locator, locator, filename, limit=5, crawled_links_logger=crawled_links_logger)
