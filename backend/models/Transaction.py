from datetime import datetime
from enum import Enum


class TransactionCategory(str, Enum):
    FOOD='FOOD',
    GROCERIES='GROCERIES',
    SHOPPING='SHOPPING',
    MISC='MISC',
    INCOME='INCOME',
    HOUSING='HOUSING',
    TRANSPORTATION='TRANSPORTATION',
    INVESTING='INVESTING',
    FEE='FEE',
    ENTERTAINMENT='ENTERTAINMENT'
    

class TransactionDTO:
    date: datetime
    transaction_id: str
    merchant_name: str
    category: TransactionCategory
    amount: float
    
    def __init__(
        self,
        date,
        transaction_id,
        merchant_name,
        category,
        amount
    ):
        self.date = date
        self.transaction_id = transaction_id
        self.merchant_name = merchant_name
        self.category = category
        self.amount = amount
        
    def __str__(self):
        return str(vars(self))
    

class TransactionEntity:
    id: str
    account_id: str
    amount: float
    authorized_date: datetime
    authorized_datetime: datetime
    date: datetime
    datetime: datetime
    iso_currency_code: str
    logo_url: str
    merchant_entity_id: str
    merchant_name: str
    name: str
    payment_channel: str
    pending: bool
    transaction_code: str
    website: str
    address: str
    city: str
    country: str
    lat: str
    lon: str
    postal_code: str
    region: str
    category: str
    
    def __init__(self):
        pass
        
    def __str__(self):
        return str(vars(self))
    
    def to_csv_str(self):
        csv_string = ''
        dct = vars(self)
        for i in dct.keys():
            csv_string += f'{dct[i]},'