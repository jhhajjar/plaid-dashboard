from flask import Blueprint, jsonify, request

from logic.sync_logic import plaid_sync
from logic.transaction_logic import map_transaction_to_dto

sync_bp = Blueprint("sync", __name__)

@sync_bp.route('/sync', methods=['POST'])
def sync_request():
    # call plaid sync
    transactions = plaid_sync()
    print(transactions[0])
    print(set([tr['account_id'] for tr in transactions]))
    
    transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
    
    mapped = [map_transaction_to_dto(tr) for tr in transactions]
    
    return mapped