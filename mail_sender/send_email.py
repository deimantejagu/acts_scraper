import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import zipfile
import os
from datetime import datetime
from pathlib import Path
from .prepare_email_data import main as prepare_email

MAX_EMAIL_SIZE = 25
DIRECTORY_PATH = Path("storage/docx_downloads").resolve()

def get_docx_files_and_sizes():
    files = []
    all_files_size = 0
    for filename in os.listdir(DIRECTORY_PATH):
        file_path = os.path.join(DIRECTORY_PATH, filename)
        file_size = os.path.getsize(file_path)
        file_size /= (1024 * 1024)
        all_files_size += file_size
        files.append((filename, file_size))
    print(f"All files: {len(files)}")
    print(f"All files size: {all_files_size}")

    return files

def split_files_zip(files):
    zip_files = []
    current_size = 0
    for filename, file_size in files:
        if current_size + file_size < MAX_EMAIL_SIZE:
            current_size += file_size
            zip_files.append(filename)
        else:
            print("--------")
            print(f"Last file size + current size: {current_size + file_size}")
            print(f"Current size: {current_size}") 
            print(f"All files in zip: {len(zip_files)}")
            break

    return zip_files

def press_files_into_zip(zip_name, file_paths):
    zip_file_path = f"{zip_name}.zip"
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            full_path = DIRECTORY_PATH / file_path
            zipf.write(full_path, arcname=full_path.name)

    zip_file_size = os.path.getsize(zip_file_path) / (1024 * 1024)
    print("--------")
    print(f"ZIP file size: {zip_file_size:.2f}")

    return zip_file_path

def send_email():
    # Set up SMTP server
    server = smtplib.SMTP('localhost', 1025)  # Mailpit server running on localhost

    # Create email
    msg = MIMEMultipart()
    msg['Subject'] = 'Test Email With Attachment'
    msg['From'] = 'praktika985@gmail.com'
    msg['To'] = 'praktika985@gmail.com'

    # Attach email body
    msg.attach(MIMEText('This is a test email with a zipped attachment.', 'plain'))

    # Zip directory
    folder_name = datetime.today().strftime("%Y-%m-%d")
    files = get_docx_files_and_sizes()
    zip_files = split_files_zip(files)
    zip_file_path = press_files_into_zip(folder_name, zip_files)

    # Attach zip file
    with open(zip_file_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={folder_name}')

    msg.attach(part)

    # Send email
    server.sendmail('praktika985@gmail.com', ['praktika985@gmail.com'], msg.as_string())
    server.quit()

    # Clean up ZIP file after sending
    os.remove(zip_file_path)

def main():
    prepare_email()
    send_email()

if __name__ == "__main__":
    main()