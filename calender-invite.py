import csv
import getpass
import sys
import os
import base64
import re
import mimetypes

from email.utils import formataddr
from email.header import Header
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from templates.variable_mappings import variable_column_mapping

# Help and number of argument passed checker
if len(sys.argv) < 5:
    #DONT USE <LOBBY LINK VARIABLE>
    print("USAGE: python3 calender-invite.py <template_file> <csv_file> <include_meet> <slot_time> (OPTIONAL)<variables_with_same_value_for_all_mails>")
    print('python3 calender-invite.py selections/onboarding onboarding.csv YES slot_time="Tuesday, 3 June 2023, 10:00 PM - 11:00 PM"')
    print("python3 calender-invite.py selections/onboarding onboarding.csv NO slot_time='Tuesday, 2 February 2030, 8:00 AM - 1:00 PM' number_of_applicants='250+'")
    sys.exit(1)
    
# If modifying SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/calendar.events"]

# Various files being used
template_file = "./templates/" + sys.argv[1]
csv_file = "./csv/" + sys.argv[2]
signature_file = "./templates/signature"
hasMeet = (sys.argv[3].lower() == 'yes')

# Getting subject and mail body
lines = []
with open(template_file, "r") as file:
    subject_template = file.readline().strip()
    lines = file.readlines()[1:]  # Slice the list starting from index 2 (line number 3)
email_body_template = "".join(lines)
# Getting signature
with open(signature_file) as file:
    signature = file.read()

def convert_to_RFC3339(input):
    lookUp={'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

    chunks = re.findall(r"[\w']+",input)
    chunks[2] = lookUp[chunks[2]]
    if chunks[6]=='PM':
        chunks[4]=int(chunks[4])+12
    if chunks[9]=='PM':
        chunks[7]=int(chunks[7])+12

    chunks[4]=str(chunks[4]).zfill(2)
    chunks[7]=str(chunks[7]).zfill(2)
    chunks[1]=str(chunks[1]).zfill(2)
    chunks[2]=str(chunks[2]).zfill(2)

    return [f"{chunks[3]}-{chunks[2]}-{chunks[1]}T{chunks[4]}:{chunks[5]}:00",f"{chunks[3]}-{chunks[2]}-{chunks[1]}T{chunks[7]}:{chunks[8]}:00"]

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

def create_event(sender, email_list, subject, message, timeRange, has_meet):
    formatted_sender = formataddr((str(Header('KOSS IIT Kharagpur', 'utf-8')), sender))
    attendee_data = []
    for address in email_list:
        attendee_data.append({'email': address})

    if(has_meet):
        event = {
            'summary': f'{subject}',
            'description': f'{message}',
            'start': {
                'dateTime': f'{timeRange[0]}+05:30',
                'timeZone': 'Asia/Kolkata'
            },
            'end': {
                'dateTime': f'{timeRange[1]}+05:30',
                'timeZone': 'Asia/Kolkata'
            },
            'attendees': attendee_data,
            'reminders': {
                'useDefault': False,
                'overrides': [
                #email reminder 1 day before event
                {'method': 'email', 'minutes': 24 * 60},
                #pop-up reminder 10 minutes before event
                {'method': 'popup', 'minutes': 10},
                ],
            },
            'guestsCanSeeOtherGuests': False,
            'guestsCanInviteOthers': False,
            "conferenceData": {"createRequest": {"requestId": "sample123", "conferenceSolutionKey": {"type": "hangoutsMeet"}}}
        }
        return event
    
    event = {
            'summary': f'{subject}',
            'description': f'{message}',
            'start': {
                'dateTime': f'{timeRange[0]}+05:30',
                'timeZone': 'Asia/Kolkata'
            },
            'end': {
                'dateTime': f'{timeRange[1]}+05:30',
                'timeZone': 'Asia/Kolkata'
            },
            'attendees': attendee_data,
            'reminders': {
                'useDefault': False,
                'overrides': [
                #email reminder 1 day before event
                {'method': 'email', 'minutes': 24 * 60},
                #pop-up reminder 10 minutes before event
                {'method': 'popup', 'minutes': 10},
                ],
            },
            'guestsCanSeeOtherGuests': False,
            'guestsCanInviteOthers': False,
        }
    return event

def send_event(service, event):
    event = service.events().insert(calendarId='primary', body=event, sendNotifications=True,sendUpdates='all',conferenceDataVersion=1).execute()
    print ('Event created: %s' % (event.get('htmlLink')))
    print ('Meet link: %s' % (event.get('hangoutLink')))
    return event

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
    serviceCal = build("calendar", "v3", credentials=creds)

    timeSlot=[]
    
    # Getting extra static variables(those which are same for all mails) if required by the template - from arguments
    if len(sys.argv) > 4:
        variables = {}
        for arg in sys.argv[4:]:
            variable, value = arg.split("=")
            variables[variable] = value.strip()
        
        if 'slot_time' in variables:
            timeSlot=convert_to_RFC3339(variables['slot_time'])

        email_body_template = fill_variables(email_body_template, variables)
        subject_template = fill_variables(subject_template, variables)

    sender = "admin@kossiitkgp.org"

    with open(csv_file, newline="") as file:
        reader = csv.DictReader(file)

        emailList=[]

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

            emailList.append(email)

    # Calender invites cannot have personalised details
    email_body = email_body_template 
    subject = subject_template

    email_content = email_body + signature

    event_obj = create_event(sender,emailList,subject,email_content,timeSlot,hasMeet)
    send_event(serviceCal,event_obj)

    print("Script execution completed.")

if __name__ == "__main__":
    main(subject_template, email_body_template, signature)
