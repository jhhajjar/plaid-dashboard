from datetime import datetime
from models.Transaction import TransactionDTO, TransactionEntity


def apply_additions(transactions, additions):
    transactions.extend(additions)
    return drop_duplicates(transactions)

def apply_updates(transactions, updates):
    return apply_additions(apply_deletions(transactions, updates), updates)

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

def get_merchant_name(tr) -> str:
    return tr['merchant_name'] if tr['merchant_name'] != None else tr['name']

def get_authorized_date(tr) -> datetime:
    return tr['authorized_date'] if tr['authorized_date'] != None else tr['date']

def map_plaid_category_to_app_category(category: str):
    return category.replace('_', ' ')

def map_transaction_to_dto(transaction: TransactionEntity) -> TransactionDTO:
    transaction_id = transaction.id
    merchant_name = get_merchant_name(transaction)
    date = get_authorized_date(transaction)
    category = map_plaid_category_to_app_category(transaction.category)
    amount = transaction.amount
    
    return TransactionDTO(
        date,
        transaction_id,
        merchant_name,
        category,
        amount
    )
    
def map_transaction_to_transaction_entity(tr) -> TransactionEntity:
    trEntity = TransactionEntity()
    trEntity.id = tr['transaction_id']
    trEntity.account_id = tr['account_id']
    trEntity.amount = tr['amount']
    trEntity.authorized_date = tr['authorized_date']
    trEntity.authorized_datetime = tr['authorized_datetime']
    trEntity.date = tr['date']
    trEntity.datetime = tr['datetime']
    trEntity.iso_currency_code = tr['iso_currency_code']
    trEntity.logo_url = tr['logo_url']
    trEntity.merchant_entity_id = tr['merchant_entity_id']
    trEntity.merchant_name = tr['merchant_name']
    trEntity.name = tr['name']
    trEntity.payment_channel = tr['payment_channel']
    trEntity.pending = tr['pending']
    trEntity.transaction_code = tr['transaction_code']
    trEntity.website = tr['website']
    
    trEntity.address = tr['location']['address']
    trEntity.city = tr['location']['city']
    trEntity.country = tr['location']['country']
    trEntity.lat = tr['location']['lat']
    trEntity.lon = tr['location']['lon']
    trEntity.postal_code = tr['location']['postal_code']
    trEntity.region = tr['location']['region']
    
    trEntity.category = tr['personal_finance_category']['detailed'] # TODO mapper
    
    return trEntity
    