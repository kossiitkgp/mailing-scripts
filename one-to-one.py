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
from tkinterweb import HtmlFrame
from tkinter import filedialog
from tkinter import ttk, messagebox
from datetime import datetime


# If modifying SCOPES, delete the file token.json.
class EmailSender:
    def __init__(self):
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close) # When closing the UI
        self.notebook = ttk.Notebook(self.root)  # Notebook widget
        self.email_frame = Frame(self.notebook)  # Frame for sending emails
        self.calendar_frame = Frame(self.notebook) # Frame for sending calendar invites
        self.notebook.add(self.email_frame, text='Send Emails')  # Adding tabs to the notebook
        self.notebook.add(self.calendar_frame, text='Send Calendar Invites')
        self.notebook.pack(expand=1, fill='both')

        self.variables = {}
        s = ttk.Style() # Styling for tabs
        s.theme_create('custom_style', parent='alt', settings={
            "TNotebook.Tab": {
                "configure": {"padding": [5, 2], "background": "#608cab", "foreground": "#ffffff"},
                "map": {"background": [("selected", "#0067b0")]}
            }
        })
        s.theme_use('custom_style')

        self.variables_frame = None # frame for user variables
        self.load = False 
        self.ok = False
        self.is_calendar_invite = False 
        self.template_file = None #Template file location
        self.csv_file = None # csv file location
        self.subject_template = "" # template subject
        self.email_body_template = "" # email body
        self.signature = "" 
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.send",
                       "https://www.googleapis.com/auth/calendar"]
        self.service = None
        self.creds = None
        self.row = {}

    def on_close(self): # when closing UI
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    def select_csv_file(self):  # filedialog for selecting CSV file mail frame
        csv_file_path = filedialog.askopenfilename(title="Select CSV File")
        self.csv_file_entry.delete(0, END)
        self.csv_file_entry.insert(0, csv_file_path)

    def select_template_file(self):  # filedialog for selecting template file mail frmae
        template_file_path = filedialog.askopenfilename(
            title="Select Template File")
        self.template_file_entry.delete(0, END)
        self.template_file_entry.insert(0, template_file_path)

    def select_csv_file_calendar(self):  # filedialog for selecting CSV file calendar frame
        csv_file_path = filedialog.askopenfilename(title="Select CSV File")
        self.csv_file_entry_calendar.delete(0, END)
        self.csv_file_entry_calendar.insert(0, csv_file_path)

    # filedialog for selecting template file calendar frame
    def select_template_file_calendar(self):
        template_file_path = filedialog.askopenfilename(
            title="Select Template File")
        self.template_file_entry_calendar.delete(0, END)
        self.template_file_entry_calendar.insert(0, template_file_path)

    def command_ok(self):  # command for ok button mail frame (for initial mail)
        self.ok = True
        self.mail_frame.quit()

    def command_cancel(self):  # command for cancel button mail frame (for initial mail)
        self.ok = False
        self.mail_frame.destroy()

    def command_cancel_load(self):  # command cancel
        self.load = False
        self.root.destroy()

    def create_message(self, sender, to, subject, message):
        formatted_sender = formataddr(
            (str(Header('KOSS IIT Kharagpur', 'utf-8')), sender))
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

    # Refresh the user variables if another template is loaded
    def destroy_variables_frame(self):
        if self.variables_frame:
            self.variables_frame.destroy()

    def send_message(self, user_id, message):
        try:
            message = self.service.users().messages().send(
                userId=user_id, body=message).execute()
        except Exception as e:
            print(f"An error occurred while sending the message: {e}")

    def fill_variables(self, content, variables):  # replace the variables in template
        for variable, value in variables.items():
            placeholder = "{" + variable + "}"
            content = content.replace(placeholder, value)

        for variable, value in self.variables.items():  # replace user input variables if exists
            placeholder = "{" + variable + "}"
            content = content.replace(placeholder, value.get())

        return content

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def load_files(self):  # command for load button mail frame
        self.get_csv_variables()
        self.display_missing_variables(self.email_frame)
        self.load = True

    def load_files_calendar(self):  # command for load button calendar frame
        self.get_csv_variables()
        self.display_missing_variables(self.calendar_frame)
        self.is_calendar_invite = True
        self.load = True

    # get variables from csv that are in the template and matches variable_column_mapping
    def get_csv_variables(self):
        if self.csv_file_entry.get():
            with open(self.csv_file_entry.get(), newline="") as file:
                reader = csv.DictReader(file)
                self.row = next(iter(reader))
                required_columns = set([column for variables in variable_column_mapping.values()
                                        for column in variables if column in self.row])
                self.csv_variables = {}
                for variable, columns in variable_column_mapping.items():
                    for column in columns:
                        if column in required_columns:
                            self.csv_variables[variable] = self.row.get(
                                column, "").strip()
                            break

        elif self.csv_file_entry_calendar.get(): #gets variables is sending calendar invite
            with open(self.csv_file_entry_calendar.get(), newline="") as file:
                reader = csv.DictReader(file)
                self.row = next(iter(reader))
                required_columns = set([column for variables in variable_column_mapping.values()
                                        for column in variables if column in self.row])
                self.csv_variables = {}
                for variable, columns in variable_column_mapping.items():
                    for column in columns:
                        if column in required_columns:
                            self.csv_variables[variable] = self.row.get(
                                column, "").strip()
                            break

    def load_variables(self):  # get variables from template
        with open(self.template_file, "r") as template_file:
            template_content = template_file.read()
            placeholders = re.findall(r'\{(.*?)\}', template_content)
            self.variables = {placeholder: "" for placeholder in placeholders}

    def send_emails(self): # sending emails

        self.template_file = self.template_file_entry.get() # get template location
        self.csv_file = self.csv_file_entry.get() #get csv location

        with open(self.template_file, "r") as file:
            self.subject_template = file.readline().strip() # get subject
            self.email_body_template = "".join(file.readlines()[1:]) # get email body

        with open("./templates/signature") as file:
            self.signature = file.read() # signature

        self.get_credentials()

        self.service = build("gmail", "v1", credentials=self.creds)

        with open(self.csv_file, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader: # send mails to each entry
                required_columns = set([column for variables in variable_column_mapping.values(
                ) for column in variables if column in row]) 

                variables = {}
                for variable, columns in variable_column_mapping.items():
                    for column in columns:
                        if column in required_columns:
                            variables[variable] = row.get(column, "").strip()
                            break

                email = variables.get('email', "").strip()
                if not self.validate_email(email):
                    print(f'Invalid email provided: {email}')
                    continue

                email_body = self.fill_variables(
                    self.email_body_template, variables)
                subject = self.fill_variables(self.subject_template, variables)

                sender = "admin@kossiitkgp.org"
                email_content = email_body + self.signature
                message = self.create_message(
                    sender, email, subject, email_content)

                self.send_message("me", {"raw": message})
                print(f'Message sent to: {email}')

    # display initial mail to confirm the execution
    def display_initial_mail(self, frame):
        if (frame == self.email_frame):
            self.csv_file = self.csv_file_entry.get()
        elif (frame == self.calendar_frame):
            self.csv_file = self.csv_file_entry_calendar.get()
        if (frame == self.email_frame):
            self.template_file = self.template_file_entry.get()
        elif (frame == self.calendar_frame):
            self.template_file = self.template_file_entry_calendar.get()
        with open("./templates/signature") as file:
            self.signature = file.read()

        with open(self.template_file, "r") as file:
            self.subject_template = file.readline().strip()
            self.email_body_template = "".join(file.readlines()[1:])
        with open(self.csv_file, newline="") as file:
            reader = csv.DictReader(file)
            self.row = next(iter(reader))

            email = self.csv_variables.get('email', "").strip()

            email_body = self.fill_variables(
                self.email_body_template, self.csv_variables)
            subject = self.fill_variables(
                self.subject_template, self.csv_variables)

            sender = "admin@kossiitkgp.org"
            email_content = email_body + self.signature
            message = self.create_message(
                sender, email, subject, email_content)
            self.mail_frame = Tk()
            self.mail_frame.title("Mail Content")
            myhtmlframe = HtmlFrame(self.mail_frame, messages_enabled=False)
            myhtmlframe.load_html(email_content)
            myhtmlframe.pack(side=RIGHT)
            button_ok = Button(self.mail_frame, text='OK',
                               command=self.command_ok, background='#45f775')
            button_ok.pack()
            label = Label(self.mail_frame, text='')
            label.pack()
            button_cancel = Button(
                self.mail_frame, text='Cancel', command=self.command_cancel, background='#c73243')
            button_cancel.pack()
            self.mail_frame.mainloop()
            self.command_ok()

    def display_missing_variables(self, frame):  # get user variables
        self.destroy_variables_frame()
        self.variables_frame = Frame(frame)
        self.variables_frame.pack()

        label = Label(self.variables_frame, text="", pady=5)
        label.pack()

        if (frame == self.email_frame): # if frame is email frame get template location from its entry
            self.template_file = self.template_file_entry.get()
        elif (frame == self.calendar_frame):
            self.template_file = self.template_file_entry_calendar.get()

        # display user variables to get input
        if self.template_file:
            with open(self.template_file, "r") as template_file:
                template_content = template_file.read()
                placeholders = re.findall(r'\{(.*?)\}', template_content)
                placeholders = set(placeholders)
                for variable in placeholders:
                    if variable not in self.csv_variables:
                        label = Label(self.variables_frame, text=variable)
                        label.pack()
                        entry = Entry(self.variables_frame)
                        entry.pack()
                        self.variables[variable] = entry

        button_continue = Button(self.variables_frame, text='Continue',
                                 command=lambda: self.continue_after_variables(frame), background='#45f775')
        button_continue.pack()

    # command for continue button after loading user variables
    def continue_after_variables(self, frame):
        if all(entry.get() for entry in self.variables.values()) and frame == self.email_frame:
            self.root.quit()
            self.load = True
            self.display_initial_mail(frame)
        
        elif all(entry.get() for entry in self.variables.values()) and all(entry.get() for entry in self.timing_entries) and frame == self.calendar_frame:
            self.root.quit()
            self.load = True
            self.display_initial_mail(frame)
        else:
            print("Please fill all required variables.")

    def load_email_frame(self): # GUI code for loading sending emails frame
        label = Label(self.email_frame, text='Send Mails',
                      font=("Helvetica", "14")) # heading for mailing frame
        label.pack(side='top',pady = 10)

        select_csv_button = Button(self.email_frame, text="Select CSV File",
                                   command=self.select_csv_file, bg='#007bff', fg='white') 
        select_csv_button.pack()

        self.csv_file_entry = Entry(self.email_frame, width=50)
        self.csv_file_entry.pack()

        select_template_button = Button(
            self.email_frame, text="Select Template File", command=self.select_template_file, bg='#007bff', fg='white')
        select_template_button.pack()

        self.template_file_entry = Entry(self.email_frame, width=50)
        self.template_file_entry.pack()

        button_load = Button(self.email_frame, text='Load',
                             command=self.load_files, background='#45f775')
        button_load.pack(pady=10)

        button_cancel = Button(
            self.email_frame, text='Cancel', command=self.command_cancel_load, background='#c73243')
        button_cancel.pack()

    def load_calendar_frame(self): # GUI code for loading calendar invite frame
        label = Label(self.calendar_frame, text='Calendar Invite',
                      font=("Helvetica", "14")) # heading for calendar invite frame
        label.pack(pady = 10)
        select_csv_button = Button(self.calendar_frame, text="Select CSV File",
                                   command=self.select_csv_file_calendar, bg='#007bff', fg='white')
        select_csv_button.pack()

        self.csv_file_entry_calendar = Entry(self.calendar_frame, width=50)
        self.csv_file_entry_calendar.pack()

        select_template_button_calendar = Button(
            self.calendar_frame, text="Select Template File", command=self.select_template_file_calendar, bg='#007bff', fg='white')
        select_template_button_calendar.pack()


        self.template_file_entry_calendar = Entry(
            self.calendar_frame, width=50)
        self.template_file_entry_calendar.pack()

        label = Label(self.calendar_frame, text='Note: Input date and time in exact format , time is in 24:00 Hour format',pady=10)
        label.pack()

        self.start_frame = Frame(self.calendar_frame)
        self.start_frame.pack()

        self.end_frame = Frame(self.calendar_frame)
        self.end_frame.pack()

        self.timing_entries = []

        self.date_label = Label(self.start_frame, text="Select Start date (YYYY-MM-DD):")
        self.date_label.pack(side=LEFT)

        self.date_entry = Entry(self.start_frame)
        self.date_entry.pack(side=LEFT)
        self.timing_entries.append(self.date_entry)

        self.time_label = Label(self.start_frame, text="Select Start Time (HH:MM):")
        self.time_label.pack(side=LEFT)

        self.time_entry = Entry(self.start_frame)
        self.time_entry.pack(side=LEFT)
        self.timing_entries.append(self.time_entry)

        self.end_date_label = Label(self.end_frame, text="Select End date (YYYY-MM-DD):")
        self.end_date_label.pack(side=LEFT)

        self.end_date_entry = Entry(self.end_frame)
        self.end_date_entry.pack(side=LEFT)
        self.timing_entries.append(self.end_date_entry)

        self.end_time_label = Label(self.end_frame, text="Select End Time (HH:MM):")
        self.end_time_label.pack(side=LEFT)

        self.end_time_entry = Entry(self.end_frame)
        self.end_time_entry.pack(side=LEFT)
        self.timing_entries.append(self.end_time_entry)

        label_calendar = Label(self.calendar_frame, text='')
        label_calendar.pack()

        button_load_calendar = Button(self.calendar_frame, text='Load',
                                      command=self.load_files_calendar, background='#45f775')
        button_load_calendar.pack(pady=10)

        button_cancel = Button(
            self.calendar_frame, text='Cancel', command=self.command_cancel_load, background='#c73243')
        button_cancel.pack()

    def main(self):
        # Initalizing UI window -- START
        self.get_credentials()
        self.root.title("Email Script")
        self.load_email_frame()
        self.load_calendar_frame()
        self.root.mainloop()
        # initializing UI Window -- END

        if self.load and self.ok and not self.is_calendar_invite:
            self.send_emails()  # send mails

        elif self.load and self.ok and self.is_calendar_invite:
            self.create_event() # create calendar invite

        print("Script execution completed.")

    def get_credentials(self):
        self.creds = None

        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file(
                "token.json", self.SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

# event description is created assuming no variable is used from csv
# variables in description are taken as user input only..
# do proper mapping in variable-mapping and use proper variable names in template
                
    def create_event(self): # function to create calendar invite
        self.template_file = self.template_file_entry_calendar.get()
        self.csv_file = self.csv_file_entry_calendar.get()

        with open(self.template_file, "r") as file:
            self.subject_template = file.readline().strip()
            self.email_body_template = "".join(file.readlines()[1:])

        with open("./templates/signature") as file:
            self.signature = file.read()

        email_body = self.fill_variables(
            self.email_body_template, {})
        subject = self.fill_variables(self.subject_template, {})

        service = build('calendar', 'v3', credentials=self.creds)
        email_list = []
        with open(self.csv_file, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                required_columns = set([column for variables in variable_column_mapping.values(
                ) for column in variables if column in row])

                variables = {}
                for variable, columns in variable_column_mapping.items():
                    for column in columns:
                        if column in required_columns:
                            variables[variable] = row.get(column, "").strip()
                            break

                email = variables.get('email', "").strip()
                email_list.append(email)

        print(email_list)

        event = {
            'summary': subject,
            'description': email_body,
            'start': {
                'dateTime': str(self.date_entry.get()).strip()+'T'+str(self.time_entry.get()).strip() +':00',
                'timeZone': 'Asia/Kolkata',
            },
            # '2024-03-27T11:00:00'
            'end': {
                'dateTime': str(self.end_date_entry.get()).strip()+'T'+str(self.end_time_entry.get()).strip()+':00',
                'timeZone': 'Asia/Kolkata', 
            },
            'attendees': [{'email': email} for email in email_list],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': 'sample123',
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            },
            'guestsCanModify': False,
            'guestsCanInviteOthers': False,
            'guestsCanSeeOtherGuests': False,
            'sendNotifications': True  # Send invitation emails
        }

        event = service.events().insert(calendarId='primary', body=event,
                                        conferenceDataVersion=1).execute()
        print('Event created: %s' % (event.get('htmlLink')))


if __name__ == "__main__":
    email_sender = EmailSender()
    email_sender.main()
