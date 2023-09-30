# INarrator
![](https://github.com/keenborder786/INarrator/blob/main/assets/Logo.png)

## Install the Package

```
pip install inarrator
```

## Use the Package

### Gmail

1. In the Google Cloud console, enable the Gmail [API](https://console.cloud.google.com/flows/enableapi?apiid=gmail.googleapis.com).
![](https://github.com/keenborder786/INarrator/blob/48034edb1934c7cdec3117f42a60d9b580c2713d/assets/Image_1_Gmail.png)

2. Register your App

    - In the Google Cloud console, go to [OAuth Consent screen](https://console.cloud.google.com/apis/credentials/consent)
    - Once on OAuth Consent Screen, select User Type External and then click create:
    ![](https://github.com/keenborder786/INarrator/blob/90abfdb444974c2dc2fb91be4afc86e288397564/assets/Image_2_Gmail.png)
    - Now complete the registration of your app which is fairly simple. Just remember two things:
        - Since this is a Testing App, you will have to add some test users (ideally make it the same email through which you are registering the app)
        - Add `.../auth/gmail.readonly` scope
3. Create "gmail_credentials.json" file:
    - Go to [Credentials](https://console.cloud.google.com/apis/credentials)
    - Click `+ CREATE CREDENTIALS > OAuth client ID`
    - SELECT `Desktop app` as application type
    ![](https://github.com/keenborder786/INarrator/blob/bca253b67bc6c3884aaf0815afd6ed3f9a80b3af/assets/Image_3_Gmail.png)
    - After this a pop up will appear which will have a option to DOWNLOAD OAuth Client JSON file.
    - Save the JSON and rename it to `gmail_credentials.json`

4. Use the inarrator 

- Chat-GPT Example

    ```python
    from inarrator.email import Gmail
    from inarrator.summarizer.gpt import GPTModel

    gmail = Gmail()
    gmail.authenticate(
        credentials_path="gmail_credentials.json",
        gmail_scope=["https://www.googleapis.com/auth/gmail.readonly"],
    )
    # https://support.google.com/mail/answer/7190 (You can read more about Gmail Filters)
    emails = gmail.get_latest_emails(
            gmail_filters="from:(-noreply -no-reply) is:unread -category:social -category:promotions -unsubscribe", # 
            gmail_max_emails="30",
        )
    model = GPTModel(model_name = 'gpt-3.5-turbo-16k',api_token = "") # OPENAI_API_KEY
    documents = []
    for email in emails:
        documents.append(email)
    print(model.summarize(documents))

    ```

- Hugging Face Hub Example

    ```python

    from inarrator.email import Gmail
    from inarrator.summarizer import HuggingFaceModel


    gmail = Gmail()
    gmail.authenticate(
        credentials_path="gmail_credentials.json",
        gmail_scope=["https://www.googleapis.com/auth/gmail.readonly"],
    )
    emails = gmail.get_latest_emails(
            gmail_filters="from:(-noreply -no-reply) is:unread -category:social -category:promotions -unsubscribe",
            gmail_max_emails="30",
        )
    model =  HuggingFaceModel(model_name="tuner007/pegasus_summarizer", api_token="") # HF_HUB_TOKEN
    print(model.summarize(emails[0])) # Hugging Face Hub Models currently can summarize one email at a time.
    ```



### Outlook


1.  Create a New App [Registration](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
![](https://github.com/keenborder786/INarrator/blob/main/assets/Image_1_Outlook.png)

2. Request API permissions (Only Mail.Read)

![](https://github.com/keenborder786/INarrator/blob/main/assets/Image_3_Outlook.png)


3. Configure the Platform

    - Add a Mobile and Desktop Application
    ![](https://github.com/keenborder786/INarrator/blob/main/assets/Image_4_Outlook.png)
    - Choose the Following Configuration
    ![](https://github.com/keenborder786/INarrator/blob/main/assets/Image_5_Outlook.png)


4. Create a new client secret

    - Click on `+ New client secret`.
    ![](https://github.com/keenborder786/INarrator/blob/main/assets/Image_2_Outlook.png)
    - Now create the following JSON and name it `outlook_credentials.json`. You can get `Application (client) ID` & `Directory (tenant) ID` from overview of your App.
    ```json
    {"application_id":"Application (client) ID",
    "authority_url":"https://login.microsoftonline.com/{Directory (tenant) ID}",
    "outlook_scope":["Mail.Read"]}
    ```
5. Since OAuth only work https but our redirect URI is localhost, we would have to make the following environment variable

```console
export OAUTHLIB_INSECURE_TRANSPORT=1
```

5. Use the inarrator 

- Chat-GPT Example

    ```python
    from inarrator.email import OutLook
    from inarrator.summarizer.gpt import GPTModel

    outlook = OutLook()
    outlook.authenticate(
        credentials_path="outlook_credentials.json",
        outlook_scope=["Mail.Read"],
    )
    emails = outlook.get_latest_emails(
                outlook_max_emails=5,
            )
    model = GPTModel(model_name = 'gpt-3.5-turbo-16k',api_token = "") # OPENAI_API_KEY
    documents = []
    for email in emails:
        documents.append(email)
    print(model.summarize(documents))

    ```

- Hugging Face Hub Example

    ```python

    from inarrator.email import OutLook
    from inarrator.summarizer.huggingface import HuggingFaceModel


    outlook = OutLook()
    outlook.authenticate(
        credentials_path="outlook_credentials.json",
        outlook_scope=["Mail.Read"],
    )
    emails = outlook.get_latest_emails(
                outlook_max_emails=5,
            )
    model =  HuggingFaceModel(model_name="tuner007/pegasus_summarizer", api_token="") # HF_HUB_TOKEN
    print(model.summarize(emails[0])) # Hugging Face Hub Models currently can summarize one email at a time.    
    
    ```
