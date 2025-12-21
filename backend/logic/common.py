import plaid
import os
from plaid.api import plaid_api
from logic.aws_utils import read_cursor_s3, upload_cursor_s3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CURSOR_PATH_LOCAL = f"{BASE_DIR}/../data_access/.cursor"
CURSOR_FILE_NAME_S3 = ".cursor"


def start_plaid():
    """ "
    Starts plaid client
    """
    configuration = plaid.Configuration(
        host=plaid.Environment.Production,
        api_key={
            "clientId": os.getenv("PLAID_CLIENT_ID"),
            "secret": os.getenv("PLAID_SECRET"),
        },
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    return client


def read_cursor():
    return read_cursor_s3(CURSOR_FILE_NAME_S3)


def save_cursor(cursor: str):
    upload_cursor_s3(cursor, CURSOR_FILE_NAME_S3)


def read_cursor_local():
    """
    Reads the cursor from the file
    """
    cursor = ""
    if os.path.exists(CURSOR_PATH_LOCAL):
        cursor = open(CURSOR_PATH_LOCAL, "r").read()
    if cursor is None:
        cursor = ""

    return cursor


def save_cursor_local(cursor: str):
    try:
        open(CURSOR_PATH_LOCAL, "w").write(cursor)
    except Exception as e:
        print("There was an error saving the cursor")
        print(f"NEW CURSOR: {cursor}")
        print(e)
