import os
MAX_ATTEMPTS = 3
PASSWORD = ""
if os.path.exists("password.txt") and os.path.getsize("password.txt") > 0:
    with open("password.txt", "r") as pass_file:
        PASSWORD = pass_file.readline().strip()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDEREMAIL = "mohammedebrahem99999@gmail.com"
Email_REGEX = r"^[a-zA-Z0-9.]+@gmail\.com$"
PHONE_REGEX = r"^01[0125]\d{8}$"
ISBN_PATTERN = r"^[\d-]{10,17}$"
URL_REGEX = r"^https?://[^\s/$.?#].[^\s]*/.+\.(PDF|DOCX|DOC|PPTX|TXT|EPUB|RTF)(\?[^\s]*)?$"
ALLOWED_FILE_FORMAT = ['PDF', 'DOCX', 'DOC', 'PPTX', 'TXT', 'EPUB', 'RTF']