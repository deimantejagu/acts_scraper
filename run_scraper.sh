# dos2unix run_scraper.sh
# bash run_scraper.sh

LOCK_FILE="/tmp/acts_scraper.lock"
docx_download="storage/docx_downloads"
STORAGE_DIR="storage/"

# Check if the lock file exists. If it does, exit the script.
if [ -e $LOCK_FILE ]; then
    echo "Script is already running. Exiting..." >> /mnt/c/Users/Testinis/Desktop/acts-scraper/cron_test.log
    exit 1
fi

# Create the lock file to prevent other instances from running
touch $LOCK_FILE

echo "Script ran at $(date)" >> /mnt/c/Users/Testinis/Desktop/acts-scraper/cron_test.log && \

cd /mnt/c/Users/Testinis/Desktop/acts-scraper || exit && \

# Scrape acts and add to .json
scrapy crawl ActData -o storage/output.json:json && \

# Create database if not exists
DATABASE="database/ActsData.db"
if [ ! -f "$DATABASE" ]; then
    python3 -m database.create_db
fi

# Read .json and add data into DB
python3 -m database.add_data_into_db && \

# Downloads scraped files
python3 -m utils.prepare_data_from_db && \

if [ -e $docx_download ]; then
    # Run mail sender
    python3 -m mail_sender.send_email && \

    # Pass document to llama3.2
    python3 -m ollama_integration.analyse_documents
fi

# Delete output.json and downloads folders
rm -r $STORAGE_DIR && \

# Remove the lock file after the script finishes
rm -f $LOCK_FILE

# Log the end time
echo "Script ended at $(date)" >> /mnt/c/Users/Testinis/Desktop/acts-scraper/cron_test.log