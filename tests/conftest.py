import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))


@pytest.fixture
def make_record():
    def _make_record(record_type="expense", category_name="Groceries", amount=-500.0):
        return {
            "id": "test-id",
            "recordDate": "2026-04-01",
            "category": {"name": category_name},
            "baseAmount": {"currencyCode": "CZK", "value": amount},
            "recordType": record_type,
        }
    return _make_record
