import time

from ollama import ChatResponse, Client
from docx import Document

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])

    return text

def main():
    client = Client(host='http://localhost:11434')
    act_path = './2a0b9661cd8d11efb81fa0211f8edf4d.docx'

    try:
        act_content = extract_text_from_docx(act_path)
        prompt = f"""Išanalizuokite toliau pateiktą dokumentą, ar jame yra su korupcija susijusių klausimų. 
            Nustatykite galimas spragas ar korupciją liudijančius modelius, pvz. kyšininkavimą, nepotizmą, 
            bičiuliškumą ar piktnaudžiavimą valdžia. Pateikite išsamią turinio analizę, daugiausia dėmesio skirdami 
            konkretiems skirsniams, kurie  rodo korupcijos riziką.

            Documento turinys:
        {act_content}"""

        start = time.time()

        response: ChatResponse = client.chat(model='llama3.2', messages=[ {'role': 'user', 'content': prompt} ])
        print(response['message']['content'])

        elapsed_time = time.time() - start
        print(f"Time elapsed: {int(elapsed_time // 60)} minutes {int(elapsed_time % 60)} seconds")
    except Exception as e :
        print(f"Error: {e}")

if __name__ == "__main__":
    main()