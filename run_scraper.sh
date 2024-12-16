#!/usr/bin/env bash
# bash run_scraper.sh

# Scrape acts and add to .json
scrapy crawl ActData -o storage/output.json:json && \

# Create databaseif not exists
DATABASE="database/ActsData.db"
if [ ! -f "$DATABASE" ]; then
    python3 -m database.create_db
fi

# Read .json and add data into DB
python3 -m database.add_data_into_db && \

# Run mail sender
python3 -m mail_sender.send_email && \

# Delete output.json and downloads folders
rm -r storage/