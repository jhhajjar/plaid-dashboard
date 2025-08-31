import json
import os

# Get the absolute path of this script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the path relative to the script's directory
TRANSACTION_FILE_PATH = os.path.join(BASE_DIR, "transactions.json")

def get_all_transactions():
    with open(TRANSACTION_FILE_PATH, 'r') as fp:
        transactions = json.load(fp)
        
    return transactions

def save_transactions(trs):
    json_trs = [vars(tr) for tr in trs]
    with open(TRANSACTION_FILE_PATH, 'w') as fp:
        json.dump(json_trs, fp, indent=2, default=str)