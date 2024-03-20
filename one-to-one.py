import csv
import getpass
import sys
import os
import base64
import re
from email.utils import formataddr
from email.header import Header
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from templates.variable_mappings import variable_column_mapping
from tkinter import *
from tkhtmlview import HTMLLabel
from tkinterweb import HtmlFrame 


# Help and number of argument passed checker
if len(sys.argv) < 3:
    print("USAGE: python3 one-to-one.py <template_file> <csv_file> (OPTIONAL)<variables_with_same_value_for_all_mails>")
    print("python3 one-to-one.py selections/onboarding onboarding.csv")
    print("python3 one-to-one.py selections/onboarding onboarding.csv number_of_applicants='250+'")
    sys.exit(1)
    
# If modifying SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


root = Tk()
ok = False # variable to check whether mail content is alright

def command_ok(): # command for ok button UI
    global ok
    ok = True
    root.quit()

def command_cancel(): # command for cancel button UI
    global ok
    root.quit()
    ok = False

# Various files being used
template_file = "./templates/" + sys.argv[1]
csv_file = "./csv/" + sys.argv[2]
signature_file = "./templates/signature"

# Getting subject and mail body
lines = []
with open(template_file, "r") as file:
    subject_template = file.readline().strip()
    lines = file.readlines()[1:]  # Slice the list starting from index 2 (line number 3)
email_body_template = "".join(lines)
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

def main(subject_template, email_body_template, signature):
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
    
    # Getting extra static variables(those which are same for all mails) if required by the template - from arguments
    if len(sys.argv) > 2:
        variables = {}
        for arg in sys.argv[3:]:
            variable, value = arg.split("=")
            variables[variable] = value.strip()
            
        email_body_template = fill_variables(email_body_template, variables)
        subject_template = fill_variables(subject_template, variables)

    with open(csv_file, newline="") as file:
        reader = csv.DictReader(file)
        num = False # variable to index the first mail

        for row in reader:
            # Getting unique variables values - from the CSV file
            required_columns = set([column for variables in variable_column_mapping.values() for column in variables if column in row])

            variables = {}
            for variable, columns in variable_column_mapping.items():
                for column in columns:
                    if column in required_columns:
                        variables[variable] = row.get(column, "").strip()
                        break
                    
            email = variables['email'].strip()
            if not validate_email(email):
                print(f'Invalid mail provided: {email}')
                continue

            email_body = fill_variables(email_body_template, variables)
            subject = fill_variables(subject_template, variables)
            
            sender = "admin@kossiitkgp.org"
            email_content = email_body + signature
            message = create_message(sender, email, subject, email_content)
            
            if num==False: # only view the first mail when executing
                myhtmlframe = HtmlFrame(root,messages_enabled = False)
                myhtmlframe.load_html(email_content) 
                myhtmlframe.grid(row=0,column=0) 
                button_ok = Button(root,text = 'OK' , command=command_ok, background='#45f775')
                button_ok.grid(row = 1,column=0)
                l = Label(root,text='')
                l.grid(row=2,column=0)
                button_cancel = Button(root, text = 'Cancel',command=command_cancel,background='#c73243')
                button_cancel.grid(row=3,column=0)
                root.mainloop()
                num = True
            
            if ok==False: # cancel the execution if mail content is not right
                break

            send_message(service, "me", {"raw": message})
            print(f'Message sent to: {email}')

    print("Script execution completed.")

if __name__ == "__main__":
    main(subject_template, email_body_template, signature)
