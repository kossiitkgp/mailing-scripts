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

# Help and number of argument passed checker
if len(sys.argv) < 3:
    print("USAGE: python3 one-to-one.py <template_file> <csv_file> (OPTIONAL)<other_variables>")
    print("python3 one-to-one.py selections/onboarding onboarding.csv")
    print("python3 one-to-one.py selections/onboarding onboarding.csv number_of_applicants='250+'")
    sys.exit(1)
    
# If modifying SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Various files being used
template_file = "./templates/" + sys.argv[1]
csv_file = "./csv/" + sys.argv[2]
signature_file = "./templates/signature"

# Getting subject
with open(template_file, "r") as file:
    subject = file.readline().strip()
# Getting mail body
lines = []
with open(template_file, "r") as file:
    lines = file.readlines()[2:]  # Slice the list starting from index 2 (line number 3)
email_body = "".join(lines)
# Getting signature
with open(signature_file) as file:
    signature = file.read()

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

        for row in reader:
            email = row[1]
            name = row[2]

            sender = "admin@kossiitkgp.org"
            if mail_body == "task":
                taskURL = row[7]
                deadline = sys.argv[3]
                emailBody = emailContents.getTaskMail(name, taskURL, deadline)
            elif mail_body == "onboarding":
                number_of_participants = sys.argv[3]
                emailBody = emailContents.getOnboardingMail(name, number_of_participants)
            email_content = email_body + signature
            message = create_message(sender, email, subject, email_content)
            send_message(service, "me", {"raw": message})
            print(f'Message sent to: {email}')

    print("Script execution completed.")

if __name__ == "__main__":
    main(subject, email_body, signature)
