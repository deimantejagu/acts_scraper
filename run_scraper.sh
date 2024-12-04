#!/usr/bin/env bash
# bash run_scraper.sh

cd acts-scraper

# Scrape acts and add to .json
scrapy crawl ActData -o output.json

# Read .json and add data into DB
python3 WebScraper/Database/createDB.py