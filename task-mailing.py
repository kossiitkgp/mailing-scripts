import csv
import getpass
import sys
import os
import base64
from email.utils import formataddr
from email.header import Header
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from emailContents import signature
from emailContents import getTaskMail

# If modifying SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

if len(sys.argv) < 3:
    print("Usage: python3 task_mailing.py <csv_file> <day, date> (for the deadline)")
    sys.exit(1)

csv_file = sys.argv[1]
deadline = sys.argv[2]

def create_message(sender, to, subject, message):
    formatted_sender = formataddr((str(Header('KOSS IIT Kharagpur', 'utf-8')), sender))
    message = (
        f"From: {formatted_sender}\n"
        f"To: {to}\n"
        f"Subject: {subject}\n"
        f"MIME-Version: 1.0\n"
        f"Content-Type: text/html; charset=utf-8\n"
        f"\n"
        f"{message}"
    )
    return base64.urlsafe_b64encode(message.encode("utf-8")).decode("utf-8")

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
    except Exception as e:
        print(f"An error occurred while sending the message: {e}")

def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row

        for row in reader:
            email = row[1]
            name = row[2]
            taskURL = row[7]

            sender = "admin@kossiitkgp.org"
            subject = "KOSS Selections - Task"
            emailBody = getTaskMail(name, taskURL, deadline)
            emailContent = emailBody + signature
            message = create_message(sender, email, subject, emailContent)
            send_message(service, "me", {"raw": message})
            print(f'Message sent. E-mail ID: {email}')

    print("Script execution completed.")

if __name__ == "__main__":
    main()
