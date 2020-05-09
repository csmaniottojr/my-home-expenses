import base64
import os.path
import pickle

from google.auth.transport.requests import Request

import config
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

SCOPES = (
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.appdata",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
)


def get_credentials():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def list_gmail_messages(query, credentials):
    gmail = build("gmail", "v1", credentials=credentials)
    result = gmail.users().messages().list(userId="me", q=query).execute()
    return [message["id"] for message in result["messages"]]


def get_message(message_id, credentials):
    gmail = build("gmail", "v1", credentials=credentials)
    return gmail.users().messages().get(userId="me", id=message_id).execute()


def download_attachment(message_id, attachment_id, credentials):
    gmail = build("gmail", "v1", credentials=credentials)
    attachment = (
        gmail.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id,)
        .execute()
    )
    return base64.urlsafe_b64decode(attachment["data"])


def get_emails_ids_from_sheet(credentials):
    service = build("sheets", "v4", credentials=credentials)

    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=config.SPREADSHEET_ID, range=config.EMAIL_ID_RANGE)
        .execute()
    )

    values = result.get("values", [])
    return [value[0] if value else "" for value in values]


def update_sheet(rows, credentials):
    service = build("sheets", "v4", credentials=credentials)

    body = {"values": rows}

    service.spreadsheets().values().append(
        spreadsheetId=config.SPREADSHEET_ID,
        range=config.SHEET_NAME,
        valueInputOption="RAW",
        body=body,
    ).execute()


def upload_file_to_drive(filename, mimetype, file_buffer, credentials):
    service = build("drive", "v3", credentials=credentials)

    body = {"name": filename, "parents": [config.FOLDER_ID]}
    media = MediaInMemoryUpload(file_buffer, mimetype=mimetype)

    file = service.files().create(body=body, media_body=media, fields="id").execute()
    file_id = file.get("id")

    return f"https://drive.google.com/file/d/{file_id}"
