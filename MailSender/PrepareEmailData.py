from WebScraper.Database.CreateDbConnection import get_connection
import os
import re
import unicodedata
from collections import Counter

MAX_PATH_LENGTH = 255

def download_acts_from_DB(cursor, table_name):
    new_dir = 'docx_downloads'
    os.makedirs(new_dir, exist_ok=True)

    cursor.execute(f"SELECT title, document FROM {table_name}")
    rows = cursor.fetchall()
    print(f"Number of rows fetched: {len(rows)}")

    title_counts = Counter()

    for row in rows:
        title, document = row

        # Validate file name
        sanitized_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
        sanitized_title = re.sub(r'[^\w\s-]', '', sanitized_title.lower())
        sanitized_title = re.sub(r'[-\s]+', '-', sanitized_title).strip('-_')

        # Increment the counter for this title
        title_counts[sanitized_title] += 1

        # Handle duplicates by appending the counter
        if title_counts[sanitized_title] > 1:
            sanitized_title = f"{sanitized_title}_{title_counts[sanitized_title]}"
        output_path = os.path.join(new_dir, f"{sanitized_title}.docx")

        # Ensure the path length does not exceed the limit
        reserved_length = len(new_dir) + len(".docx") + 3 # Reserve space for separators
        if len(output_path) > MAX_PATH_LENGTH:
            valid_title_length = MAX_PATH_LENGTH - reserved_length
            truncated_title = sanitized_title[:valid_title_length]
            sanitized_title = f"{truncated_title}_{title_counts[sanitized_title]}"
            output_path = os.path.join(new_dir, f"{sanitized_title}.docx")

        try:
            # Save the file
            with open(output_path, 'wb') as file:
                file.write(document)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    saved_files = os.listdir(new_dir)
    # Compare saved files with rows
    print(f"Number of files saved: {len(saved_files)}")
    if len(rows) != len(saved_files):
        print(f"Mismatch: {len(rows) - len(saved_files)} files were not saved!")

def main():
    connection = get_connection()
    cursor = connection.cursor()
    table_name = "Acts"

    download_acts_from_DB(cursor, table_name)

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()