import sys
import os
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.Transaction import TransactionEntity


def create_mock_transaction_entity(
    id: str,
    account_id: str,
    amount: float,
    plaid_amount: float = None,
    date: str = None,
    authorized_date: str = None,
    merchant_name: str = None,
    name: str = "Test Transaction",
    category: str = "GENERAL_MERCHANDISE_OTHER_GENERAL_MERCHANDISE",
) -> TransactionEntity:
    """Create a mock TransactionEntity for testing."""
    tr = TransactionEntity()
    tr.id = id
    tr.account_id = account_id
    tr.amount = amount
    tr.plaid_amount = plaid_amount if plaid_amount is not None else -amount
    tr.date = date
    tr.authorized_date = authorized_date
    tr.authorized_datetime = None
    tr.datetime = None
    tr.iso_currency_code = "USD"
    tr.logo_url = None
    tr.merchant_entity_id = None
    tr.merchant_name = merchant_name
    tr.name = name
    tr.payment_channel = "other"
    tr.pending = False
    tr.transaction_code = None
    tr.website = None
    tr.address = None
    tr.city = None
    tr.country = None
    tr.lat = None
    tr.lon = None
    tr.postal_code = None
    tr.region = None
    tr.category = category
    return tr


def create_plaid_transaction(
    transaction_id: str,
    account_id: str,
    amount: float,
    date: str = "2025-08-22",
    authorized_date: str = "2025-08-22",
    merchant_name: str = "Test Merchant",
    name: str = "Test Transaction",
    category: str = "GENERAL_MERCHANDISE_OTHER_GENERAL_MERCHANDISE",
    address: str = None,
    city: str = None,
    country: str = None,
    lat: float = None,
    lon: float = None,
    postal_code: str = None,
    region: str = None,
) -> Dict[str, Any]:
    """
    Create a mock Plaid transaction in the format returned by Plaid's API.
    Note: Plaid uses 'transaction_id' and nested 'location' and 'personal_finance_category'.
    """
    return {
        "transaction_id": transaction_id,
        "account_id": account_id,
        "amount": amount,
        "authorized_date": authorized_date,
        "authorized_datetime": None,
        "date": date,
        "datetime": None,
        "iso_currency_code": "USD",
        "logo_url": None,
        "merchant_entity_id": None,
        "merchant_name": merchant_name,
        "name": name,
        "payment_channel": "other",
        "pending": False,
        "transaction_code": None,
        "website": None,
        "location": {
            "address": address,
            "city": city,
            "country": country,
            "lat": lat,
            "lon": lon,
            "postal_code": postal_code,
            "region": region,
        },
        "personal_finance_category": {
            "detailed": category,
            "primary": category.split("_")[0] if category else None,
        },
    }


# Mock Plaid transactions in the format returned by Plaid's transactions_sync API
mock_plaid_transactions: List[Dict[str, Any]] = [
    create_plaid_transaction(
        transaction_id="plaid_txn_001",
        account_id="acc_001",
        amount=245.0,  # Plaid uses positive for debits
        date="2025-08-22",
        authorized_date="2025-08-22",
        merchant_name="Robinhood",
        name="Robinhood",
        category="GENERAL_MERCHANDISE_OTHER_GENERAL_MERCHANDISE",
    ),
    create_plaid_transaction(
        transaction_id="plaid_txn_002",
        account_id="acc_002",
        amount=50.0,
        date="2025-08-21",
        authorized_date="2025-08-21",
        merchant_name="Whole Foods",
        name="Whole Foods Market",
        category="FOOD_AND_DRINK_GROCERIES",
    ),
    create_plaid_transaction(
        transaction_id="plaid_txn_003",
        account_id="acc_001",
        amount=343.0,
        date="2025-08-20",
        authorized_date="2025-08-20",
        merchant_name="Uber",
        name="Uber Trip",
        category="TRANSPORTATION_TAXIS_AND_RIDE_SHARES",
    ),
    create_plaid_transaction(
        transaction_id="plaid_txn_004",
        account_id="acc_002",
        amount=13.0,
        date="2025-08-19",
        authorized_date="2025-08-19",
        merchant_name="Netflix",
        name="Netflix Subscription",
        category="ENTERTAINMENT_TV_AND_MOVIES",
    ),
    create_plaid_transaction(
        transaction_id="plaid_txn_005",
        account_id="acc_003",
        amount=154.0,
        date="2025-08-18",
        authorized_date="2025-08-18",
        merchant_name="Transfer",
        name="Account Transfer",
        category="TRANSFER_OUT_ACCOUNT_TRANSFER",
    ),
    create_plaid_transaction(
        transaction_id="plaid_txn_006",
        account_id="acc_001",
        amount=66.0,
        date="2025-08-15",
        authorized_date="2025-08-15",
        merchant_name="Fidelity",
        name="Investment Transfer",
        category="TRANSFER_OUT_INVESTMENT_AND_RETIREMENT_FUNDS",
    ),
    create_plaid_transaction(
        transaction_id="plaid_txn_007",
        account_id="acc_001",
        amount=-600.99,  # Plaid uses negative for credits/income
        date="2025-08-15",
        authorized_date="2025-08-15",
        merchant_name=None,
        name="DIR DEP PAYROLL",
        category="INCOME_WAGES",
    ),
]

# Mock transactions already in internal TransactionEntity format (for existing transaction lists)
mock_existing_transactions: List[TransactionEntity] = [
    create_mock_transaction_entity(
        id="existing_txn_001",
        account_id="acc_001",
        amount=-100.0,
        plaid_amount=100.0,
        date="2025-08-10",
        authorized_date="2025-08-10",
        merchant_name="Amazon",
        name="Amazon.com",
        category="GENERAL_MERCHANDISE_ONLINE_MARKETPLACES",
    ),
    create_mock_transaction_entity(
        id="existing_txn_002",
        account_id="acc_002",
        amount=-75.50,
        plaid_amount=75.50,
        date="2025-08-09",
        authorized_date="2025-08-09",
        merchant_name="Target",
        name="Target",
        category="GENERAL_MERCHANDISE_SUPERSTORES",
    ),
]

# Duplicate transaction (same id and account_id as existing)
mock_duplicate_plaid_transaction: Dict[str, Any] = create_plaid_transaction(
    transaction_id="existing_txn_001",  # Same as existing
    account_id="acc_001",  # Same as existing
    amount=999.0,  # Different amount
    date="2025-08-22",
    authorized_date="2025-08-22",
    merchant_name="Duplicate Merchant",
    name="Duplicate Transaction",
    category="GENERAL_MERCHANDISE_OTHER_GENERAL_MERCHANDISE",
)

# Transaction with location data
mock_plaid_transaction_with_location: Dict[str, Any] = create_plaid_transaction(
    transaction_id="plaid_txn_location",
    account_id="acc_001",
    amount=45.00,
    date="2025-08-22",
    authorized_date="2025-08-22",
    merchant_name="Starbucks",
    name="Starbucks Coffee",
    category="FOOD_AND_DRINK_COFFEE",
    address="123 Main St",
    city="San Francisco",
    country="US",
    lat=37.7749,
    lon=-122.4194,
    postal_code="94102",
    region="CA",
)
