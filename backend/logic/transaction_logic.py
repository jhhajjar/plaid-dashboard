from models.Transaction import TransactionDTO, TransactionEntity
from datetime import  datetime
from typing import List


def apply_filters(transactions: List[TransactionEntity], start: str, end: str) -> List[TransactionEntity]:
    start_datetime = datetime.strptime(start, '%Y-%m')
    end_datetime = datetime.strptime(end, '%Y-%m')
    return list(filter(lambda x: x.get_date() <= end_datetime and x.get_date() >= start_datetime, transactions))

def apply_additions(transactions: List[TransactionEntity], additions: List[TransactionEntity]):
    transactions.extend(additions)
    return drop_duplicates(transactions)

def apply_updates(transactions: List[TransactionEntity], updates: List[TransactionEntity]):
    return apply_additions(apply_deletions(transactions, updates), updates)

def apply_deletions(transactions: List[TransactionEntity], deletions: List[TransactionEntity]):
    keys_to_delete = [
        f"{tr['transaction_id']}{tr['account_id']}" for tr in deletions
    ]
    return [tr for tr in transactions if gen_key(tr) not in keys_to_delete]
    
def gen_key(transaction: TransactionEntity):
    return f"{transaction.id}{transaction.account_id}"

def drop_duplicates(transactions: List[TransactionEntity]):
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

def get_merchant_name(tr: TransactionEntity) -> str:
    return tr.merchant_name if tr.merchant_name != None else tr.name

def format_date(date: str | datetime) -> datetime:
    if type(date) == datetime:
        return date
    else:
        format_string = '%Y-%m-%d'
        return datetime.strptime(date, format_string)

def get_authorized_date(tr: TransactionEntity) -> datetime:
    date = tr.authorized_date if tr.authorized_date != None else tr.date
    formatted_date = format_date(date)
    return formatted_date

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
    
def map_plaid_transaction_to_transaction_entity(tr) -> TransactionEntity:
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

def map_json_transaction_to_transaction_entity(tr) -> TransactionEntity:
    entity = TransactionEntity()
    entity.id = tr['id']
    entity.account_id = tr['account_id']
    entity.amount = tr['amount']
    entity.authorized_date = tr['authorized_date']
    entity.authorized_datetime = tr['authorized_datetime']
    entity.date = tr['date']
    entity.datetime = tr['datetime']
    entity.iso_currency_code = tr['iso_currency_code']
    entity.logo_url = tr['logo_url']
    entity.merchant_entity_id = tr['merchant_entity_id']
    entity.merchant_name = tr['merchant_name']
    entity.name = tr['name']
    entity.payment_channel = tr['payment_channel']
    entity.pending = tr['pending']
    entity.transaction_code = tr['transaction_code']
    entity.website = tr['website']
    
    entity.address = tr['address']
    entity.city = tr['city']
    entity.country = tr['country']
    entity.lat = tr['lat']
    entity.lon = tr['lon']
    entity.postal_code = tr['postal_code']
    entity.region = tr['region']
    
    entity.category = tr['category']
    
    # Convert dates correctly
    if entity.authorized_date is not None:
        entity.authorized_date = format_date(entity.authorized_date)
    if entity.authorized_datetime is not None:
        entity.authorized_datetime = format_date(entity.authorized_datetime)
    if entity.date is not None:
        entity.date = format_date(entity.date)
    if entity.datetime is not None:
        entity.datetime = format_date(entity.datetime)
    
    return entity