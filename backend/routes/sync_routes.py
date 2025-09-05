from logic.transaction_logic import map_transaction_to_dto
from logic.sync_logic import plaid_sync
from flask import Blueprint

sync_bp = Blueprint("sync", __name__)

@sync_bp.route('/sync', methods=['POST'])
def sync_request():
    # call plaid sync
    transactions = plaid_sync()
    
    # map the transactions
    mapped_transactions = [map_transaction_to_dto(tr) for tr in transactions]
    
    # sort by date
    sorted_mapped_transactions = sorted(mapped_transactions, key=lambda x: x.date, reverse=True)
    
    return sorted_mapped_transactions