import json


TRANSACTION_FILE_PATH = './transaction.json'

def get_all_transactions():
    with open(TRANSACTION_FILE_PATH, 'r') as fp:
        transactions = json.load(fp)
        
    return transactions