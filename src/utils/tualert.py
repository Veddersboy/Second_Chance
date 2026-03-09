import requests
import imaplib
import email
from datetime import datetime

SERVER_URL = 'https://web-production-277c.up.railway.app'
APP_SECRET = '45VMfleRenMZK7iDB7iRWCdgohA8So0O'

def fetch_creds():
    # Fetch credentials from server
    response = requests.get(
        f'{SERVER_URL}/credentials',
        headers={'Authorization': f'Bearer {APP_SECRET}'}
    )
    response.raise_for_status()
    return response.json()

def get_latest_alert():
    # Grab Credentials from railway server
    creds = fetch_creds()

    # Initialize mail handler
    mail_handler = imaplib.IMAP4_SSL('imap.gmail.com')
    mail_handler.login(creds['email'], creds['password'])
    mail_handler.select('inbox', readonly=True)

    # Grab most recent tualert
    status, messages = mail_handler.search(None, "FROM 'aidan.ross0001@temple.edu'")
    message_ids = messages[0].split()
    status, message_data = mail_handler.fetch(message_ids[-1], '(RFC822)')
    raw_email = message_data[0][1]
    msg = email.message_from_bytes(raw_email)

    # Get send date
    date = email.utils.parsedate_to_datetime(msg['Date']).strftime("%Y-%m-%d %H:%M")

    # Get Subject
    subject = msg["Subject"]

    # Extract the alert from the message body
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()
        
    for line in body.strip().splitlines():
        if line.startswith("TUalertEMER:"):
            alert = line

    # Return Formatted Alert
    return f"{date}\n{subject}\n{alert}"