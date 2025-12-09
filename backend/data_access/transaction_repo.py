import json
import os

from logic.aws_utils import read_transactions_s3, upload_transactions_s3
from logic.transaction_logic import map_json_transaction_to_transaction_entity, validate, custom_serializer, to_file_friendly
from models.Transaction import TransactionEntity
from typing import List

# Get the absolute path of this script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the path relative to the script's directory
TRANSACTION_FILE_PATH_LOCAL = os.path.join(BASE_DIR, "transactions.json")
TRANSACTION_FILE_NAME_S3 = "transactions.json"

def get_all_transactions() -> List[TransactionEntity]:
    raw_trs = read_transactions_s3(TRANSACTION_FILE_NAME_S3)
    return list(map(map_json_transaction_to_transaction_entity, raw_trs))

def get_all_transactions_local() -> List[TransactionEntity]:
    with open(TRANSACTION_FILE_PATH_LOCAL, 'r') as fp:
        transactions = json.load(fp)
        
    return list(map(map_json_transaction_to_transaction_entity, transactions))

def save_tranasctions(trs: List[TransactionEntity]) -> bool:
    return upload_transactions_s3(trs, TRANSACTION_FILE_NAME_S3)

def save_transactions_local(trs: List[TransactionEntity]) -> None:
    [validate(tr) for tr in trs]
    json_trs = [to_file_friendly(tr) for tr in trs]
    with open(TRANSACTION_FILE_PATH_LOCAL, 'w') as fp:
        json.dump(json_trs, fp, default=custom_serializer, indent=2)