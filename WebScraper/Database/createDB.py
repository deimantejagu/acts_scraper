import sqlite3

def connect_to_DB():
    connection = sqlite3.connect("ActsData.db")
    print(connection.total_changes)

    return connection

def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Acts (
        act_id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        date TEXT,
        title TEXT,
        document BLOB
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS RelatedDocuments (
        doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        act_id INTEGER,
        FOREIGN KEY (act_id) REFERENCES Acts (act_id)
    )
    """)
    connection.commit()
    cursor.close()

def insert_into_Acts(connection):
    cursor = connection.cursor()

    file_path = '/Users/deimantejagucanskyte/Documents/work/scraper/acts-scraper/downloads/66de74cc5d_MSO2010_DOCX.docx'
    with open(file_path, 'rb') as file:
        blob_data = file.read()

    # Prepare the SQL INSERT statement with placeholders
    sql_insert = """
        INSERT INTO Acts (url, date, title, document)
        VALUES (?, ?, ?, ?)
    """

    # Execute the INSERT statement with actual data
    cursor.execute(sql_insert, ('https://e-seimas.lrs.lt/portal/legalAct/lt/TAP/8005d610b0b511efa81e811ff75635ec?positionInSearchResults=39&searchModelUUID=31cfffaf-e21d-4042-b6d6-38f86e2a8661', '2024-12-04', 'Dėl meilės negavimo', blob_data))
    connection.commit()
    cursor.close()

def insert_into_RelatedDocuments(connection):
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO RelatedDocuments (url, act_id) VALUES (?, ?)
    """, (
        'https://e-seimas.lrs.lt/portal/legalAct/lt/TAK/391ca611b0b611efa81e811ff75635ec?positionInSearchResults=38&searchModelUUID=31cfffaf-e21d-4042-b6d6-38f86e2a8661',
        1  
    ))
    cursor.execute("""
    INSERT INTO RelatedDocuments (url, act_id) VALUES (?, ?)
    """, (
        'https://e-seimas.lrs.lt/portal/legalAct/lt/TAK/391ca611b0b611efa81e811ff75635ec?positionInSearchResults=38&searchModelUUID=31cfffaf-e21d-4042-b6d6-38f86e2a8661',
        1  
    ))

    connection.commit()
    cursor.close()

def main():
    connection = connect_to_DB()
    create_tables(connection)
    insert_into_Acts(connection)
    insert_into_RelatedDocuments(connection)

if __name__ == "__main__":
    main()