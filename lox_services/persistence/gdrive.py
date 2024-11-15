import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from lox_services.persistence.config import SERVICE_ACCOUNT_PATH


# Authenticate with Google Drive API
def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        os.path.join(SERVICE_ACCOUNT_PATH),
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    print(os.path.join(SERVICE_ACCOUNT_PATH))
    return build("drive", "v3", credentials=creds)
