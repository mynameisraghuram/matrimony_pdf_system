"""
sheet_reader.py

Reads rows from Google Sheets using OAuth credentials.

Expected environment variables:
- GOOGLE_OAUTH_CLIENT_FILE
- GOOGLE_OAUTH_TOKEN_FILE
- GOOGLE_SHEET_ID

Optional:
- GOOGLE_WORKSHEET_NAME
- GOOGLE_WORKSHEET_INDEX
- GOOGLE_SCOPES

Behavior:
1. If GOOGLE_WORKSHEET_NAME is set and found, use it.
2. Else if GOOGLE_WORKSHEET_INDEX is set, use that sheet index (0-based).
3. Else use first worksheet.

This version safely handles duplicate header names by auto-renaming them:
Example:
    Occupation
    Occupation
becomes:
    Occupation
    Occupation__2
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import gspread


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

DEFAULT_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _clean_env(value):
    if value is None:
        return None
    value = str(value).strip().strip('"').strip("'")
    return value or None


def _get_scopes():
    raw_scopes = _clean_env(os.getenv("GOOGLE_SCOPES"))
    if not raw_scopes:
        return DEFAULT_SCOPES
    scopes = [item.strip() for item in raw_scopes.split(",") if item.strip()]
    return scopes or DEFAULT_SCOPES


def _resolve_path(path_value):
    path_value = _clean_env(path_value)
    if not path_value:
        return None

    path = Path(path_value)
    if path.is_absolute():
        return path

    return (BASE_DIR / path).resolve()


def _ensure_parent_dir(file_path: Path):
    file_path.parent.mkdir(parents=True, exist_ok=True)


def _get_required_setting(name: str) -> str:
    value = _clean_env(os.getenv(name))
    if not value:
        raise ValueError(
            f"Missing required environment variable: {name}. "
            f"Please update {BASE_DIR / '.env'}"
        )
    return value


def _load_credentials(client_file: Path, token_file: Path, scopes):
    creds = None

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), scopes)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _ensure_parent_dir(token_file)
        token_file.write_text(creds.to_json(), encoding="utf-8")
        return creds

    if not client_file.exists():
        raise FileNotFoundError(f"Google OAuth client file not found: {client_file}")

    flow = InstalledAppFlow.from_client_secrets_file(str(client_file), scopes)
    creds = flow.run_local_server(port=0)

    _ensure_parent_dir(token_file)
    token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds


def get_gspread_client():
    scopes = _get_scopes()

    client_file = _resolve_path(_get_required_setting("GOOGLE_OAUTH_CLIENT_FILE"))
    token_file = _resolve_path(_get_required_setting("GOOGLE_OAUTH_TOKEN_FILE"))

    if client_file is None:
        raise ValueError("GOOGLE_OAUTH_CLIENT_FILE could not be resolved")
    if token_file is None:
        raise ValueError("GOOGLE_OAUTH_TOKEN_FILE could not be resolved")

    creds = _load_credentials(client_file, token_file, scopes)
    return gspread.authorize(creds)


def get_spreadsheet():
    sheet_id = _get_required_setting("GOOGLE_SHEET_ID")
    client = get_gspread_client()
    return client.open_by_key(sheet_id)


def list_worksheet_names():
    spreadsheet = get_spreadsheet()
    worksheets = spreadsheet.worksheets()
    return [ws.title for ws in worksheets]


def get_worksheet():
    spreadsheet = get_spreadsheet()
    worksheets = spreadsheet.worksheets()

    if not worksheets:
        raise ValueError("No worksheets found in the spreadsheet.")

    worksheet_name = _clean_env(os.getenv("GOOGLE_WORKSHEET_NAME"))
    worksheet_index_raw = _clean_env(os.getenv("GOOGLE_WORKSHEET_INDEX"))

    available_names = [ws.title for ws in worksheets]

    if worksheet_name:
        for ws in worksheets:
            if ws.title.strip() == worksheet_name.strip():
                return ws

        raise ValueError(
            "Worksheet not found.\n"
            f"Requested GOOGLE_WORKSHEET_NAME: {worksheet_name}\n"
            f"Available worksheets: {available_names}"
        )

    if worksheet_index_raw is not None:
        try:
            worksheet_index = int(worksheet_index_raw)
        except ValueError:
            raise ValueError(
                f"GOOGLE_WORKSHEET_INDEX must be an integer, got: {worksheet_index_raw}"
            )

        if worksheet_index < 0 or worksheet_index >= len(worksheets):
            raise ValueError(
                f"GOOGLE_WORKSHEET_INDEX out of range: {worksheet_index}. "
                f"Available worksheet count: {len(worksheets)}"
            )

        return worksheets[worksheet_index]

    return worksheets[0]


def _normalize_header_cell(value, index):
    """
    Convert empty header names into fallback column names.
    """
    value = "" if value is None else str(value).strip()
    if value:
        return value
    return f"column_{index + 1}"


def make_headers_unique(headers):
    """
    Rename duplicate headers safely.

    Example:
        ['Name', 'Occupation', 'Occupation']
    becomes:
        ['Name', 'Occupation', 'Occupation__2']
    """
    counts = {}
    unique_headers = []

    for index, header in enumerate(headers):
        base_header = _normalize_header_cell(header, index)

        if base_header not in counts:
            counts[base_header] = 1
            unique_headers.append(base_header)
        else:
            counts[base_header] += 1
            unique_headers.append(f"{base_header}__{counts[base_header]}")

    return unique_headers


def fetch_raw_values():
    """
    Fetch full worksheet values as raw 2D list.
    Useful for debugging header issues.
    """
    worksheet = get_worksheet()
    return worksheet.get_all_values()


def fetch_sheet_rows():
    """
    Fetch all rows as list of dictionaries using a manually built header row.

    This safely supports duplicate headers.
    """
    worksheet = get_worksheet()
    values = worksheet.get_all_values()

    if not values:
        return []

    raw_headers = values[0]
    headers = make_headers_unique(raw_headers)

    rows = []
    data_rows = values[1:]

    for row in data_rows:
        padded_row = list(row) + [""] * (len(headers) - len(row))
        trimmed_row = padded_row[:len(headers)]

        record = {}
        for header, value in zip(headers, trimmed_row):
            cleaned_value = value.strip() if isinstance(value, str) else value
            record[header] = cleaned_value if cleaned_value != "" else None

        # skip completely empty rows
        if any(value is not None for value in record.values()):
            rows.append(record)

    return rows


if __name__ == "__main__":
    print("=" * 80)
    print("Google Sheet Reader Debug")
    print("=" * 80)

    spreadsheet = get_spreadsheet()
    print(f"Spreadsheet title: {spreadsheet.title}")

    worksheet_names = list_worksheet_names()
    print("Available worksheets:")
    for i, name in enumerate(worksheet_names):
        print(f"  [{i}] {name}")

    worksheet = get_worksheet()
    print(f"Selected worksheet: {worksheet.title}")

    values = fetch_raw_values()
    if not values:
        print("Worksheet is empty.")
    else:
        raw_headers = values[0]
        unique_headers = make_headers_unique(raw_headers)

        print("\nRaw headers:")
        for i, header in enumerate(raw_headers, start=1):
            print(f"  {i}. {header}")

        print("\nUnique headers used by pipeline:")
        for i, header in enumerate(unique_headers, start=1):
            print(f"  {i}. {header}")

        rows = fetch_sheet_rows()
        print(f"\nFetched rows: {len(rows)}")

        if rows:
            print("\nFirst row:")
            print(rows[0])

    print("=" * 80)