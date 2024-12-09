#!/usr/bin/env bash
# bash run_scraper.sh

# Scrape acts and add to .json
# scrapy crawl ActData -o output.json:json  && \

# Create databaseif not exists
DATABASE="ActsData.db"
if [ ! -f "$DATABASE" ]; then
    python3 WebScraper/Database/CreateDB.py
fi

# Read .json and add data into DB
python3 WebScraper/Database/AddDataToDB.py 

# Run mail sender
# python3 -m WebScraper.MailSender.PrepareEmailData  && \

# Delete output.json and downloads folder 
# rm -r downloads
# rm -r docx_downloads
# rm output.json