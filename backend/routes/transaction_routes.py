from logic.transaction_logic import map_transaction_to_dto, apply_filters
from logic.sync_logic import plaid_sync
from flask import Blueprint, request

transactions_bp = Blueprint("transactions", __name__)

@transactions_bp.route('/', methods=['GET'])
def get_transactions():
    start = request.args.get('start')
    end = request.args.get('end')
    
    # get transactions
    transactions = plaid_sync()
    filtered_transactions = apply_filters(transactions, start, end)
    
    # map the transactions
    mapped_transactions = [map_transaction_to_dto(tr) for tr in filtered_transactions]
    
    # sort by date
    sorted_mapped_transactions = sorted(mapped_transactions, key=lambda x: x.date, reverse=True)
    
    return sorted_mapped_transactions