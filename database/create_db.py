from database.create_db_connection import get_connection

def create_tables():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Acts (
        act_id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at DATETIME,
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

def main():
    create_tables()

if __name__ == "__main__":
    main()