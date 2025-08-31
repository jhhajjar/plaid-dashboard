import os
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from logic.common import start_plaid, read_cursor, save_cursor
from plaid.api import plaid_api

from logic.transaction_logic import apply_additions, apply_updates, apply_deletions
from data_access.transaction_repo import get_all_transactions, save_transactions


def transaction_sync(plaid_client: plaid_api.PlaidApi, cursor: str = ""):
    """
    Calls transaction sync plaid endpoint
    """
    curr_cursor = cursor
    added = []
    modified = []
    removed = []
    has_more = True
    # Iterate through each page of new transaction updates for item
    while has_more:
        request = TransactionsSyncRequest(
            access_token=os.getenv('PLAID_ACCESS_TOKEN'),
            cursor=curr_cursor,
            count=500,
        )
        response = plaid_client.transactions_sync(request)
        # Add this page of results
        added.extend(response['added'])
        modified.extend(response['modified'])
        removed.extend(response['removed'])
        has_more = response['has_more']
        # Update cursor to the next cursor
        curr_cursor = response['next_cursor']

    return added, modified, removed, curr_cursor


def plaid_sync():
    """
    Initiates transaction sync, resolves updates, additions, and deletions, returns cleaned ledger
    """
    # start plaid
    client = start_plaid()

    # Call transaction sync
    cursor = read_cursor()
    added, modified, removed, new_cursor = transaction_sync(client, cursor)
    save_cursor(new_cursor)

    # apply updates
    transactions = get_all_transactions()
    transactions = apply_additions(transactions, added)
    transactions = apply_updates(transactions, modified)
    transactions = apply_deletions(transactions, removed)
    
    # write
    save_transactions(transactions)
    
    # return new transactions
    return transactions