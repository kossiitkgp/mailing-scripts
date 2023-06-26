# Mailing Automation Scripts

Automates the mailing process for KOSS during various events like KWoC and selections.
 
> **Warning** Always do a test run before using the scripts, there are many things which might go wrong and we can't afford sending broken/incorrect mails to the reciepients.

### How to use

0. For the first time, you need to [generate token for api](#generating-token-for-gmail-enabled-googleapi).

1. Either use already available templates or create a new template with the convention mentioned in [about templates](./templates/README.md)

2. Make sure the csv files meets the following requirements:
    - The email column must be the 2nd column(when counting starts from 1).

3. Make sure the files are stored in correct directory:
    - Templates files must be stored in `./templates/`.
    - CSV files must be stored in `./csv/`, 

    Hence no need to mention them again while specifying the location, just speciy the location after these default directories.

4. Use the script according to your needs, `bcc.py` or `one-to-one.py`. Both follow same method of execution
    ```bash
    python3 script.py <template> <csv_file> (OPTIONAL)<variables with same value for all mails>
    ```
    
### Executing the scripts

Here are one example for each case supported:

```bash
python3 one-to-one.py selections/onboarding onboarding.csv number_of_applicants="250+"
python3 one-to-one.py selections/task day1.csv deadline="Monday, 9 June 2023"
python3 bcc.py selections/rejection rejected.csv
python3 bcc.py selections/round1-interview-slot r1d1.csv slot_time="Tuesday, 3 June 2023, 10:00 PM - 11:00 PM" lobby_link="https://meet.google.com/xxx-xxxx-xxx"
python3 bcc.py selections/round2-interview-slot r2d2.csv slot_time="Tuesday, 3 June 2023, 10:00 PM - 11:00 PM" lobby_link="https://meet.google.com/xxx-xxxx-xxx"
```

### Generating token for GMail enabled googleapi

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
    - Run any of the scripts. Refer [Executing the scripts](#executing-the-scripts) section for commands.
    - Browser window will open and ask you to select the account, choose `admin@kossiitkgp.org` (get access to it if you don't have).
    - Allow permission on that email to use just enabled __GMAIL API__.
    - `token.json` will be generated in the root directory of this repository and mailing will start.
    
6. Next time mailing will start automatically since `token.json` has been generated.
