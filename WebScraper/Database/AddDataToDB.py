from CreateDbConnection import get_connection

connection = get_connection()

def create_Acts_placeholder():
    sql_insert_Act = """
        INSERT INTO Acts (url, date, title, document)
        VALUES (?, ?, ?, ?)
    """

    return sql_insert_Act

def create_RelatedDocuments_placeholder():
    sql_insert_RelatedDocuments = """
        INSERT INTO RelatedDocuments (url, date, title, document)
        VALUES (?, ?, ?, ?)
    """

    return sql_insert_RelatedDocuments

def insert_into_Acts(connection):
    cursor = connection.cursor()

    # Test data
    file_path = '/mnt/c/Users/Testinis/Desktop/acts-scraper/downloads/0cf5a27edd_MSO2010_DOCX.docx'
    with open(file_path, 'rb') as file:
        blob_data = file.read()

    cursor.execute(create_Acts_placeholder(), 
    (
        'https://e-seimas.lrs.lt/portal/legalAct/lt/TAP/8005d610b0b511efa81e811ff75635ec?positionInSearchResults=39&searchModelUUID=31cfffaf-e21d-4042-b6d6-38f86e2a8661', 
        '2024-12-04', 'Dėl meilės negavimo', 
        blob_data
    ))
    connection.commit()
    cursor.close()

def insert_into_RelatedDocuments(connection):
    cursor = connection.cursor()

    cursor.execute(create_RelatedDocuments_placeholder(), 
    (
        'https://e-seimas.lrs.lt/portal/legalAct/lt/TAK/391ca611b0b611efa81e811ff75635ec?positionInSearchResults=38&searchModelUUID=31cfffaf-e21d-4042-b6d6-38f86e2a8661',
        1 
    ))

    connection.commit()
    cursor.close()

def main():
    insert_into_Acts(connection)
    insert_into_RelatedDocuments(connection)

if __name__ == "__main__":
    main()