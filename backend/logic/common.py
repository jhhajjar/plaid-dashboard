import plaid
import os
from plaid.api import plaid_api

CURSOR_PATH = '../data-access/.cursor'

def start_plaid():
    """"
    Starts plaid client
    """
    configuration = plaid.Configuration(
        host=plaid.Environment.Production,
        api_key={
            'clientId': os.getenv("PLAID_CLIENT_ID"),
            'secret': os.getenv("PLAID_SECRET"),
        }
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    return client

def read_cursor():
    """
    Reads the cursor from the file
    """
    cursor = ""
    if os.path.exists(CURSOR_PATH):
        cursor = open(CURSOR_PATH, 'r').read()
    if cursor is None:
        cursor = ""
        
    return cursor

def save_cursor(cursor: str):
    try:
        open(CURSOR_PATH).write(cursor)
    except Exception as e:
        print('There was an error saving the cursor')
        print(f'NEW CURSOR: {cursor}')
        print(e)