from report import ReportBuilder


def test_groups_expenses_by_category(make_record):
    records = [
        make_record(category_group="Food & Drinks", amount=-500.0),
        make_record(category_group="Food & Drinks", amount=-300.0),
        make_record(category_group="Transportation", amount=-200.0),
    ]
    result = ReportBuilder(records).current_month_expenses_by_category()
    assert result["Food & Drinks"] == 800.0
    assert result["Transportation"] == 200.0


def test_total_equals_sum_of_categories(make_record):
    records = [
        make_record(category_group="Food & Drinks", amount=-400.0),
        make_record(category_group="Transportation", amount=-100.0),
    ]
    result = ReportBuilder(records).current_month_expenses_by_category()
    assert result["Total"] == 500.0


def test_excludes_income_records(make_record):
    records = [
        make_record(category_group="Food & Drinks", amount=-500.0),
        make_record(record_type="income", category_group="Food & Drinks", amount=1000.0),
    ]
    result = ReportBuilder(records).current_month_expenses_by_category()
    assert result["Food & Drinks"] == 500.0


def test_excludes_transfer_category(make_record):
    records = [
        make_record(category_name="Groceries", category_group="Food & Drinks", amount=-500.0),
        make_record(category_name="Transfer", category_group="Transfer", amount=-1000.0),
    ]
    result = ReportBuilder(records).current_month_expenses_by_category()
    assert "Transfer" not in result
    assert result["Food & Drinks"] == 500.0


def test_amounts_are_absolute(make_record):
    records = [make_record(category_group="Food & Drinks", amount=-750.0)]
    result = ReportBuilder(records).current_month_expenses_by_category()
    assert result["Food & Drinks"] == 750.0


def test_unpacks_category_name(make_record):
    rb = ReportBuilder([make_record(category_name="Groceries")])
    assert rb._df["category_name"][0] == "Groceries"


def test_unpacks_category_group(make_record):
    rb = ReportBuilder([make_record(category_group="Food & Drinks")])
    assert rb._df["category_group"][0] == "Food & Drinks"


def test_unpacks_amount(make_record):
    rb = ReportBuilder([make_record(amount=-123.45)])
    assert rb._df["amount"][0] == -123.45


def test_unpacks_currency_code(make_record):
    rb = ReportBuilder([make_record()])
    assert rb._df["currencyCode"][0] == "CZK"


def test_output_columns(make_record):
    rb = ReportBuilder([make_record()])
    assert rb._df.columns == ["id", "recordDate", "category_name", "category_group", "amount", "currencyCode", "recordType"]


def test_repr(make_record):
    rb = ReportBuilder([make_record(), make_record()])
    assert repr(rb) == "ReportBuilder(records=2)"
