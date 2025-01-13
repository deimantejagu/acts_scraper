# dos2unix run_scraper.sh
# bash run_scraper.sh

LOCK_FILE="/tmp/acts_scraper.lock"
docx_download="storage/docx_downloads"
STORAGE_DIR="storage/"
LOG_FILE="/path/to/logfile.log"
SCRIPT_PATH="/mnt/c/Users/Testinis/Desktop/acts-scraper/run_scraper.sh"
CRON_LOG="/mnt/c/Users/Testinis/Desktop/acts-scraper/cron_test.log"

# Function to reset the script or perform any cleanup
reset_script() {
    echo "Resetting the script..."
    # Stop the cron job
    echo "Disabling cron job..."
    crontab -l | grep -v "/path/to/your/script.sh" | crontab -

        # Delete lock file if it exists
    if [ -f "$LOCK_FILE" ]; then
        echo "Deleting lock file..."
        rm -f "$LOCK_FILE"
    fi

    # Delete storage directory or reset it
    if [ -d "$STORAGE_DIR" ]; then
        echo "Deleting storage directory..."
        rm -rf "$STORAGE_DIR"  # Caution: This will delete the storage completely
    fi

    # Clear log file (optional)
    if [ -f "$LOG_FILE" ]; then
        echo "Clearing log file..."
        > "$LOG_FILE"  # Clears the log file
    fi

    echo "Reset actions completed."

    if [[ "$current_time" == "23:59" ]]; then
        echo "It's 23:59, stopping and resetting the script..."
        # Re-enable the cron job (add back to crontab)
        echo "Re-enabling cron job..."

        # Run the script immediately after reset
        echo "Starting the script immediately..."
        /bin/bash /mnt/c/Users/Testinis/Desktop/acts-scraper/run_scraper.sh
    fi
}

current_time=$(date +"%H:%M")

if [[ "$current_time" == "23:55" ]]; then
    echo "It's 23:55, stopping and resetting the script..."
    reset_script
    exit 0
fi

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

# Create databaseif not exists
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