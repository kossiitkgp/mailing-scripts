import sys
from google_auth_oauthlib.flow import InstalledAppFlow

scopes = [f"https://www.googleapis.com/auth/gmail.{sys.argv[1]}"]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
creds = flow.run_local_server(port=0)

with open("token.json", "w") as token:
    token.write(creds.to_json())