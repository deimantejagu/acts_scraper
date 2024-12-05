import json
from urllib.parse import urlparse
from CreateDbConnection import get_connection

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

def load_json():
    with open('output.json', 'r') as file:
        datas = json.load(file)

    return datas

def insert_into_Acts(connection, datas, cursor):
    for data in datas:
        file_url = urlparse(data['file_urls'][0]).path
        file_name = file_url.split('/')[-4] + '.docx'
        file_path = f'/mnt/c/Users/Testinis/Desktop/acts-scraper/downloads/{file_name}'
        with open(file_path, 'rb') as file:
            blob_file = file.read()

        cursor.execute(create_Acts_placeholder(), 
        (
            data['url'], 
            data['date'], 
            data['title'], 
            blob_file
        ))
        connection.commit()

def main():
    connection = get_connection()
    cursor = connection.cursor()

    datas = load_json()
    insert_into_Acts(connection, datas, cursor)
    # print(f"{datas[0]['url']}, {datas[0]['date']}, {datas[0]['title']}, {datas[0]['file_urls']}")
    cursor.close()

if __name__ == "__main__":
    main()