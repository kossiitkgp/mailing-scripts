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
    print("ERROR: python3 bcc.py <name of the variable referring to the 'compaitible' email body stored in emailContents.py - (rejection/interview supproted currently>")
    print("Run: python3 bcc.py <interview/rejection> to know about their usecases")
    sys.exit(1)
    
mail_body = sys.argv[1]

if mail_body == "rejection":
    if len(sys.argv) < 3:
        print("Usage: python3 bcc.py rejection <csv_file>")
        print("Example: python3 bcc.py rejection csv/rejected.csv")
        sys.exit(1)
elif mail_body == "interview":
    if len(sys.argv) < 4:
        print("Usage: python3 bcc.py interview <csv_file> <slot_details (Day, Date, Timing)>")
        print("Example: python3 bcc.py interview csv/d1s2.csv 'Thursday, 12 May, 9:00PM - 10:00PM'")
        sys.exit(1)
    
csv_file = sys.argv[2]

def create_message(sender, to, bcc, subject, message):
    formatted_sender = formataddr((str(Header('KOSS IIT Kharagpur', 'utf-8')), sender))
    message = (
        f"From: {formatted_sender}\n"
        f"To: {to}\n"
        f"Bcc: {bcc}\n"
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

        emails = []  # List to store the email addresses for BCC

        for row in reader:
            email = row[1]
            emails.append(email)  # Add the email to the BCC list
            print(f"BCC TO: {email}")
            
        if mail_body == "rejection":
            emailBody = getattr(emailContents, "rejection")
            subject = "Update on KOSS Selections"
        elif mail_body == "interview":
            emailBody = emailContents.getInterviewMail(sys.argv[3])
            subject = "KOSS Selection Interview"
            
        # Create a single message with BCC recipients
        sender = "admin@kossiitkgp.org"  # Replace with your email address
        bcc = ", ".join(emails)  # Join the emails with commas for BCC
        emailContent = emailBody + emailContents.signature
        message = create_message(sender, "", bcc, subject, emailContent)  # Set "to" as an empty string
        send_message(service, "me", {"raw": message})
        print(f"Email sent to {len(emails)} recipients as BCC.")

    print("Script execution completed.")

if __name__ == "__main__":
    main()
