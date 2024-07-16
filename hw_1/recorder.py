#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json

class CrawledLinksLogger:
    def __init__(self, filename='config/crawled_links.json'):
        self.filename = filename

    def read_crawled_links(self):
        try:
            with open(self.filename, 'r') as file:
                crawled_links = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            crawled_links = []
        return crawled_links

    def write_crawled_link(self, link):
        crawled_links = self.read_crawled_links()
        if link not in crawled_links:
            crawled_links.append(link)
            with open(self.filename, 'w') as file:
                json.dump(crawled_links, file)

    def find_new_uncrawled_links(self, links):
        # Initialize CrawledLinksLogger to check if links already clicked
        crawled_links = self.read_crawled_links() # Use self here
    
        # Convert lists to sets
        links_set = set(links)
        crawled_links_set = set(crawled_links)
    
        # Find links that haven't been crawled yet
        new_links_set = links_set.difference(crawled_links_set)
    
        # Convert the result back to a list
        new_links = list(new_links_set)
    
        return new_links
