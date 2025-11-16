import datetime
import json
import os

from typing import List
from logic.transaction_logic import map_json_transaction_to_transaction_entity, validate
from models.Transaction import TransactionEntity

# Get the absolute path of this script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the path relative to the script's directory
TRANSACTION_FILE_PATH = os.path.join(BASE_DIR, "transactions.json")

def get_all_transactions() -> List[TransactionEntity]:
    with open(TRANSACTION_FILE_PATH, 'r') as fp:
        transactions = json.load(fp)
        
    return list(map(map_json_transaction_to_transaction_entity, transactions))

def custom_serializer(obj) -> str:
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def save_transactions(trs: List[TransactionEntity]) -> None:
    [validate(tr) for tr in trs]
    json_trs = [to_file_friendly(tr) for tr in trs]
    with open(TRANSACTION_FILE_PATH, 'w') as fp:
        json.dump(json_trs, fp, default=custom_serializer, indent=2)
        
def to_file_friendly(tr: TransactionEntity) -> dict:
    if(type(tr) == dict):
        return tr
    return vars(tr)