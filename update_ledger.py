import plaid
import pandas as pd
import numpy as np
import os.path
import json
import os
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.transactions_get_request import TransactionsGetRequest
from collections import defaultdict
from plaid.api import plaid_api
from datetime import datetime as dt
from argparse import ArgumentParser
from dotenv import load_dotenv

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
            'clientId': os.getenv("CLIENT_ID"),
            'secret': os.getenv("SECRET"),
        }
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    return client


def get_recent_transactions(start, end):
    """
    Retrieve all transactions between two dates
    start: start date (datetime.date)
    end: end date (datetime.date)

    Returns a list of json objects of transactions
    """
    client = start_plaid()

    request = TransactionsGetRequest(
        access_token=os.getenv('ACCESS_TOKEN'),
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
            access_token=os.getenv('ACCESS_TOKEN'),
            start_date=start,
            end_date=end,
            options=options
        )
        response = client.transactions_get(request)
        transactions += response['transactions']

    return transactions


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


def raw_ledger(transactions):
    """
    Returns a 'raw', un-categorized ledger to 'raw_ledger.csv'

    TODO: maybe there are  optimizations that can be done here
    """
    ddict = defaultdict(list)
    for tr in transactions:
        ddict['date'].append(tr['date'])
        ddict['authorized_date'].append(tr['authorized_date'])
        ddict['transaction_id'].append(tr['transaction_id'])
        ddict['name'].append(tr['name'])
        ddict['merchant_name'].append(tr['merchant_name'])

        if tr['category'] is not None:
            ddict['plaid_categories'].append('-'.join(tr['category']))
        else:
            ddict['plaid_categories'].append("")
        ddict['amount'].append(-tr['amount'])

    recent_df = pd.DataFrame(ddict)
    recent_df['authorized_date'].fillna(recent_df['date'])

    df = pd.read_csv("./raw_ledger.csv")
    curr_num_transactions = df.shape[0]
    df = pd.concat((df, recent_df))
    df.drop_duplicates(subset=['transaction_id'], inplace=True)
    new_transactions = df.shape[0] - curr_num_transactions
    if new_transactions > 0:
        df['date'] = pd.to_datetime(
            df['date'], format="%Y-%m-%d", errors='coerce').dt.date
        df['authorized_date'] = pd.to_datetime(
            df['authorized_date'], format="%Y-%m-%d", errors='coerce').dt.date

        df.sort_values(by='authorized_date', inplace=True, ascending=False)
        return df, new_transactions
    else:
        return False, 0


def clean_ledger(transactions) -> None:
    """
    Cleans up the categories from the plaid transactions api

    transactions: pd.DataFrame, created by raw_ledger
    """
    transactions['category'] = transactions.apply(categorize, axis=1)
    transactions = transactions[
        ["date", "authorized_date", "transaction_id", "name", "merchant_name", "plaid_categories", "category", "amount"]]

    return transactions


def main(args):
    debug = args.debug
    if debug:
        print("WE ARE IN DEBUG MODE BABY")

    load_dotenv()

    # read the .date file to find out where to start analysis
    date_str = open('.date', 'r').read()
    start_date = dt.strptime(date_str, '%Y-%m-%d').date()
    now = dt.now()
    end_date = now.date()

    # get the recent transactions
    transactions = get_recent_transactions(start_date, end_date)
    if len(transactions) == 0:
        print(f"{now}: No new transactions.")
        return

    # save to raw ledger, keep in memory
    raw_transactions, num_new = raw_ledger(transactions)
    if num_new > 0:
        raw_transactions.to_csv('./raw_ledger.csv', index=False)
        # categorize each transaction
        clean_transactions = clean_ledger(raw_transactions)
        clean_transactions.to_csv('./clean_ledger.csv', index=False)

        print(f"{now}: Added {num_new} new transactions.")
    else:
        print(f"{now}: No new transactions.")

    open('.date', 'w').write(end_date.strftime('%Y-%m-%d'))


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('--debug', action='store_true')
    args = ap.parse_args()
    main(args)
