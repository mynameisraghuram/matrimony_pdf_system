import os
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_google_credentials():
    client_file = os.getenv("GOOGLE_OAUTH_CLIENT_FILE")
    token_file = os.getenv("GOOGLE_OAUTH_TOKEN_FILE")

    if not client_file:
        raise ValueError("GOOGLE_OAUTH_CLIENT_FILE is missing in .env")

    if not os.path.exists(client_file):
        raise FileNotFoundError(f"OAuth client file not found: {client_file}")

    creds = None

    if token_file and os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(client_file, SCOPES)
        creds = flow.run_local_server(port=0)

    if token_file:
        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds


def get_sheet_records():
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    worksheet_name = os.getenv("GOOGLE_WORKSHEET_NAME", "Sheet1")

    if not sheet_id:
        raise ValueError("GOOGLE_SHEET_ID is missing in .env")

    creds = get_google_credentials()
    service = build("sheets", "v4", credentials=creds)

    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=worksheet_name)
        .execute()
    )

    values = result.get("values", [])

    if not values:
        return []

    headers = values[0]
    rows = values[1:]

    records = []
    for row in rows:
        padded_row = row + [""] * (len(headers) - len(row))
        record = dict(zip(headers, padded_row))
        records.append(record)

    return records