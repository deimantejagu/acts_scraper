import time
import os

from database.create_db_connection import get_connection
from ollama import ChatResponse, chat, Client
from docx import Document
from pathlib import Path

DIRECTORY_PATH = Path("storage/docx_downloads").resolve()
TABLE_NAME = "Acts"
TABLE_COLUMN = "ollamaAnalysedDocument"

def get_docx_files():
    files = []
    for filename in os.listdir(DIRECTORY_PATH):
        files.append(filename)
    print(f"All files: {len(files)}")

    return files

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])

    return text

def main():
    client = Client(host='http://localhost:11434') 
    files = get_docx_files()

    for file_name in files:
        try:
            base_dir = Path(__file__).parent.resolve().parent
            file_path = f'{base_dir}/storage/docx_downloads/{file_name}'

            # Pass file to Ollama
            act_content = extract_text_from_docx(file_path)
            prompt = f"""Išanalizuokite toliau pateiktą dokumentą, ar jame yra su korupcija susijusių klausimų. 
                Nustatykite galimas spragas ar korupciją liudijančius modelius, pvz. kyšininkavimą, nepotizmą, 
                bičiuliškumą ar piktnaudžiavimą valdžia. Pateikite išsamią turinio analizę, daugiausia dėmesio skirdami 
                konkretiems skirsniams, kurie rodo korupcijos riziką.

                Documento turinys:
            {act_content}"""

            # start = time.time()

            # response: ChatResponse = client.chat(model='llama3.2', messages=[ {'role': 'user', 'content': prompt} ])
            # print(response['message']['content'])
            # response_content = response['message']['content']
            output_file = f"{file_name}.docx"

            # Add response into doc
            doc = Document()
            # doc.add_paragraph(response_content)

            # elapsed_time = time.time() - start
            # print(f"Time elapsed: {int(elapsed_time // 60)} minutes {int(elapsed_time % 60)} seconds")

            connection = get_connection()
            cursor = connection.cursor()
            # Retrieve the title from the database
            cursor.execute(f"SELECT title FROM {TABLE_NAME} ORDER BY created_at DESC")
            titles = cursor.fetchall()

            # Insert analysed file into Acts table
            if file_name in titles:
                print(f"file name {file_name}")
                print(f"file name {titles}")
                # cursor.execute(f"INSERT INTO {TABLE_NAME} ({TABLE_COLUMN}) VALUES (?)", (output_file,))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()