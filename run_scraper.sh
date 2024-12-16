#!/usr/bin/env bash
# bash run_scraper.sh

# Scrape acts and add to .json
scrapy crawl ActData -o output.json:json && \

# Create databaseif not exists
DATABASE="ActsData.db"
if [ ! -f "$DATABASE" ]; then
    python3 WebScraper/database/create_db.py
fi

# Read .json and add data into DB
python3 -m WebScraper.database.add_data_into_db && \

# Run mail sender
python3 -m mail_sender.send_email && \

# Delete output.json and downloads folders
rm -r downloads 
rm -r docx_downloads 
rm output.json