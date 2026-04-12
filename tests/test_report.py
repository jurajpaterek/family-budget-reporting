from report import ReportBuilder


def test_sums_all_three_food_categories(make_record):
    records = [
        make_record(category_name="Groceries", amount=-500.0),
        make_record(category_name="Bar cafe", amount=-200.0),
        make_record(category_name="Restaurants & fast food", amount=-300.0),
    ]
    assert ReportBuilder(records).current_month_food_spend() == 1000.0


def test_excludes_non_food_category(make_record):
    records = [
        make_record(category_name="Groceries", amount=-500.0),
        make_record(category_name="Transport", amount=-200.0),
    ]
    assert ReportBuilder(records).current_month_food_spend() == 500.0


def test_excludes_income_records(make_record):
    records = [
        make_record(category_name="Groceries", amount=-500.0),
        make_record(record_type="income", category_name="Groceries", amount=1000.0),
    ]
    assert ReportBuilder(records).current_month_food_spend() == 500.0


def test_expense_amounts_are_made_absolute(make_record):
    records = [make_record(category_name="Groceries", amount=-750.0)]
    assert ReportBuilder(records).current_month_food_spend() == 750.0


def test_returns_zero_when_no_food_expenses(make_record):
    records = [make_record(category_name="Transport", amount=-200.0)]
    assert ReportBuilder(records).current_month_food_spend() == 0.0


def test_unpacks_category_name(make_record):
    rb = ReportBuilder([make_record(category_name="Groceries")])
    assert rb.df_records["category_name"][0] == "Groceries"


def test_unpacks_amount(make_record):
    rb = ReportBuilder([make_record(amount=-123.45)])
    assert rb.df_records["amount"][0] == -123.45


def test_unpacks_currency_code(make_record):
    rb = ReportBuilder([make_record()])
    assert rb.df_records["currencyCode"][0] == "CZK"


def test_output_columns(make_record):
    rb = ReportBuilder([make_record()])
    assert rb.df_records.columns == ["id", "recordDate", "category_name", "amount", "currencyCode", "recordType"]
