# Mailing Automation Scripts

Automates the mailing process for KOSS during various events like KWoC and selections.
 
> **Warning** Always do a test run before using the scripts, there are many things which might go wrong and we can't afford sending broken/incorrect mails to the reciepients.

### How to use

0. For the first time, you need to [generate token for api](#generating-token-for-gmail-enabled-googleapi).

1. Either use already available [templates](./templates) or create a new template with the conventions mentioned in [about templates](./templates/README.md).

2. Make sure the the column names for `name` and `email` entries are one of those mentioned in [variable_mappings.py](./templates/variable_mappings.py).
   
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

1. Follow the steps at [Gmail API - Python Quickstart](https://developers.google.com/gmail/api/quickstart/python) guide to get `credentials.json`.
   > **Note** `credentials.json` is permanent until you delete it in your google clound console.<br>
   > And make sure to add `admin@kossiitkgp.org` as a test user in case you made the app internal.

2. Follow the steps below to generate `token.json`:
    - Download [gentokenjson.py](https://gist.github.com/proffapt/adbc716a427c036f238e828d8995e1a3) in the same folder containing `credentials.json`
    - Import the required module
      
      ```bash
      pip install google-auth-oauthlib
      ```
    - Execute `gentokenjson.py` with `send` argument
   
      ```bash
      python3 gentokenjson.py send
      ```
    - Browser window will open and ask you to select the account, choose the one receiving OTP for login
    - Allow permission on that email to use just enabled __GMAIL API__
       - Click on `Continue` instead of __Back To Safety__
       - Then press `Continue` again
    - `token.json` will be generated in same folder as that of `credentials.json`
  
    > **Warning** `token.json` expires after sometime. So make sure to check that in your projects and keep refreshing it.
