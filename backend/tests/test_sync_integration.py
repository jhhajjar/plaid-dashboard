import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.Transaction import TransactionEntity, TransactionCategory
from logic.transaction_logic import (
    map_plaid_transaction_to_transaction_entity,
    map_plaid_category_to_app_category,
    apply_additions,
    apply_updates,
    apply_deletions,
    gen_key,
    drop_duplicates,
)
from mocks import (
    mock_plaid_transactions,
    mock_existing_transactions,
    mock_duplicate_plaid_transaction,
    mock_plaid_transaction_with_location,
    create_plaid_transaction,
    create_mock_transaction_entity,
)


class TestPlaidTransactionMapping(unittest.TestCase):
    """Tests for mapping Plaid transactions to internal TransactionEntity format."""

    def test_map_plaid_transaction_basic_fields(self) -> None:
        """Test that basic fields are correctly mapped from Plaid format."""
        plaid_tr = mock_plaid_transactions[0]
        entity = map_plaid_transaction_to_transaction_entity(plaid_tr)

        self.assertEqual(entity.id, plaid_tr["transaction_id"])
        self.assertEqual(entity.account_id, plaid_tr["account_id"])
        self.assertEqual(entity.merchant_name, plaid_tr["merchant_name"])
        self.assertEqual(entity.name, plaid_tr["name"])
        self.assertEqual(entity.date, plaid_tr["date"])
        self.assertEqual(entity.authorized_date, plaid_tr["authorized_date"])
        self.assertEqual(entity.iso_currency_code, plaid_tr["iso_currency_code"])
        self.assertEqual(entity.payment_channel, plaid_tr["payment_channel"])
        self.assertEqual(entity.pending, plaid_tr["pending"])

    def test_map_plaid_transaction_amount_transformation(self) -> None:
        """Test that Plaid amounts are negated (Plaid positive = expense, app negative = expense)."""
        # Plaid positive amount (debit/expense)
        plaid_tr = create_plaid_transaction(
            transaction_id="test_amount",
            account_id="acc_001",
            amount=100.0,
        )
        entity = map_plaid_transaction_to_transaction_entity(plaid_tr)

        self.assertEqual(entity.plaid_amount, 100.0)
        self.assertEqual(entity.amount, -100.0)  # Negated

        # Plaid negative amount (credit/income)
        plaid_tr_income = create_plaid_transaction(
            transaction_id="test_income",
            account_id="acc_001",
            amount=-500.0,
            category="INCOME_WAGES",
        )
        entity_income = map_plaid_transaction_to_transaction_entity(plaid_tr_income)

        self.assertEqual(entity_income.plaid_amount, -500.0)
        self.assertEqual(entity_income.amount, 500.0)  # Negated (becomes positive income)

    def test_map_plaid_transaction_location_extraction(self) -> None:
        """Test that nested location data is correctly flattened."""
        entity = map_plaid_transaction_to_transaction_entity(
            mock_plaid_transaction_with_location
        )

        self.assertEqual(entity.address, "123 Main St")
        self.assertEqual(entity.city, "San Francisco")
        self.assertEqual(entity.country, "US")
        self.assertEqual(entity.lat, 37.7749)
        self.assertEqual(entity.lon, -122.4194)
        self.assertEqual(entity.postal_code, "94102")
        self.assertEqual(entity.region, "CA")

    def test_map_plaid_transaction_null_location(self) -> None:
        """Test that null location fields are handled correctly."""
        plaid_tr = mock_plaid_transactions[0]  # No location data
        entity = map_plaid_transaction_to_transaction_entity(plaid_tr)

        self.assertIsNone(entity.address)
        self.assertIsNone(entity.city)
        self.assertIsNone(entity.country)
        self.assertIsNone(entity.lat)
        self.assertIsNone(entity.lon)
        self.assertIsNone(entity.postal_code)
        self.assertIsNone(entity.region)

    def test_map_plaid_transaction_category_extraction(self) -> None:
        """Test that category is extracted from nested personal_finance_category."""
        plaid_tr = create_plaid_transaction(
            transaction_id="test_category",
            account_id="acc_001",
            amount=50.0,
            category="FOOD_AND_DRINK_RESTAURANT",
        )
        entity = map_plaid_transaction_to_transaction_entity(plaid_tr)

        self.assertEqual(entity.category, "FOOD_AND_DRINK_RESTAURANT")

    def test_map_all_mock_transactions(self) -> None:
        """Test that all mock Plaid transactions can be mapped without errors."""
        for plaid_tr in mock_plaid_transactions:
            entity = map_plaid_transaction_to_transaction_entity(plaid_tr)
            self.assertIsInstance(entity, TransactionEntity)
            self.assertIsNotNone(entity.id)
            self.assertIsNotNone(entity.account_id)


class TestCategoryMapping(unittest.TestCase):
    """Tests for Plaid category to app category mapping."""

    def test_income_category_mapping(self) -> None:
        """Test income categories are mapped correctly."""
        self.assertEqual(
            map_plaid_category_to_app_category("INCOME_WAGES"),
            TransactionCategory.INCOME,
        )
        self.assertEqual(
            map_plaid_category_to_app_category("INCOME_INTEREST_EARNED"),
            TransactionCategory.INCOME,
        )

    def test_food_category_mapping(self) -> None:
        """Test food/dining categories are mapped correctly."""
        self.assertEqual(
            map_plaid_category_to_app_category("FOOD_AND_DRINK_RESTAURANT"),
            TransactionCategory.FOOD,
        )
        self.assertEqual(
            map_plaid_category_to_app_category("FOOD_AND_DRINK_COFFEE"),
            TransactionCategory.FOOD,
        )
        self.assertEqual(
            map_plaid_category_to_app_category("FOOD_AND_DRINK_FAST_FOOD"),
            TransactionCategory.FOOD,
        )

    def test_groceries_category_mapping(self) -> None:
        """Test grocery categories are mapped correctly."""
        self.assertEqual(
            map_plaid_category_to_app_category("FOOD_AND_DRINK_GROCERIES"),
            TransactionCategory.GROCERIES,
        )

    def test_transportation_category_mapping(self) -> None:
        """Test transportation categories are mapped correctly."""
        self.assertEqual(
            map_plaid_category_to_app_category("TRANSPORTATION_TAXIS_AND_RIDE_SHARES"),
            TransactionCategory.TRANSPORTATION,
        )
        self.assertEqual(
            map_plaid_category_to_app_category("TRANSPORTATION_GAS"),
            TransactionCategory.TRANSPORTATION,
        )

    def test_entertainment_category_mapping(self) -> None:
        """Test entertainment categories are mapped correctly."""
        self.assertEqual(
            map_plaid_category_to_app_category("ENTERTAINMENT_TV_AND_MOVIES"),
            TransactionCategory.ENTERTAINMENT,
        )

    def test_shopping_category_mapping(self) -> None:
        """Test shopping categories are mapped correctly."""
        self.assertEqual(
            map_plaid_category_to_app_category(
                "GENERAL_MERCHANDISE_OTHER_GENERAL_MERCHANDISE"
            ),
            TransactionCategory.SHOPPING,
        )
        self.assertEqual(
            map_plaid_category_to_app_category(
                "GENERAL_MERCHANDISE_CLOTHING_AND_ACCESSORIES"
            ),
            TransactionCategory.SHOPPING,
        )

    def test_investing_category_mapping(self) -> None:
        """Test investing categories are mapped correctly."""
        self.assertEqual(
            map_plaid_category_to_app_category(
                "TRANSFER_OUT_INVESTMENT_AND_RETIREMENT_FUNDS"
            ),
            TransactionCategory.INVESTING,
        )

    def test_misc_category_mapping(self) -> None:
        """Test misc/transfer categories are mapped correctly."""
        self.assertEqual(
            map_plaid_category_to_app_category("TRANSFER_OUT_ACCOUNT_TRANSFER"),
            TransactionCategory.MISC,
        )

    def test_unknown_category_defaults_to_misc(self) -> None:
        """Test that unknown categories default to MISC."""
        self.assertEqual(
            map_plaid_category_to_app_category("UNKNOWN_CATEGORY_XYZ"),
            TransactionCategory.MISC,
        )


class TestDuplicatePrevention(unittest.TestCase):
    """Tests for ensuring duplicate transactions are not added."""

    def test_no_duplicates_after_adding_new_transactions(self) -> None:
        """Test that adding transactions with same id+account_id doesn't create duplicates."""
        existing = [
            create_mock_transaction_entity("txn1", "acc1", 100.0),
            create_mock_transaction_entity("txn2", "acc2", 200.0),
        ]

        # Map Plaid transactions to entities
        additions = [
            map_plaid_transaction_to_transaction_entity(plaid_tr)
            for plaid_tr in mock_plaid_transactions
        ]

        result = apply_additions(existing, additions)

        # Check no duplicates by verifying unique keys
        keys = [gen_key(tr) for tr in result]
        self.assertEqual(len(keys), len(set(keys)))

    def test_duplicate_plaid_transaction_not_added(self) -> None:
        """Test that a duplicate Plaid transaction (same id+account_id) is not added."""
        existing = list(mock_existing_transactions)  # Copy to avoid mutation
        original_count = len(existing)

        # Create a mapped entity that has the same id+account_id as existing
        duplicate_entity = map_plaid_transaction_to_transaction_entity(
            mock_duplicate_plaid_transaction
        )

        result = apply_additions(existing, [duplicate_entity])

        # Count should remain the same
        self.assertEqual(len(result), original_count)

        # The original transaction's amount should be preserved (first occurrence kept)
        original_tr = next(tr for tr in result if tr.id == "existing_txn_001")
        self.assertEqual(original_tr.amount, -100.0)  # Original amount, not 999.0

    def test_same_transaction_id_different_account_not_duplicate(self) -> None:
        """Test that same transaction_id but different account_id is not a duplicate."""
        existing = [create_mock_transaction_entity("txn1", "acc1", 100.0)]

        # Same transaction_id but different account_id
        new_tr = create_mock_transaction_entity("txn1", "acc2", 200.0)

        result = apply_additions(existing, [new_tr])

        # Both should exist
        self.assertEqual(len(result), 2)
        keys = [gen_key(tr) for tr in result]
        self.assertIn("txn1acc1", keys)
        self.assertIn("txn1acc2", keys)

    def test_drop_duplicates_preserves_order(self) -> None:
        """Test that drop_duplicates keeps first occurrence and preserves order."""
        transactions = [
            create_mock_transaction_entity("txn1", "acc1", 100.0),
            create_mock_transaction_entity("txn2", "acc2", 200.0),
            create_mock_transaction_entity("txn1", "acc1", 999.0),  # Duplicate
            create_mock_transaction_entity("txn3", "acc3", 300.0),
        ]

        result = drop_duplicates(transactions)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].id, "txn1")
        self.assertEqual(result[0].amount, 100.0)  # First occurrence
        self.assertEqual(result[1].id, "txn2")
        self.assertEqual(result[2].id, "txn3")


class TestSyncIntegration(unittest.TestCase):
    """Integration tests for the full sync flow."""

    def test_full_sync_flow_additions(self) -> None:
        """Test full sync flow with additions only."""
        existing = list(mock_existing_transactions)

        # Simulate Plaid sync returning new transactions
        added_from_plaid = [
            map_plaid_transaction_to_transaction_entity(plaid_tr)
            for plaid_tr in mock_plaid_transactions[:3]  # First 3 transactions
        ]

        result = apply_additions(existing, added_from_plaid)

        # Should have original + new transactions
        self.assertEqual(len(result), len(existing) + len(added_from_plaid))

        # Verify all original transactions are present
        result_ids = [(tr.id, tr.account_id) for tr in result]
        for orig_tr in existing:
            self.assertIn((orig_tr.id, orig_tr.account_id), result_ids)

    def test_full_sync_flow_updates(self) -> None:
        """Test full sync flow with updates (modified transactions)."""
        existing = [
            create_mock_transaction_entity(
                "txn1", "acc1", -100.0, plaid_amount=100.0, merchant_name="Old Merchant"
            ),
            create_mock_transaction_entity(
                "txn2", "acc2", -200.0, plaid_amount=200.0, merchant_name="Unchanged"
            ),
        ]

        # Simulate Plaid returning an updated transaction
        updated_plaid = create_plaid_transaction(
            transaction_id="txn1",
            account_id="acc1",
            amount=150.0,  # Changed amount
            merchant_name="Updated Merchant",
        )
        updates = [map_plaid_transaction_to_transaction_entity(updated_plaid)]

        result = apply_updates(existing, updates)

        # Should still have 2 transactions
        self.assertEqual(len(result), 2)

        # txn1 should be updated
        updated_tr = next(tr for tr in result if tr.id == "txn1")
        self.assertEqual(updated_tr.amount, -150.0)  # Negated from Plaid
        self.assertEqual(updated_tr.merchant_name, "Updated Merchant")

        # txn2 should be unchanged
        unchanged_tr = next(tr for tr in result if tr.id == "txn2")
        self.assertEqual(unchanged_tr.amount, -200.0)
        self.assertEqual(unchanged_tr.merchant_name, "Unchanged")

    def test_full_sync_flow_deletions(self) -> None:
        """Test full sync flow with deletions."""
        existing = [
            create_mock_transaction_entity("txn1", "acc1", -100.0),
            create_mock_transaction_entity("txn2", "acc2", -200.0),
            create_mock_transaction_entity("txn3", "acc3", -300.0),
        ]

        # Simulate Plaid returning deletions
        deletions = [
            {"transaction_id": "txn1", "account_id": "acc1"},
            {"transaction_id": "txn3", "account_id": "acc3"},
        ]

        result = apply_deletions(existing, deletions)

        # Should only have txn2 remaining
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "txn2")

    def test_full_sync_flow_combined(self) -> None:
        """Test full sync flow with additions, updates, and deletions combined."""
        existing = [
            create_mock_transaction_entity("txn1", "acc1", -100.0, plaid_amount=100.0),
            create_mock_transaction_entity("txn2", "acc2", -200.0, plaid_amount=200.0),
            create_mock_transaction_entity("txn3", "acc3", -300.0, plaid_amount=300.0),
        ]

        # Additions
        added_plaid = create_plaid_transaction(
            transaction_id="txn4", account_id="acc4", amount=400.0
        )
        additions = [map_plaid_transaction_to_transaction_entity(added_plaid)]

        # Updates
        updated_plaid = create_plaid_transaction(
            transaction_id="txn2", account_id="acc2", amount=250.0
        )
        updates = [map_plaid_transaction_to_transaction_entity(updated_plaid)]

        # Deletions
        deletions = [{"transaction_id": "txn1", "account_id": "acc1"}]

        # Apply in order: additions, updates, deletions (as in plaid_sync)
        result = apply_additions(existing, additions)
        result = apply_updates(result, updates)
        result = apply_deletions(result, deletions)

        # Should have: txn2 (updated), txn3 (unchanged), txn4 (added) = 3 transactions
        self.assertEqual(len(result), 3)

        result_ids = [tr.id for tr in result]
        self.assertNotIn("txn1", result_ids)  # Deleted
        self.assertIn("txn2", result_ids)  # Updated
        self.assertIn("txn3", result_ids)  # Unchanged
        self.assertIn("txn4", result_ids)  # Added

        # Verify txn2 was updated
        txn2 = next(tr for tr in result if tr.id == "txn2")
        self.assertEqual(txn2.amount, -250.0)

    def test_sync_with_all_mock_transactions_no_duplicates(self) -> None:
        """Test that syncing all mock transactions produces no duplicates."""
        existing = list(mock_existing_transactions)

        # Map all Plaid transactions
        additions = [
            map_plaid_transaction_to_transaction_entity(plaid_tr)
            for plaid_tr in mock_plaid_transactions
        ]

        result = apply_additions(existing, additions)

        # Verify no duplicates
        keys = [gen_key(tr) for tr in result]
        self.assertEqual(len(keys), len(set(keys)), "Duplicate transactions found!")

        # Verify expected count
        expected_count = len(existing) + len(mock_plaid_transactions)
        self.assertEqual(len(result), expected_count)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases in transaction sync."""

    def test_empty_additions(self) -> None:
        """Test handling empty additions list."""
        existing = list(mock_existing_transactions)
        result = apply_additions(existing, [])
        self.assertEqual(len(result), len(existing))

    def test_empty_existing_transactions(self) -> None:
        """Test adding to empty existing transaction list."""
        additions = [
            map_plaid_transaction_to_transaction_entity(plaid_tr)
            for plaid_tr in mock_plaid_transactions[:2]
        ]

        result = apply_additions([], additions)
        self.assertEqual(len(result), 2)

    def test_null_merchant_name_handling(self) -> None:
        """Test that transactions with null merchant_name are handled."""
        plaid_tr = create_plaid_transaction(
            transaction_id="null_merchant",
            account_id="acc_001",
            amount=100.0,
            merchant_name=None,
            name="Fallback Name",
        )

        entity = map_plaid_transaction_to_transaction_entity(plaid_tr)

        self.assertIsNone(entity.merchant_name)
        self.assertEqual(entity.name, "Fallback Name")

    def test_multiple_transactions_same_account(self) -> None:
        """Test handling multiple transactions from the same account."""
        plaid_transactions = [
            create_plaid_transaction(
                transaction_id=f"txn_{i}",
                account_id="same_account",
                amount=float(i * 10),
            )
            for i in range(5)
        ]

        entities = [
            map_plaid_transaction_to_transaction_entity(tr) for tr in plaid_transactions
        ]

        result = apply_additions([], entities)

        # All 5 should be present (different transaction_ids)
        self.assertEqual(len(result), 5)

        # Verify all have same account_id but different ids
        account_ids = {tr.account_id for tr in result}
        self.assertEqual(account_ids, {"same_account"})

        transaction_ids = {tr.id for tr in result}
        self.assertEqual(len(transaction_ids), 5)


if __name__ == "__main__":
    unittest.main()
