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

# If modifying SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

if len(sys.argv) < 3:
    print("Usage: python script.py <csv_file> <day, date> (for the deadline)")
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

            emailContents = f"""Hello {name},<br><br>

Congratulations! You have made it to the second round of selections. You can find your task in the GitHub link below.<br><br>

<a href="{taskURL}">{taskURL}</a><br><br>

<i>The task may seem daunting at first because it is daunting given the time frame. However, we are more concerned with your approach rather than the final delivery</i>.<br><br>

We expect you to upload your code/presentation to a GitHub repository and share the link with us as a reply to this email by <b>{deadline}, at 1 AM</b>.<br><br>

Round - 2 Interview is scheduled for <b>{deadline}</b> tentatively. The exact timings will be mailed later.<br><br>

In case of any issues with the task, or if you want to change your task, please drop us a mail or contact any of us.<br><br>

Happy Learning!<br>
--<br>
Regards,<br>
Kharagpur Open Source Society<br>
IIT Kharagpur<br>
<a href="https://kossiitkgp.org/">Website</a> | <a href="https://github.com/kossiitkgp">GitHub</a> | <a href="https://facebook.com/kossiitkgp">Facebook</a> | <a href="https://twitter.com/kossiitkgp">Twitter</a>"""

            sender = "admin@kossiitkgp.org"  # Replace with your email address
            subject = "KOSS Selections - Task"
            message = create_message(sender, email, subject, emailContents)
            send_message(service, "me", {"raw": message})
            print(f'Message sent. E-mail ID: {email}')

    print("Script execution completed.")

if __name__ == "__main__":
    main()
