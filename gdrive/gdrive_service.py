from google.oauth2 import service_account
from googleapiclient.discovery import build


def get_drive_service(cred_file_path: str):
    creds = service_account.Credentials.from_service_account_file(
        cred_file_path, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build('drive', 'v3', credentials=creds)
