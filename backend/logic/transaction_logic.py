def apply_additions(transactions, additions):
    transactions.extend(additions)
    return drop_duplicates(transactions)

def apply_updates(transactions, updates):
    updated_transactions = []
    update_hashes = [gen_key(tr) for tr in updates]
    
    for tr in transactions:
        if gen_key(tr) in update_hashes:
            # this is a stale transaction, do not append
            continue
        else:
            updated_transactions.append(tr)
            
    return apply_additions(updated_transactions, updates)

def apply_deletions(transactions, deletions):
    keys_to_delete = [
        f"{tr['transaction_id']}{tr['account_id']}" for tr in deletions
    ]
    return [tr for tr in transactions if gen_key(tr) not in keys_to_delete]
    
def gen_key(transaction):
    return f"{transaction['transaction_id']}{transaction['account_id']}"

def drop_duplicates(transactions):
    de_duped_transactions = []
    seen_pairs = set()
    
    # Add transactions to new array if the id and account pair 
    for tr in transactions:
        key = gen_key(tr)
        
        if key in seen_pairs:
            continue
        else:
            de_duped_transactions.append(tr)
            seen_pairs.add(key)
            
    return de_duped_transactions