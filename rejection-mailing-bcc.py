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

if len(sys.argv) < 2:
    print("Usage: python script.py <csv_file>")
    sys.exit(1)

csv_file = sys.argv[1]

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
            print(f"BCC TO: {email}")
            emails.append(email)  # Add the email to the BCC list

            emailContents = f"""Hello,<br><br>
            
We are afraid to be writing with some bad news. Unfortunately, we would not be able to extend your selection application to Kharagpur Open Source Society.<br><br>

The selections this year have by far been the toughest we have experienced, even after stretching the interview and judging process for many days.<br><br>

Your caliber was outstanding to the point that we found ourselves, unfortunately, having to turn down even the most highly qualified applicants with fantastic submissions. We tried our best to increase the amount of intake this year, but we don't have the bandwidth to be able to take on more of you and still ensure you all have a great experience.<br><br>

Even if you’re not a part of KOSS, we still hope to work together to spread Open Source awareness in Kharagpur because it takes a whole village to do that. We’re rooting for you and looking forward to seeing what you do next.<br><br>

Here are some resources below which you may find useful:
    
    <ol>
    <li><a href="https://rejected.us/">We've All Faced Rejection</a></li>
    <li><a href="https://github.com/deepanshu1422/List-Of-Open-Source-Internships-Programs">List of Open Source Internship Programs</a></li>
    <li><a href="https://slack.metakgp.org/">Invitation to MetaKGP Slack</a></li>
    <li><a href="https://1x.engineer/">1x Engineer</a></li>
    <li><a href="https://github.com/codecrafters-io/build-your-own-x">Build Your Own X</a></li>
    </ol>
            
--<br>
Regards,<br>
Kharagpur Open Source Society<br>
IIT Kharagpur<br>
<a href="https://kossiitkgp.org/">Website</a> | <a href="https://github.com/kossiitkgp">GitHub</a> | <a href="https://facebook.com/kossiitkgp">Facebook</a> | <a href="https://twitter.com/kossiitkgp">Twitter</a>"""

        # Create a single message with BCC recipients
        sender = "admin@kossiitkgp.org"  # Replace with your email address
        subject = "Update on KOSS Selections"
        bcc = ", ".join(emails)  # Join the emails with commas for BCC
        message = create_message(sender, "", bcc, subject, emailContents)  # Set "to" as an empty string

        send_message(service, "me", {"raw": message})
        print(f"Email sent to {len(emails)} recipients as BCC.")

    print("Script execution completed.")

if __name__ == "__main__":
    main()
