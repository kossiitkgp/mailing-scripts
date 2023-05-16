import csv
import getpass
import sys
import os
import base64
import emailContents
from email.utils import formataddr
from email.header import Header
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

if len(sys.argv) < 2:
    print("ERROR: python3 bcc.py <name of the variable referring to the 'compaitible' email body stored in emailContents.py - (task/onboarding supproted currently>")
    print("Run: python3 bcc.py <task/onboarding> to know about their usecases")
    sys.exit(1)
    
mail_body = sys.argv[1]

if mail_body == "task":
    if len(sys.argv) < 3:
        print("Usage: python3 bcc.py task <csv_file> <deadline>")
        print("Example: python3 bcc.py task csv/day1.csv 'Tuesday, 23 May 2023'")
        sys.exit(1)
elif mail_body == "onboarding":
    if len(sys.argv) < 4:
        print("Usage: python3 bcc.py onboarding <csv_file> <slot_details (Day, Date, Timing)>")
        print("Example: python3 bcc.py onboarding csv/day1.csv '250+'")
        sys.exit(1)
else:
    print("ERROR: python3 bcc.py <name of the variable referring to the 'compaitible' email body stored in emailContents.py - (task/onboarding supproted currently>")
    print("Run: python3 bcc.py <task/onboarding> to know about their usecases")
    sys.exit(1)
    
csv_file = sys.argv[2]

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
            if mail_body == "task":
                deadline = sys.argv[3]
                emailBody = emailContents.getTaskMail(name, taskURL, deadline)
                subject = "KOSS Selections - Task"
            elif mail_body == "onboarding":
                number_of_participants = sys.argv[3]
                emailBody = emailContents.getOnboardingMail(name, number_of_participants)
                subject = f"Congratulations {name}! Welcome to Kharagpur Open Source Society!"
            emailContent = emailBody + emailContents.signature
            message = create_message(sender, email, subject, emailContent)
            send_message(service, "me", {"raw": message})
            print(f'Message sent. E-mail ID: {email}')

    print("Script execution completed.")

if __name__ == "__main__":
    main()
