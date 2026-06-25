import gspread
from google.oauth2.service_account import Credentials

from config import SHEET_ID, CREDENTIALS_FILE, HEADERS


def get_client():
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return gspread.authorize(creds)


def init_table():
    client = get_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    existing = sheet.get_all_values()
    if not existing:
        sheet.append_row(HEADERS)
    return sheet


def apply_conditional_formatting():
    client = get_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet = spreadsheet.sheet1

    existing = sheet.get_all_values()
    has_rules = len(existing) > 1 or (
        len(existing) == 1 and existing[0] == HEADERS
    )
    if not has_rules and not existing:
        sheet.append_row(HEADERS)

    col = HEADERS.index("Самовыкуп/раздача")
    body = {
        "requests": [
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": sheet.id,
                            "startColumnIndex": col,
                            "endColumnIndex": col + 1,
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": "Самовыкуп"}],
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 0.8,
                                    "green": 0.9,
                                    "blue": 0.7,
                                }
                            },
                        },
                    },
                    "index": 0,
                }
            },
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": sheet.id,
                            "startColumnIndex": col,
                            "endColumnIndex": col + 1,
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": "Раздача"}],
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 0.95,
                                    "green": 0.7,
                                    "blue": 0.7,
                                }
                            },
                        },
                    },
                    "index": 1,
                }
            },
        ]
    }
    spreadsheet.batch_update(body)


def set_font_size(size: int = 14):
    client = get_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    col_letter = chr(ord("A") + len(HEADERS) - 1)
    sheet.format(f"A:{col_letter}", {"textFormat": {"fontSize": size}})


def append_row(data: list):
    sheet = init_table()
    sheet.append_row(data)
