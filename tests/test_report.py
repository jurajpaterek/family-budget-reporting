from report import ReportBuilder


def test_groups_expenses_by_category(make_record, obligatory_expenses):
    records = [
        make_record(category_group="Food & Drinks", amount=-500.0),
        make_record(category_group="Food & Drinks", amount=-300.0),
        make_record(category_group="Transportation", amount=-200.0),
    ]
    result = ReportBuilder(records, obligatory_expenses).current_month_expenses_by_category()
    assert result["Food & Drinks"] == 800.0
    assert result["Transportation"] == 200.0


def test_total_equals_sum_of_all_expenses(make_record, obligatory_expenses):
    records = [
        make_record(category_group="Food & Drinks", amount=-400.0),
        make_record(category_group="Transportation", amount=-100.0),
    ]
    result = ReportBuilder(records, obligatory_expenses).current_month_expenses_by_category()
    assert result["Total"] == 500.0


def test_obligatory_excluded_from_category_breakdown(make_record, obligatory_expenses):
    records = [
        make_record(category_group="Food & Drinks", amount=-300.0),
        make_record(category_name="Rent", category_group="Housing", amount=-15000.0, counter_party="test-counterparty"),
    ]
    result = ReportBuilder(records, obligatory_expenses).current_month_expenses_by_category()
    assert "Housing" not in result
    assert result["Food & Drinks"] == 300.0


def test_total_includes_obligatory(make_record, obligatory_expenses):
    records = [
        make_record(category_group="Food & Drinks", amount=-300.0),
        make_record(category_name="Rent", category_group="Housing", amount=-15000.0, counter_party="test-counterparty"),
    ]
    result = ReportBuilder(records, obligatory_expenses).current_month_expenses_by_category()
    assert result["Total"] == 15300.0


def test_excludes_income_records(make_record, obligatory_expenses):
    records = [
        make_record(category_group="Food & Drinks", amount=-500.0),
        make_record(record_type="income", category_group="Food & Drinks", amount=1000.0),
    ]
    result = ReportBuilder(records, obligatory_expenses).current_month_expenses_by_category()
    assert result["Food & Drinks"] == 500.0


def test_excludes_transfer_category(make_record, obligatory_expenses):
    records = [
        make_record(category_name="Groceries", category_group="Food & Drinks", amount=-500.0),
        make_record(category_name="Transfer", category_group="Transfer", amount=-1000.0),
    ]
    result = ReportBuilder(records, obligatory_expenses).current_month_expenses_by_category()
    assert "Transfer" not in result
    assert result["Food & Drinks"] == 500.0


def test_amounts_are_absolute(make_record, obligatory_expenses):
    records = [make_record(category_group="Food & Drinks", amount=-750.0)]
    result = ReportBuilder(records, obligatory_expenses).current_month_expenses_by_category()
    assert result["Food & Drinks"] == 750.0


def test_obligatory_paid(make_record, obligatory_expenses):
    records = [
        make_record(category_name="Rent", category_group="Housing", amount=-14000.0, counter_party="test-counterparty"),
    ]
    status = ReportBuilder(records, obligatory_expenses).current_month_obligatory_status()
    assert status[0]["paid"] is True
    assert status[0]["amount"] == 14000.0
    assert status[0]["label"] == "Rent"


def test_obligatory_not_paid(make_record, obligatory_expenses):
    records = [make_record(category_group="Food & Drinks", amount=-500.0)]
    status = ReportBuilder(records, obligatory_expenses).current_month_obligatory_status()
    assert status[0]["paid"] is False
    assert status[0]["amount"] is None


def test_obligatory_amount_range_not_matched(make_record):
    obligatory_with_range = [
        {
            "label": "Scholarship",
            "counterparty": "test-counterparty",
            "category": "Education",
            "amount_min": -15000,
            "amount_max": -5000,
        }
    ]
    records = [
        make_record(category_name="Education", category_group="Education", amount=-3000.0, counter_party="test-counterparty"),
    ]
    status = ReportBuilder(records, obligatory_with_range).current_month_obligatory_status()
    assert status[0]["paid"] is False


def test_unpacks_category_name(make_record, obligatory_expenses):
    rb = ReportBuilder([make_record(category_name="Groceries")], obligatory_expenses)
    assert rb._df["category_name"][0] == "Groceries"


def test_unpacks_category_group(make_record, obligatory_expenses):
    rb = ReportBuilder([make_record(category_group="Food & Drinks")], obligatory_expenses)
    assert rb._df["category_group"][0] == "Food & Drinks"


def test_unpacks_amount(make_record, obligatory_expenses):
    rb = ReportBuilder([make_record(amount=-123.45)], obligatory_expenses)
    assert rb._df["amount"][0] == -123.45


def test_unpacks_currency_code(make_record, obligatory_expenses):
    rb = ReportBuilder([make_record()], obligatory_expenses)
    assert rb._df["currencyCode"][0] == "CZK"


def test_output_columns(make_record, obligatory_expenses):
    rb = ReportBuilder([make_record()], obligatory_expenses)
    assert rb._df.columns == ["id", "recordDate", "category_name", "category_group", "amount", "currencyCode", "recordType", "counterParty", "obligatory_regular"]


def test_repr(make_record, obligatory_expenses):
    rb = ReportBuilder([make_record(), make_record()], obligatory_expenses)
    assert repr(rb) == "ReportBuilder(records=2)"
