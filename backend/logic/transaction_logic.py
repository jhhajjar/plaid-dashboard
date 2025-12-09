import calendar
from models.Transaction import TransactionCategory, TransactionDTO, TransactionEntity
from datetime import  datetime
from typing import List


def apply_filters(transactions: List[TransactionEntity], start: str, end: str) -> List[TransactionEntity]:
    start_datetime = datetime.strptime(start, '%Y-%m')
    end_datetime = datetime.strptime(end, '%Y-%m')
    last_day_of_month = calendar.monthrange(end_datetime.year, end_datetime.month)[1]
    end_datetime = end_datetime.replace(day=last_day_of_month)
    return list(filter(lambda x: x.get_date() <= end_datetime and x.get_date() >= start_datetime, transactions))

def apply_additions(transactions: List[TransactionEntity], additions: List[TransactionEntity]) -> List[TransactionEntity]:
    transactions.extend(additions)
    return drop_duplicates(transactions)

def apply_updates(transactions: List[TransactionEntity], updates: List[TransactionEntity]) -> List[TransactionEntity]:
    to_delete = [{"transaction_id": tr.id, "account_id": tr.account_id} for tr in updates]
    return apply_additions(apply_deletions(transactions, to_delete), updates)

def apply_deletions(transactions: List[TransactionEntity], deletions: List[dict]) -> List[TransactionEntity]:
    keys_to_delete = [
        f"{tr['transaction_id']}{tr['account_id']}" for tr in deletions
    ]
    return [tr for tr in transactions if gen_key(tr) not in keys_to_delete]
    
def gen_key(transaction: TransactionEntity) -> str:
    return f"{transaction.id}{transaction.account_id}"

def drop_duplicates(transactions: List[TransactionEntity]) -> List[TransactionEntity]:
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
        # sometimes these come in with the time
        if len(date) == 19:
            format_string = '%Y-%m-%dT00:00:00'
            return datetime.strptime(date, format_string)
        elif len(date) == 10:
            format_string = '%Y-%m-%d'
            return datetime.strptime(date, format_string)

def get_authorized_date(tr: TransactionEntity) -> datetime:
    date = tr.authorized_date if tr.authorized_date != None else tr.date
    formatted_date = format_date(date)
    return formatted_date

def validate(tr: TransactionEntity) -> None:
    """
    Validates transaction entity before saving
    """
    if tr.amount != transform_amount(tr):
        raise ValueError(f"Transaction {tr.id} has amount {tr.amount} not equal to transformed plaid amount {transform_amount(tr)}")

def transform_amount(transaction: TransactionEntity) -> float:
    return -transaction.plaid_amount

def map_plaid_category_to_app_category(category: str) -> str:
    """
    Maps a detailed Plaid category string to a simplified application category.

    Args:
        category: The raw Plaid category string (e.g., 'FOOD_AND_DRINK_RESTAURANT').

    Returns:
        The simplified TransactionCategory value (e.g., 'FOOD').
    """
    
    # 1. INCOME
    if category in {
        'INCOME_WAGES',
        'INCOME_INTEREST_EARNED',
        'INCOME_TAX_REFUND',
    }:
        return TransactionCategory.INCOME
        
    # 2. FEES (Bank Fees)
    elif category in {
        'BANK_FEES_FOREIGN_TRANSACTION_FEES',
        'BANK_FEES_ATM_FEES',
        'BANK_FEES_OTHER_BANK_FEES',
        'BANK_FEES_INTEREST_CHARGE',
    }:
        return TransactionCategory.FEE

    # 3. GROCERIES
    elif category in {
        'FOOD_AND_DRINK_GROCERIES',
        'GENERAL_MERCHANDISE_SUPERSTORES', # Often includes significant grocery purchases
    }:
        return TransactionCategory.GROCERIES

    # 4. FOOD (Dining, Coffee, Alcohol, Fast Food)
    elif category in {
        'FOOD_AND_DRINK_RESTAURANT',
        'FOOD_AND_DRINK_OTHER_FOOD_AND_DRINK',
        'FOOD_AND_DRINK_BEER_WINE_AND_LIQUOR',
        'FOOD_AND_DRINK_COFFEE',
        'FOOD_AND_DRINK_VENDING_MACHINES',
        'FOOD_AND_DRINK_FAST_FOOD',
    }:
        return TransactionCategory.FOOD

    # 5. SHOPPING (General Merchandise, Clothing, Personal Care)
    elif category in {
        'GENERAL_MERCHANDISE_OTHER_GENERAL_MERCHANDISE',
        'GENERAL_MERCHANDISE_CLOTHING_AND_ACCESSORIES',
        'GENERAL_MERCHANDISE_SPORTING_GOODS',
        'GENERAL_MERCHANDISE_CONVENIENCE_STORES',
        'GENERAL_MERCHANDISE_ONLINE_MARKETPLACES',
        'GENERAL_MERCHANDISE_PET_SUPPLIES',
        'GENERAL_MERCHANDISE_BOOKSTORES_AND_NEWSSTANDS',
        'GENERAL_MERCHANDISE_TOBACCO_AND_VAPE',
        'GENERAL_MERCHANDISE_GIFTS_AND_NOVELTIES',
        'GENERAL_MERCHANDISE_ELECTRONICS',
        'GENERAL_MERCHANDISE_DISCOUNT_STORES',
        'GENERAL_MERCHANDISE_DEPARTMENT_STORES',
        'HOME_IMPROVEMENT_HARDWARE',
        'HOME_IMPROVEMENT_FURNITURE',
    }:
        return TransactionCategory.SHOPPING

    # 6. ENTERTAINMENT
    elif category in {
        'ENTERTAINMENT_TV_AND_MOVIES',
        'ENTERTAINMENT_SPORTING_EVENTS_AMUSEMENT_PARKS_AND_MUSEUMS',
        'ENTERTAINMENT_OTHER_ENTERTAINMENT',
        'ENTERTAINMENT_CASINOS_AND_GAMBLING',
        'ENTERTAINMENT_VIDEO_GAMES',
        'ENTERTAINMENT_MUSIC_AND_AUDIO',
    }:
        return TransactionCategory.ENTERTAINMENT

    # 7. HOUSING/UTILITIES
    elif category in {
        'RENT_AND_UTILITIES_GAS_AND_ELECTRICITY',
        'RENT_AND_UTILITIES_TELEPHONE',
        'RENT_AND_UTILITIES_RENT',
    }:
        return TransactionCategory.HOUSING

    # 8. TRANSPORTATION
    elif category in {
        'TRANSPORTATION_GAS',
        'TRANSPORTATION_TAXIS_AND_RIDE_SHARES',
        'TRANSPORTATION_PARKING',
        'TRANSPORTATION_PUBLIC_TRANSIT',
        'TRANSPORTATION_OTHER_TRANSPORTATION',
        'GENERAL_SERVICES_AUTOMOTIVE',
        # TRAVEL
        'TRAVEL_FLIGHTS',
        'TRAVEL_LODGING',
        'TRAVEL_OTHER_TRAVEL',
        'TRAVEL_RENTAL_CARS', # Treating this as transport cost
    }:
        return TransactionCategory.TRANSPORTATION

    # 9. INVESTING/LOANS/DEBT
    elif category in {
        'TRANSFER_OUT_INVESTMENT_AND_RETIREMENT_FUNDS',
        'LOAN_PAYMENTS_CREDIT_CARD_PAYMENT',
        'LOAN_PAYMENTS_PERSONAL_LOAN_PAYMENT',
    }:
        return TransactionCategory.INVESTING
    
    # 10. SELF_IMPROVEMENT (Health, Medical, Personal Care)
    elif category in {
        'PERSONAL_CARE_GYMS_AND_FITNESS_CENTERS',
        'PERSONAL_CARE_HAIR_AND_BEAUTY',
        'PERSONAL_CARE_OTHER_PERSONAL_CARE',
        'PERSONAL_CARE_LAUNDRY_AND_DRY_CLEANING',
        # HEALTH & MEDICAL
        'MEDICAL_OTHER_MEDICAL',
        'MEDICAL_PHARMACIES_AND_SUPPLEMENTS',
        'MEDICAL_DENTAL_CARE',
    }:
        return TransactionCategory.SELF_IMPROVEMENT
    
    # 11. TRAVEL
    elif category in {
        'TRAVEL_FLIGHTS',
        'TRAVEL_LODGING',
        'TRAVEL_OTHER_TRAVEL',
        'TRAVEL_RENTAL_CARS',
    }:
        return TransactionCategory.TRAVEL

    # 12. MISC (Medical, Travel, Transfers, Services, Government, Personal Care)
    # Catch-all for everything that doesn't fit neatly into the main buckets.
    elif category in {
        # SERVICES
        'GENERAL_SERVICES_OTHER_GENERAL_SERVICES',
        'GENERAL_SERVICES_POSTAGE_AND_SHIPPING',
        'GENERAL_SERVICES_EDUCATION',
        'GENERAL_SERVICES_ACCOUNTING_AND_FINANCIAL_PLANNING',
        # GOVERNMENT/DONATIONS
        'GOVERNMENT_AND_NON_PROFIT_DONATIONS',
        'GOVERNMENT_AND_NON_PROFIT_GOVERNMENT_DEPARTMENTS_AND_AGENCIES',
        # TRANSFERS (Usually handled by Plaid as not income/expense, but categorized here for completeness)
        'TRANSFER_OUT_ACCOUNT_TRANSFER',
        'TRANSFER_IN_ACCOUNT_TRANSFER',
        'TRANSFER_OUT_WITHDRAWAL',
        'TRANSFER_IN_DEPOSIT',
        'TRANSFER_OUT_OTHER_TRANSFER_OUT',
    }:
        return TransactionCategory.MISC
        
    # Default for any new or uncategorized Plaid items
    else:
        print('Unmapped category:', category)
        return TransactionCategory.MISC
        
def to_file_friendly(tr: TransactionEntity) -> dict:
    if(type(tr) == dict):
        return tr
    return vars(tr)

def custom_serializer(obj) -> str:
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

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
    trEntity.plaid_amount = tr['amount']
    trEntity.amount = transform_amount(trEntity)
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
    entity.plaid_amount = tr['plaid_amount']
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