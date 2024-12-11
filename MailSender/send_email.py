import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import zipfile
import os
import io

MAX_EMAIL_SIZE = 25

def zip_directory(directory_path):
    zip_buffer = io.BytesIO()
    files_sizes = []
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                file_size = os.stat(file_path).st_size
                files_sizes.append(file_size)
                zipf.write(file_path, arcname=os.path.relpath(file_path, directory_path))
    zip_buffer.seek(0)

    zip_size_mb = len(zip_buffer.getvalue()) / (1024 * 1024)
    print(f"Zip file size: {zip_size_mb:.2f} MB")

    return zip_buffer, files_sizes

def split_files_zip(files_sizes):
    current_size = 0
    for size in files_sizes:
        size_in_mb = size / (1024 * 1024)
        if current_size + size_in_mb < MAX_EMAIL_SIZE:
            current_size += size_in_mb
        else:
            print(current_size) 
            current_size = 0
    pass

def send_email():
    # Set up the SMTP server
    server = smtplib.SMTP('localhost', 1025)  # Mailpit server running on localhost

    # Create the email
    msg = MIMEMultipart()
    msg['Subject'] = 'Test Email With Attachment'
    msg['From'] = 'praktika985@gmail.com'
    msg['To'] = 'praktika985@gmail.com'

    # Attach the email body
    msg.attach(MIMEText('This is a test email with a zipped attachment.', 'plain'))

    # Zip the directory
    directory_path = 'docx_downloads'
    zip_file, files_sizes = zip_directory(directory_path)

    split_files_zip(files_sizes)

    # Attach the zip file
    filename = 'output.zip'
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(zip_file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={filename}')

    msg.attach(part)

    # Send the email
    server.sendmail('praktika985@gmail.com', ['praktika985@gmail.com'], msg.as_string())
    server.quit()

def main():
    send_email()

if __name__ == "__main__":
    main()