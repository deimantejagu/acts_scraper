import os
import re
import unicodedata
from collections import Counter
from database.create_db_connection import get_connection

MAX_PATH_LENGTH = 253
NEW_DIR = 'storage/docx_downloads'

def download_acts_from_DB(cursor, table_name):
    os.makedirs(NEW_DIR, exist_ok=True)

    # Select when last data was created_at
    cursor.execute(f"SELECT created_at FROM {table_name} ORDER BY created_at DESC LIMIT 1")
    last_created_at = cursor.fetchone()[0]
    print(last_created_at)

    cursor.execute(f"SELECT act_id, title, document FROM {table_name} WHERE created_at = ?", (last_created_at,))    
    rows = cursor.fetchall()

    title_counts = Counter()

    for row in rows:
        id, title, document = row

        # Validate file name
        sanitized_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
        sanitized_title = re.sub(r'[^\w\s-]', '', sanitized_title.lower())
        sanitized_title = re.sub(r'[-\s]+', '_', sanitized_title).strip('-_')

        # Increment the counter for this title
        title_counts[sanitized_title] += 1

        # Handle duplicates by appending the counter
        if title_counts[sanitized_title] > 1:
            sanitized_title = f"{sanitized_title}_{title_counts[sanitized_title]}"
        output_path = os.path.join(NEW_DIR, f"{sanitized_title}")

        # Ensure that path length does not exceed the limit
        reserved_length = len(NEW_DIR) + len(".docx") + 3 # Reserve space for separators
        if len(output_path) > MAX_PATH_LENGTH:
            valid_title_length = MAX_PATH_LENGTH - reserved_length
            truncated_title = sanitized_title[:valid_title_length]
            sanitized_title = f"{truncated_title}_{title_counts[sanitized_title]}"
            output_path = os.path.join(NEW_DIR, f"{sanitized_title}")
        output_path = f"{output_path}_{id}.docx"

        try:
            # Save file
            with open(output_path, 'wb') as file:
                file.write(document)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def main():
    connection = get_connection()
    cursor = connection.cursor()
    table_name = "Acts"

    download_acts_from_DB(cursor, table_name)

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()