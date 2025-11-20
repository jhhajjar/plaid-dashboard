from dataclasses import dataclass
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
    SELF_IMPROVEMENT='SELF_IMPROVEMENT',
    TRAVEL='TRAVEL',
    FEE='FEE',
    ENTERTAINMENT='ENTERTAINMENT'
    
    
@dataclass
class TransactionDTO:
    date: datetime
    transactionId: str
    merchantName: str
    category: TransactionCategory
    amount: float
    includeInCalc: bool
    
    def __init__(
        self,
        date,
        transaction_id,
        merchant_name,
        category,
        amount
    ):
        self.date = date
        self.transactionId = transaction_id
        self.merchantName = merchant_name
        self.category = category
        self.amount = amount
        self.includeInCalc = True
        
    def __str__(self):
        return str(vars(self))
    

class TransactionEntity:
    id: str
    account_id: str
    amount: float
    plaid_amount: float
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
            
    def get_date(self):
        return self.authorized_date if self.authorized_date is not None else self.date