import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))


@pytest.fixture
def make_record():
    def _make_record(record_type="expense", category_name="Groceries", category_group="Food & Drinks", amount=-500.0):
        return {
            "id": "test-id",
            "recordDate": "2026-04-01",
            "category": {
                "id": "food-id",
                "name": category_name,
                "group": {"id": "food_drinks", "name": category_group},
            },
            "amount": {"value": amount, "currencyCode": "CZK"},
            "recordType": record_type,
        }
    return _make_record
