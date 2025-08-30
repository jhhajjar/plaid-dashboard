from flask import Blueprint, jsonify, request

from backend.logic.sync_logic import plaid_sync

sync_bp = Blueprint("sync", __name__)

@sync_bp.route('/sync', methods=['POST'])
def sync_request():
    # call plaid sync
    updates = plaid_sync()
    
    # get newest shit

    # return that bitch