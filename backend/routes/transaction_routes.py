from data_access.transaction_repo import get_all_transactions
from logic.transaction_logic import map_transaction_to_dto, apply_filters
from flask import Blueprint, request, jsonify

transactions_bp = Blueprint("transactions", __name__)

@transactions_bp.route('/', methods=['GET'])
def get_transactions():
    start = request.args.get('start')
    end = request.args.get('end')
    
    # get transactions
    transactions = get_all_transactions()
    filtered_transactions = apply_filters(transactions, start, end)
    
    # map the transactions
    mapped_transactions = [map_transaction_to_dto(tr) for tr in filtered_transactions]
    
    # sort by date
    sorted_mapped_transactions = sorted(mapped_transactions, key=lambda x: x.date, reverse=True)
    
    return jsonify(sorted_mapped_transactions)