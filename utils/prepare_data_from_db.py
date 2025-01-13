import os
import re
import unicodedata
import sys

from collections import Counter
from datetime import datetime, timedelta
from database.create_db_connection import get_connection

MAX_PATH_LENGTH = 253
NEW_DIR = 'storage/docx_downloads'
AI_NEW_DIR = 'storage/AI_docx_downloads'

def download_from_DB(cursor, table_name, file_column, dir, file_divider):
    # Select when last data was created_at
    cursor.execute(f"SELECT created_at FROM {table_name} ORDER BY created_at DESC LIMIT 1")
    last_created_at = cursor.fetchone()[0]
    print(last_created_at)

    # if datetime.strptime(last_created_at, "%Y-%m-%d %H:%M:%S").hour != datetime.now().hour or datetime.strptime(last_created_at, "%Y-%m-%d %H:%M:%S").minute != datetime.now().minute:
    #     sys.exit()
    
    os.makedirs(dir, exist_ok=True)

    cursor.execute(f"SELECT act_id, title, {file_column} FROM {table_name} WHERE created_at = ?", (last_created_at,))
    rows = cursor.fetchall()

    title_counts = Counter()

    for row in rows:
        id, title, file_column = row

        # Validate file name
        sanitized_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
        sanitized_title = re.sub(r'[^\w\s-]', '', sanitized_title.lower())
        sanitized_title = re.sub(r'[-\s]+', '_', sanitized_title).strip('-_')

        # Increment the counter for this title
        title_counts[sanitized_title] += 1

        # Handle duplicates by appending the counter
        if title_counts[sanitized_title] > 1:
            sanitized_title = f"{sanitized_title}_{title_counts[sanitized_title]}"
        output_path = os.path.join(dir, f"{sanitized_title}")

        # Ensure that path length does not exceed the limit
        reserved_length = len(dir) + len(".docx") + 3 # Reserve space for separators
        if len(output_path) > MAX_PATH_LENGTH:
            valid_title_length = MAX_PATH_LENGTH - reserved_length
            truncated_title = sanitized_title[:valid_title_length]
            sanitized_title = f"{truncated_title}_{title_counts[sanitized_title]}"
            output_path = os.path.join(dir, f"{sanitized_title}")
        output_path = f"{output_path}_{file_divider}_{id}.docx"

        try:
            # Save file
            with open(output_path, 'wb') as file:
                file.write(file_column)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def main():
    connection = get_connection()
    cursor = connection.cursor()
    table_name = "Acts"

    download_from_DB(cursor, table_name, "document", NEW_DIR, "aktas")
    download_from_DB(cursor, table_name, "ollamaAnalysedDocument", AI_NEW_DIR, "ataskaita")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()