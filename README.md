# Selection Mailing Automation

Automates the mailing of selection status (rejection status and next round task) during the selection procedure in KOSS.
 
> **Warning** Always do a test run before using it, there are many things which might go wrong and we can't afford that.

### Getting credentials.json for GMail enabled googleapi

1. Go to the [Google Cloud Console](https://console.cloud.google.com).

2. Create a new project or select an existing project.

3. Enable the Gmail API:
    - In the Cloud Console, navigate to the "APIs & Services" > "Library" page.
    - Search for "Gmail API" and select it.
    - Click the "Enable" button to enable the API for your project.
    
4. Create credentials for your project:
    - In the Cloud Console, navigate to the "APIs & Services" > "Credentials" page.
    - Click the "Create Credentials" button and select "OAuth client ID".
    - If you don't have any "OAuth client ID" then you will have to create it, you can keep the settings however you want just make sure to add `admin@kossiitkgp.org` as a valid testing account/user during the 3rd step of creation.
    - Choose "Desktop app" as the application type (since you're running the script locally).
    - Fill in the name for the OAuth client ID and click the "Create" button.
    - You'll see your client ID and client secret on the next screen.

5. Generate a refresh token:
    - Download the JSON file for the created OAuth client ID by clicking on the download icon next to it.
    - Save the JSON file securely in the root folder of this repository.
    - Run any of the script for the first time. Refer [Executing the scripts](#executing-the-scripts) section for commands.
    - Browser window will open and ask you to select the account, choose `admin@kossiitkgp.org` (get access to it if you don't have).
    - Allow permission on that email to use just enabled __GMAIL API__.
    - `token.json` will be generated in the root directory of this repository and mailing will start.
    
6. Next time mailing will start automatically since `token.json` has been generated.

### Executing the scripts

Here is the description on how to execute the scripts:

```graphql
python3 bcc.py (name of the variable containing the mail to be sent, in emailContents.py - currently supports rejection and interview)
python3 task-mailing.py (path to csv file containing details about students and task for a particular day) (day, DD MON YEAR [Task submission deadline])
```

Here are one example for each case supported:

```bash
python3 bcc.py interview csv/d1s2.csv "Saturday, 12 May, 10:00PM - 11:00PM"
python3 bcc.py rejection csv/rejected.csv
python3 one-to-one.py task csv/day2.csv "Tuesday, 23 May 2023"
python3 one-to-one.py onboarding csv/day2.csv "250+"
```
