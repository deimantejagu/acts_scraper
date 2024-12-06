from WebScraper.Database.CreateDbConnection import get_connection
import os
import re

def download_acts_from_DB(cursor, table_name):
    new_dir = 'docx_downloads'
    os.makedirs(new_dir, exist_ok=True)

    cursor.execute(f"SELECT title, document FROM {table_name}")
    rows = cursor.fetchall()
    for row in rows:
        title, document = row
        sanitized_title = re.sub(r'[<>:"/\\|?*]', '_', title)

        output_path = os.path.join(new_dir, f"{sanitized_title[:100]}.docx")
        with open(output_path, 'wb') as f:
            f.write(document)

def main():
    connection = get_connection()
    cursor = connection.cursor()
    table_name = "Acts"

    download_acts_from_DB(cursor, table_name)

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()