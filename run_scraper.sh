#!/usr/bin/env bash
# bash run_scraper.sh

cd /mnt/c/Users/Testinis/Desktop/acts-scraper

# Scrape acts and add to .json
scrapy crawl ActData -o output.json:json

# Create database
DATABASE="ActsData.db"
if [ ! -f "$DATABASE" ]; then
    python3 WebScraper/Database/CreateDB.py
fi

# Read .json and add data into DB
python3 WebScraper/Database/AddDataToDB.py