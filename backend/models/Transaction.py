import json
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
    

class Transaction:
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