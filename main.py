import plaid
import pandas as pd
import numpy as np
import os.path
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.transactions_get_request import TransactionsGetRequest
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from collections import defaultdict
from plaid.api import plaid_api
from datetime import datetime as dt
from corn import *

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Range of cells to update
TABLE_CELLS = 'A2:E1000'

SKIP_THESE = [
    "Recurring Automatic Payment",
    "TD BANK PAYMENT",
    "TD BANK"
]

def start_plaid():
    """"
    Starts plaid client
    """
    configuration = plaid.Configuration(
        host=plaid.Environment.Development,
        api_key={
            'clientId': CLIENT_ID,
            'secret': SECRET,
        }
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    return client

def google_credentials():
    """
    Get google credentials if we don't have them...
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def get_googoo_df():
    """
    Read in existing spreadsheet into a dataframe
    """
    try:
        creds = google_credentials()
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=TABLE_CELLS).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            raise Exception("No data found")

        # read into DF
        vals_np = np.array(values)
        spreadsheet_df = pd.DataFrame(
            {
                'Month': vals_np[:,0].astype(int),
                'Date': vals_np[:,1],
                'Description': vals_np[:,2],
                'Category': vals_np[:,3],
                'Amount': vals_np[:,4].astype(float)
            }
        )
        # parse dates and sort
        spreadsheet_df['Date'] = pd.to_datetime(spreadsheet_df['Date'])
        spreadsheet_df['Date'] = spreadsheet_df['Date'].dt.date
        spreadsheet_df.sort_values('Date', ascending=False, inplace=True)
        
        return spreadsheet_df
        
    except HttpError as err:
        print(err)
    except Exception as e:
        print(e)

def get_recent_transactions(start, end):
    """
    Retrieve all transactions between two dates
    start: start date (datetime.date)
    end: end date (datetime.date)
    """
    client = start_plaid()

    request = TransactionsGetRequest(
        access_token=ACCESS_TOKEN,
        start_date=start,
        end_date=end,
    )
    response = client.transactions_get(request)
    transactions = response['transactions']

    # the transactions in the response are paginated, so make multiple calls while increasing the offset to
    # retrieve all transactions
    while len(transactions) < response['total_transactions']:
        options = TransactionsGetRequestOptions()
        options.offset = len(transactions)

        request = TransactionsGetRequest(
            access_token=ACCESS_TOKEN,
            start_date=start,
            end_date=end,
            options=options
        )
        response = client.transactions_get(request)
        transactions += response['transactions']
    
    return transactions

def process_transaction(tr):
    """
    Get relevant information out of transaction (month, date, description, plaid categories, and amount)
    tr: JSON transaction object
    """
    description = tr['merchant_name'] if tr['merchant_name'] else tr['name']
    amount = -tr['amount']
    date = tr['authorized_date'] if tr['authorized_date'] else tr['date']
    category = categorize(tr, description)
    month = date.month
    
    return month, date, description, category, amount

def categorize(tr, name):
    """
    Categorize based on spreadsheet
    name: merchant name
    plaid_cat: plaid categories (- delimited)
    amount: dollar amount:
    account_id: id of account associated with this purchase
    """

    # td cash credit card
    if tr['account_id'] == 'vQzDkopk4jfDPJyZ5qXnfqnAVD00mMF8d4RDb':
        return "Food"

    category_map = {
        "Supermarkets and Groceries": "Groceries",
        "Public Transport Services": "Transportation",
        "Travel": "Transportation",
        "Venmo": "Food",
        "Financial Planning and Investments": "Investing",
        "Recreation": "Self Improvement",
        "Restaurants": "Food",
        "Photography": "Entertainment",
        "Payroll": "Income",
        "Deposit": "Income",
        "Food and Drink": "Food",
        "Credit": "Income",
        "Convenience": "Groceries",
    }

    name_map = {
        "ski": "Entertainment",
        "too good to go inc.": "Food",
        "robinhood": "Investing",
        "hopper": "Transportation",
        "dartmouth coach": "Transportation",
        "nontd atm fee": "Fee" 
    }

    if name == 'Venmo' and tr['amount'] == 60:  #guitar
        return "Self Improvement"
    
    if tr['category'] is not None:
        # check categories
        for key in category_map:
            if key in tr['category']:
                return category_map[key]

    # check name
    for key in name_map:
        if key.lower() in name.lower():
            return name_map[key]

    # couldn't categorize
    return ""

def add_rent(df, today):
    """
    Add rent to the last day of the last month
    df: the spreadsheet
    """
    # get the last month
    curr_month = today.month
    last_month = (curr_month - 1)%12

    # get all transactions from last month
    last_month_trans = df[df['Month'] == last_month]
    # see if rent is in there
    if ((last_month_trans['Amount'] == -1500) & (last_month_trans['Category'] == 'Rent')).any():
        return df
    else:
        # put rent in for last day of that month
        last_date = last_month_trans['Date'].values[0]
        rent_row = [last_month, last_date, "Rent", "Rent", -1500]
        all_rows = df.values.tolist()
        all_rows.append(rent_row)
        df = pd.DataFrame(all_rows, columns=['Month', 'Date', 'Description', 'Category', 'Amount']).sort_values(by="Date", ascending=False)
        return df

def running_ledger(transactions):
    ddict = defaultdict(list)
    for tr in transactions:
        if tr['category'] is not None:
            ddict['category'].append('-'.join(tr['category']))
        else:
            ddict['category'].append("")
        ddict['merchant_name'].append(tr['merchant_name'])
        ddict['name'].append(tr['name'])
        ddict['amount'].append(-tr['amount'])
        ddict['authorized_date'].append(tr['authorized_date'])
        ddict['date'].append(tr['date'])

    recent_df = pd.DataFrame(ddict)
    recent_df.date = pd.to_datetime(recent_df.date)

    df = pd.read_csv("./all_transactions.csv")
    df.date = pd.to_datetime(df.date)
    df = pd.concat((df, recent_df))
    df.drop_duplicates(inplace=True)
    df = df.sort_values(by='date', ascending=False)
    df.to_csv("./all_transactions.csv", index=False)

def transactions_to_df(transactions):
    """
    Process all transactions retrieved into a dataframe
    transactions: the transactions list retrieved from Plaid
    """
    dct = defaultdict(list)
    for tr in transactions:
        month, date, description, category, amount = process_transaction(tr)
        if description in SKIP_THESE or amount == -1500 or amount == 0: # for rent
            continue
        dct['Month'].append(month)
        dct['Date'].append(date)
        dct['Description'].append(description)
        dct['Category'].append(category)
        dct['Amount'].append(amount)

    df = pd.DataFrame(dct)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.date
    df.sort_values('Date', ascending=False, inplace=True)
    
    return df

def update_values(spreadsheet_id, range_name, value_input_option, sheet_values):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
        """
    # pylint: disable=maybe-no-member
    try:
        creds = google_credentials()
        service = build('sheets', 'v4', credentials=creds)
        body = {
            'values': sheet_values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def main(debug=False):
    # read data from googoo into df.
    current_sheet_df = get_googoo_df()
    
    # get last date.
    most_recent_date = current_sheet_df['Date'].values[0]
    
    # read data from plaid from that date or maybe that date minus one
    today = dt.now().date()
    trs = get_recent_transactions(most_recent_date, today)
    running_ledger(trs) # add to total ledger
    recent_transactions = transactions_to_df(trs)
    
    # add that data to df
    full_df = pd.concat((recent_transactions, current_sheet_df), axis=0)
    full_df.sort_values("Date", ascending=False, inplace=True)
    full_df = full_df[['Month', 'Date', 'Description', 'Category', 'Amount']]   # get the ordering right
    full_df.drop_duplicates(subset=['Date', 'Description', 'Amount'], inplace=True)
    full_df = add_rent(full_df, today)
    full_df.sort_values("Date", ascending=False, inplace=True)
    full_df['Date'] = full_df['Date'].apply(lambda x: x.strftime("%m-%d-%Y"))
    
    # write that whole mf to googoo
    if debug:
        print(full_df)
    else:
        update_values(SHEET_ID, TABLE_CELLS, "USER_ENTERED", full_df.values.tolist())

    return

if __name__ == '__main__':
    main(debug=False)
