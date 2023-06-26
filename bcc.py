import csv
import getpass
import sys
import os
import re
import base64
from email.utils import formataddr
from email.header import Header
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Help and number of argument passed checker
if len(sys.argv) < 3:
    print("USAGE: python3 bcc.py <template_file> <csv_file> (OPTIONAL)<variables_with_same_value_for_all_mails>")
    print("python3 bcc.py selections/rejection rejected.csv")
    print("python3 bcc.py selections/rejection rejected.csv number_of_applicants='250+'")
    sys.exit(1)
    
# If modifying SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Various files being used
template_file = "./templates/" + sys.argv[1]
csv_file = "./csv/" + sys.argv[2]
signature_file = "./templates/signature"

# Getting subject and mail body
lines = []
with open(template_file, "r") as file:
    subject = file.readline().strip()
    lines = file.readlines()[1:]  # Slice the list starting from index 2 (line number 3)
email_body = "".join(lines)
# Getting signature
with open(signature_file) as file:
    signature = file.read()

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

def fill_variables(content, variables):
    for variable, value in variables.items():
        placeholder = "{" + variable + "}"
        content = content.replace(placeholder, value)

    return content 

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False

def main(subject, email_body, signature):
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

    # Getting extra variables if required by the template
    if len(sys.argv) > 3:
        variables = {}
        for arg in sys.argv[3:]:
            variable, value = arg.split("=")
            variables[variable] = value
            
        email_body = fill_variables(email_body, variables)
        subject = fill_variables(subject, variables)

    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row

        emails = []  # List to store the email addresses for BCC

        for row in reader:
            email = row[1]
            if not validate_email(email):
                print(f'Invalid mail provided: {email}')
                continue
            
            emails.append(email)  # Add the email to the BCC list
            print(f"BCC TO: {email}")
            
        # Create a single message with BCC recipients
        sender = "admin@kossiitkgp.org"  # Replace with your email address
        bcc = ", ".join(emails)  # Join the emails with commas for BCC
        email_content = email_body + signature
        message = create_message(sender, "", bcc, subject, email_content)  # Set "to" as an empty string
        send_message(service, "me", {"raw": message})
        print(f"Email sent to {len(emails)} recipients as BCC.")

    print("Script execution completed.")

if __name__ == "__main__":
    main(subject, email_body, signature)
