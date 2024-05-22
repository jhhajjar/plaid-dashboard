import plaid
import pandas as pd
import os.path
import json
import os
import boto3
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from collections import defaultdict
from plaid.api import plaid_api
from datetime import datetime as dt
from argparse import ArgumentParser
from dotenv import load_dotenv
from aws_utils import upload_file_s3, read_file_s3, COLUMNS
from io import StringIO

SKIP_THESE = {
    "Recurring Automatic Payment",
    "TD BANK PAYMENT",
    "TD BANK"
}


def start_plaid():
    """"
    Starts plaid client
    """
    configuration = plaid.Configuration(
        host=plaid.Environment.Development,
        api_key={
            'clientId': os.getenv("CLIENT_ID"),
            'secret': os.getenv("SECRET"),
        }
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    return client


def get_recent_transactions(cursor=None):
    """
    Retrieve all transactions between two dates
    start: start date (datetime.date)
    end: end date (datetime.date)

    Returns a list of json objects of transactions
    """
    client = start_plaid()

    # New transaction updates since "cursor"
    added = []
    modified = []
    removed = []  # Removed transaction ids
    has_more = True
    # Iterate through each page of new transaction updates for item
    while has_more:
        request = TransactionsSyncRequest(
            access_token=os.getenv('ACCESS_TOKEN'),
            cursor=cursor,
        )
        response = client.transactions_sync(request)
        # Add this page of results
        added.extend(response['added'])
        modified.extend(response['modified'])
        removed.extend(response['removed'])
        has_more = response['has_more']
        # Update cursor to the next cursor
        cursor = response['next_cursor']

    return [added, modified, removed], cursor


def categorize(trans_row):
    """
    Categorize a trans_rowansaction based on the mappings.json file

    trans_row: row in raw ledger
    """

    with open('./mappings.json', 'r') as fp:
        mappings = json.load(fp)

    if trans_row['merchant_name'] is not None:
        name = f"{trans_row['name']},{trans_row['merchant_name']}"
    else:
        name = trans_row['name']

    if isinstance(trans_row['plaid_categories'], str):
        # check categories
        for key in mappings['category_map']:
            if key in trans_row['plaid_categories']:
                return mappings['category_map'][key]

    # check name
    for key in mappings['name_map']:
        if key.lower() in name.lower():
            return mappings['name_map'][key]

    # couldn't categorize
    return "Misc"


def tr_list_to_df(tr_list):
    ddict = defaultdict(list)
    for tr in tr_list:
        ddict['date'].append(tr['date'])
        ddict['transaction_id'].append(tr['transaction_id'])
        ddict['name'].append(tr['name'])

        merchant_name = tr['merchant_name'] if tr['merchant_name'] != None else tr['name']
        authorized_date = tr['authorized_date'] if tr['authorized_date'] != None else tr['date']
        ddict['merchant_name'].append(merchant_name)
        ddict['authorized_date'].append(authorized_date)

        if tr['category'] is not None:
            ddict['plaid_categories'].append('-'.join(tr['category']))
        else:
            ddict['plaid_categories'].append("")
        ddict['amount'].append(-tr['amount'])

    tr_df = pd.DataFrame(ddict)
    tr_df['authorized_date'].fillna(tr_df['date'])

    return tr_df


def append_to_raw_ledger(raw_ledger: pd.DataFrame, sync_response: list):
    """
    Adds the new transactions to a 'raw', un-categorized ledger
    Returns the new full raw ledger, and a list with [additions, mods, deletions] 
    """
    num_additions = 0
    num_modifications = 0
    num_deletions = 0

    # First time creating raw ledger, only going to have additions
    if raw_ledger.shape[0] == 0:
        raw_ledger = tr_list_to_df(sync_response[0])
        num_additions = len(sync_response[0])
    else:
        # deal with additions
        if len(sync_response[0]) != 0:
            recent_df = tr_list_to_df(sync_response[0])
            raw_ledger = pd.concat((raw_ledger, recent_df))
            num_additions = len(sync_response[0])

        # deal with modifications [delete and then add modified]
        if len(sync_response[1]) != 0:
            to_delete = [tr['transaction_id'] for tr in sync_response[1]]
            raw_ledger = raw_ledger[~raw_ledger['transaction_id'].isin(
                to_delete)]
            modified_df = tr_list_to_df(sync_response[0])
            raw_ledger = pd.concat((raw_ledger, modified_df))
            num_modifications = len(sync_response[1])

        # deal with deletions
        if len(sync_response[2]) != 0:
            to_delete = [tr['transaction_id'] for tr in sync_response[2]]
            raw_ledger = raw_ledger[~raw_ledger['transaction_id'].isin(
                to_delete)]
            num_deletions = len(sync_response[2])

    updates = [num_additions, num_modifications, num_deletions]

    # format dates
    raw_ledger['date'] = pd.to_datetime(
        raw_ledger['date'], format="%Y-%m-%d", errors='coerce').dt.date
    raw_ledger['authorized_date'] = pd.to_datetime(
        raw_ledger['authorized_date'], format="%Y-%m-%d", errors='coerce').dt.date

    raw_ledger.sort_values(by='authorized_date', inplace=True, ascending=False)
    raw_ledger = raw_ledger.drop_duplicates(subset="transaction_id")
    raw_ledger = raw_ledger[COLUMNS]

    return raw_ledger, updates


def clean_ledger(transactions) -> None:
    """
    Cleans up the categories from the plaid transactions api

    transactions: pd.DataFrame, created by raw_ledger
    """
    transactions['category'] = transactions.apply(categorize, axis=1)
    transactions = transactions[
        ["date", "authorized_date", "transaction_id", "name", "merchant_name", "plaid_categories", "category", "amount"]]

    return transactions


def is_sync_response_empty(response):
    """
    response is a 2d array of [added, modified, removed]
    """
    for arr in response:
        if len(arr) != 0:
            return False

    return True


def main(args):
    debug = args.debug
    if debug:
        print("WE ARE IN DEBUG MODE BABY")

    load_dotenv()
    now = dt.now()

    # get cursor if it exists
    try:
        cursor = open('.cursor', 'r').read()
        first_write = False
    except:
        cursor = ""
        first_write = True

    # get the recent transactions
    sync_transactions_response, cursor = get_recent_transactions(cursor)

    # save cursor
    if not debug:
        open('.cursor', 'w').write(cursor)

    # determine if there is anything else to do
    if is_sync_response_empty(sync_transactions_response):
        print(f"{now}: No new updates.")
        return

    # save to raw ledger, keep in memory
    if first_write:
        curr_raw_ledger = pd.DataFrame()
    else:
        curr_raw_ledger = read_file_s3("raw_ledger.csv")

    raw_transactions, updates = append_to_raw_ledger(
        curr_raw_ledger, sync_transactions_response)
    if not debug:
        upload_file_s3(raw_transactions, "raw_ledger.csv")

        # categorize each transaction
        clean_transactions = clean_ledger(raw_transactions)
        upload_file_s3(clean_transactions, "clean_ledger.csv")
    else:
        raw_transactions.to_csv('./DEBUG_raw_ledger.csv', index=False)

    print(
        f"{now}: Added {updates[0]}, Modified {updates[1]}, Deleted {updates[2]}")


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('--debug', action='store_true')
    args = ap.parse_args()
    main(args)
