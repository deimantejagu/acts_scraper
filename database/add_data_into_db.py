import json
from urllib.parse import urlparse
from pathlib import Path
from database.create_db_connection import get_connection

JSON_DATA = 'storage/output.json'
TABLE_NAME = "Acts"

def create_Acts_placeholder():
    sql_insert_Act = """
        INSERT INTO Acts (created_at, url, date, title, document, ollamaAnalysedDocument)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    return sql_insert_Act

def create_RelatedDocuments_placeholder():
    sql_insert_RelatedDocuments = """
        INSERT INTO RelatedDocuments (url, act_id)
        VALUES (?, ?)
    """

    return sql_insert_RelatedDocuments

def load_json():
    with open(JSON_DATA, 'r') as file:
        datas = json.load(file)

    return datas

def get_new_datas(cursor, datas):
    new_datas = []
    cursor.execute(f"SELECT title FROM {TABLE_NAME}") 
    titles = cursor.fetchall()
    titles = [title[0] for title in titles]
    for data in datas:
        if data['title'] not in titles:
            new_datas.append(data)

    return new_datas

def insert_into_RelatedDocuments(connection, data, cursor, act_id):
    for related_document in data['related_documents']:
        cursor.execute(create_RelatedDocuments_placeholder(), 
        (
            related_document,
            act_id 
        ))
        connection.commit()

def insert_into_Acts(connection, datas, cursor):
    base_dir = Path(__file__).parent.resolve().parent
    for data in datas:
        file_url = urlparse(data['file_urls'][0]).path
        file_name = file_url.split('/')[-4] + '.docx'
        file_path = f'{base_dir}/storage/downloads/{file_name}'

        with open(file_path, 'rb') as file:
            blob_file = file.read()

        cursor.execute(create_Acts_placeholder(), 
        (
            data['created_at'],
            data['url'], 
            data['date'], 
            data['title'], 
            blob_file,
            None
        ))
        connection.commit()

        if data['related_documents']:
            act_id = cursor.lastrowid
            insert_into_RelatedDocuments(connection, data, cursor, act_id)

def main():
    connection = get_connection()
    cursor = connection.cursor()

    datas = load_json()
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    count = cursor.fetchone()[0]
    if count == 0:
        insert_into_Acts(connection, datas, cursor)
    else:
        new_datas = get_new_datas(cursor, datas)
        insert_into_Acts(connection, new_datas, cursor)

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()