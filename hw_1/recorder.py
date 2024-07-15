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
