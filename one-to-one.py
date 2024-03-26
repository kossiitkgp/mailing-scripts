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
from tkinter import filedialog


# If modifying SCOPES, delete the file token.json.
class EmailSender:
    def __init__(self):
        self.root = Tk()
        self.variables = {}
        self.variables_frame = None
        self.ok = False
        self.template_file = None
        self.csv_file = None
        self.subject_template = ""
        self.email_body_template = ""
        self.signature = ""
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        self.service = None
        self.row = {}

    def select_csv_file(self):  # filedialog for selecting CSV file
        csv_file_path = filedialog.askopenfilename(title="Select CSV File")
        self.csv_file_entry.delete(0, END)
        self.csv_file_entry.insert(0, csv_file_path)

    def select_template_file(self):  # filedialog for selecting CSV file
        template_file_path = filedialog.askopenfilename(
            title="Select Template File")
        self.template_file_entry.delete(0, END)
        self.template_file_entry.insert(0, template_file_path)

    def command_ok(self):  # command for ok button mail frame
        self.ok = True
        self.mail_frame.quit()

    def command_cancel(self):  # command for cancel button mail frame
        self.ok = False
        self.mail_frame.destroy()

    def command_cancel_load(self):  # command for cancel button main frame
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

        for variable, value in self.variables.items(): # replace user input variables if exists
            placeholder = "{" + variable + "}"
            content = content.replace(placeholder, value.get())

        return content

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def load_files(self):  # command for load button main frame
        self.get_csv_variables()
        self.display_missing_variables()
        self.load = True

    # get variables from csv that are in the template and matches variable_column_mapping
    def get_csv_variables(self):
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

    def load_variables(self):  # get variables from template
        with open(self.template_file, "r") as template_file:
            template_content = template_file.read()
            placeholders = re.findall(r'\{(.*?)\}', template_content)
            self.variables = {placeholder: "" for placeholder in placeholders}

    def send_emails(self):
        self.template_file = self.template_file_entry.get()
        self.csv_file = self.csv_file_entry.get()

        with open(self.template_file, "r") as file:
            self.subject_template = file.readline().strip()
            self.email_body_template = "".join(file.readlines()[1:])

        with open("./templates/signature") as file:
            self.signature = file.read()

        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file(
                "token.json", self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        self.service = build("gmail", "v1", credentials=creds)

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
    def display_initial_mail(self):
        self.csv_file = self.csv_file_entry.get()
        self.template_file = self.template_file_entry.get()
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

    def display_missing_variables(self): # get user variables
        self.destroy_variables_frame() 
        self.variables_frame = Frame(self.root)
        self.variables_frame.pack()

        label = Label(self.variables_frame, text="", pady=5)
        label.pack()

        self.template_file = self.template_file_entry.get()
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
                                 command=self.continue_after_variables, background='#45f775')
        button_continue.pack()

    # command for continue button after loading user variables
    def continue_after_variables(self):
        if all(entry.get() for entry in self.variables.values()):
            self.root.quit()
            self.load = True
            self.display_initial_mail()
        else:
            print("Please fill all required variables.")

    def main(self):
        # Initalizing UI window -- START
        self.root.title("Email Script")

        select_csv_button = Button(self.root, text="Select CSV File",
                                   command=self.select_csv_file, bg='#007bff', fg='white')
        select_csv_button.pack()

        self.csv_file_entry = Entry(self.root, width=50)
        self.csv_file_entry.pack()

        select_template_button = Button(
            self.root, text="Select Template File", command=self.select_template_file, bg='#007bff', fg='white')
        select_template_button.pack()

        self.template_file_entry = Entry(self.root, width=50)
        self.template_file_entry.pack()

        button_load = Button(self.root, text='Load',
                             command=self.load_files, background='#45f775')
        button_load.pack()

        label = Label(self.root, text='')
        label.pack(side='top')

        button_cancel = Button(
            self.root, text='Cancel', command=self.command_cancel_load, background='#c73243')
        button_cancel.pack()

        self.root.mainloop()
        # initializing UI Window -- END

        if self.load and self.ok:
            self.send_emails()  # send mails

        print("Script execution completed.")


if __name__ == "__main__":
    email_sender = EmailSender()
    email_sender.main()
