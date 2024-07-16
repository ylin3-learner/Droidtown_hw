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
    def __init__(self, json_filename, account_manager, directory=None):
        self._json_filename = json_filename
        self._account_manager = account_manager
        self._articut = Articut(
            username=account_manager.username, apikey=account_manager.apikey)
        self.directory = directory or "data"

    def load_crawled_data_from_files(self, directory):
        json_files = []
        crawled_data = []

        # Get all file_path of .json files
        for root, _, files in os.walk(self.directory):
            for filename in files:
                if filename.endswith(".json"):
                    json_files.append(os.path.join(root, filename))
                    
        # Load data from each files
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding="utf-8") as file:
                    file_data = json.load(file)
                    crawled_data.extend(file_data)
                    
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading JSON file {json_file}: {str(e)}")
                
        return crawled_data

    def parse_content(self):
        crawled_data = self.load_crawled_data_from_files(self.directory)
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