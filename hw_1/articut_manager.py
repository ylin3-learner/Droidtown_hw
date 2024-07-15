import json
import os
from ArticutAPI import Articut


class AccountManager:
    def __init__(self, filename="config/account.info"):
        self._filename = filename
        self._username = None
        self._apikey = None

    def read_account_info(self):
        account_info = {}
        try:
            with open(self._filename, 'r') as file:
                for line in file:
                    name, value = line.strip().split('=')
                    account_info[name.strip()] = value.strip()
        except FileNotFoundError:
            print(f"Error: Account info file '{self._filename}' not found.")
        except Exception as e:
            print(f"Error reading account info: {str(e)}")
        return account_info

    @property
    def username(self):
        if not self._username:
            account_info = self.read_account_info()
            self._username = account_info.get('username', '')
        return self._username

    @property
    def apikey(self):
        if not self._apikey:
            account_info = self.read_account_info()
            self._apikey = account_info.get('apikey', '')
        return self._apikey
    

class ArticutManager:
    def __init__(self, json_filename, account_manager):
        self._json_filename = json_filename
        self._account_manager = account_manager
        self._articut = Articut(
            username=account_manager.username, apikey=account_manager.apikey)

    def load_crawled_data(self):
        try:
            with open(self._json_filename, 'r', encoding="utf-8") as file:
                crawled_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            crawled_data = []
        return crawled_data

    def parse_content(self):
        crawled_data = self.load_crawled_data()
        parsed_results = []
        for data in crawled_data:
            content = data.get("content", "")
            if content:
                result_dict = self._articut.parse(content)
                parsed_results.append(result_dict)
        return parsed_results


if __name__ == "__main__":
    # Initialize AccountManager
    account_manager = AccountManager()

    # Initialize ArticutManager
    # Adjust the filename as per your actual setup
    json_filename = 'data/house.json'
    articut_manager = ArticutManager(
        json_filename=json_filename, account_manager=account_manager)

    # Example usage:
    parsed_results = articut_manager.parse_content()
    for result in parsed_results:
        print(result)