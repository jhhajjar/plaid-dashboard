import unittest
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.Transaction import TransactionEntity

from logic.transaction_logic import (
    gen_key,
    drop_duplicates,
    apply_additions,
    apply_updates,
    apply_deletions
)

def create_transaction_mock(id, account_id, amount):
    tr = TransactionEntity()
    tr.id = id
    tr.account_id = account_id
    tr.amount = amount
    
    return tr


class TestTransactionLogic(unittest.TestCase):
    
    def test_drop_duplicates(self):
        transactions = [
            create_transaction_mock("txn1", "acc1", 100),
            create_transaction_mock("txn2", "acc2", 200),
            create_transaction_mock("txn1", "acc1", 150),  # duplicate key
            create_transaction_mock("txn3", "acc3", 300),
        ]
        
        result = drop_duplicates(transactions)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].id, 'txn1')
        self.assertEqual(result[0].amount, 100)  # keeps first occurrence
        self.assertEqual(result[1].id, 'txn2')
        self.assertEqual(result[2].id, 'txn3')
        
    def test_drop_duplicates_empty_list(self):
        result = drop_duplicates([])
        self.assertEqual(result, [])
        
    def test_drop_duplicates_no_duplicates(self):
        transactions = [
            create_transaction_mock("txn1", "acc1", 100),
            create_transaction_mock("txn2", "acc2", 200),
        ]
        result = drop_duplicates(transactions)
        self.assertEqual(result, transactions)
    
    def test_apply_additions(self):
        existing = [
            create_transaction_mock("txn1", "acc1", 100),
            create_transaction_mock("txn2", "acc2", 200),
        ]
        
        additions = [
            create_transaction_mock("txn3", "acc3", 300),
            create_transaction_mock("txn1", "acc1", 150),  # duplicate
        ]
        
        result = apply_additions(existing, additions)
        
        self.assertEqual(len(result), 3)
        keys = [gen_key(tr) for tr in result]
        self.assertIn('txn1acc1', keys)
        self.assertIn('txn2acc2', keys)
        self.assertIn('txn3acc3', keys)
        
    def test_apply_additions_empty_existing(self):
        additions = [
            create_transaction_mock("txn1", "acc1", 100),
        ]
        result = apply_additions([], additions)
        self.assertEqual(result, additions)
        
    def test_apply_additions_empty_additions(self):
        existing = [
            create_transaction_mock("txn1", "acc1", 100),
        ]
        result = apply_additions(existing, [])
        self.assertEqual(result, existing)
    
    def test_apply_updates(self):
        existing = [
            create_transaction_mock("txn1", "acc1", 100),
            create_transaction_mock("txn2", "acc2", 200),
            create_transaction_mock("txn3", "acc3", 300)   ,
        ]
        
        updates = [
            create_transaction_mock("txn1", "acc1", 150),  # should replace existing txn1
            create_transaction_mock("txn3", "acc3", 400),  # should replace existing txn3
        ]
        
        result = apply_updates(existing, updates)
        
        self.assertEqual(len(result), 3)
        keys = [gen_key(tr) for tr in result]
        self.assertIn('txn1acc1', keys)  # kept
        self.assertIn('txn2acc2', keys)  # kept
        self.assertIn('txn3acc3', keys)  # kept
        
    def test_apply_updates_all_stale(self):
        existing = [
            create_transaction_mock("txn1", "acc1", 100),
            create_transaction_mock("txn2", "acc2", 200),
        ]
        
        updates = [
            create_transaction_mock("txn1", "acc1", 100),
            create_transaction_mock("txn2", "acc2", 200),
        ]
        
        result = apply_updates(existing, updates)
        self.assertEqual(result, updates)
    
    def test_apply_deletions(self):
        existing = [
            create_transaction_mock("txn1", "acc1", 100),
            create_transaction_mock("txn2", "acc2", 200),
            create_transaction_mock("txn3", "acc3", 300),
        ]
        
        deletions = [
            {'transaction_id': "txn1", "account_id": "acc1"},
            {'transaction_id': "txn3", "account_id": "acc3"},
        ]
        
        result = apply_deletions(existing, deletions)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 'txn2')
        self.assertEqual(result[0].account_id, 'acc2')
        
    def test_apply_deletions_no_matches(self):
        existing = [
            create_transaction_mock("txn1", "acc1", 100),
            create_transaction_mock("txn2", "acc2", 200),
        ]
        
        deletions = [
            {'transaction_id': "txn3", "account_id": "acc3"},
        ]
        
        result = apply_deletions(existing, deletions)
        self.assertEqual(result, existing)
        
    def test_apply_deletions_empty_list(self):
        result = apply_deletions([], [{'transaction_id': "txn1", "account_id": "acc1"}])
        self.assertEqual(result, [])
        
    def test_apply_deletions_no_deletions(self):
        existing = [
            create_transaction_mock("txn1", "acc1", 100),
        ]
        result = apply_deletions(existing, [])
        self.assertEqual(result, existing)


if __name__ == '__main__':
    unittest.main()