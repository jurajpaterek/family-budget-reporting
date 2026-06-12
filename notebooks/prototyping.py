import marimo

__generated_with = "0.23.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    from dotenv import load_dotenv
    from requests import get
    import polars as pl

    import marimo as mo

    return get, load_dotenv, os, pl


@app.cell
def _(load_dotenv, os):
    # load API token from .env file
    load_dotenv()
    API_TOKEN = os.environ['WALLET_API_TOKEN']

    # load API BASE URL
    API_URL = "https://rest.budgetbakers.com/wallet/v1/api/"
    return API_TOKEN, API_URL


@app.cell
def _(API_TOKEN, API_URL, get):
    def get_header():
        return {
            'Authorization': f'Bearer {API_TOKEN}',
        }

    # function to get records in a date range
    def get_records_in_range(start_date, end_date):

        headers: dict = get_header()

        params: dict[str, str] = {
            'recordDate': f'gte.{start_date},lte.{end_date}',
            'limit': '200',
            'offset': '0',
        }

        records: list[dict] = []

        while True:
            try:
                response = get(f'{API_URL}/records', headers=headers, params=params).json()
            except Exception as e:
                raise
                break

            records.extend(response['records'])

            if 'nextOffset' in response.keys():         
                params['offset'] = response['nextOffset']
            else:
                break

        return records

    def get_accounts():
        headers: dict = get_header()

        params: dict[str, str] = {
            'limit': '200',
            'offset': '0',
        }

        try:
            response = get(f'{API_URL}/accounts', headers=headers, params=params).json()
        except Exception as e:
            raise

        return response['accounts']


    def get_current_month_records():
        from datetime import datetime
        today = datetime.today()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        return get_records_in_range(start_date, end_date)

    return get_accounts, get_records_in_range


@app.cell
def _(get_accounts):
    # get accounts and categories
    accounts: list = get_accounts()
    # categories: list = get_categories()

    # category_group_mapping: dict['str', 'str'] = {item['id']: item['group']['name'] for item in categories}
    return


@app.cell
def _(get_records_in_range):
    # get records in the date range and convert to DataFrame
    records: list = get_records_in_range('2025-04-01', '2026-04-01')
    return (records,)


@app.cell
def _(pl):
    is_obligatory_regular = (   # scholarship Devinek
            pl.col('counterParty').str.contains('1035870393/5500')
          & pl.col('amount').is_between(-15000, -5000)
          & pl.col('category_name').str.contains('Education & development')
        ) | (
            pl.col('counterParty').str.contains('2869677033/0800')
          & pl.col('category_name').str.contains('Rent')
        )
    return (is_obligatory_regular,)


@app.cell
def _(is_obligatory_regular, pl, records: list):
    df_records = pl.DataFrame(records).with_columns(
        # parse recordDate, createdAt, updatedAt to datetime currently they are in following format '2026-04-01T00:00:00.000Z'
        pl.col("recordDate").str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%S%.fZ").alias("recordDate"),
        pl.col("createdAt").str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%S%.fZ").alias("createdAt"),
        pl.col("updatedAt").str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%S%.fZ").alias("updatedAt"),
        # break down category struct into separate columns
        pl.col("category").struct.field("name").alias("category_name"),
        pl.col("category").struct.field("id").alias("category_id"),
        pl.col("category").struct.field("group").struct.field("name").alias("category_group"),
        # break down labels list of structs into separate column with list of label names
        pl.col("labels").list.eval(pl.element().struct.field("name")).alias("labels_names"),
        # break down amount struct into separate columns
        pl.col("amount").struct.field("currencyCode").alias("currencyCode"),
        pl.col("amount").struct.field("value").alias("amount"),
    ).with_columns(
        # add is_obligatory_regular column
        is_obligatory_regular.alias("obligatory_regular")
    ).select(
        pl.col([
            "recordDate",
            # "category",
            "category_name",
            "category_group",
            "note",
            # "labels",
            "labels_names",
            # "baseAmount",        
            "amount",
            "currencyCode",
            "category_id",        
            "recordType",
            "recordState",
            "paymentType",
            "createdAt",
            "updatedAt",
            # "source",
            "counterParty",
            "id",
            "accountId",
        ])
        )
    return (df_records,)


@app.cell
def _(df_records):
    df_records
    return


@app.cell
def _(df_records, pl):
    df_expense_2601 = (
        df_records
            .filter(
                  (pl.col("category_name") != "Transfer")   # filters out transfers between my own accounts - they are shown as expense/income with specific category "Transfer"
                & (pl.col("recordType") == "expense")       # limits to expenses only
                & (pl.col("recordDate") >= pl.date(2026, 1, 1))
                & (pl.col("recordDate") < pl.date(2026, 2, 1))
                )       
    )

    # df_expense_2601
    return (df_expense_2601,)


@app.cell
def _(df_expense_2601, pl):
    # dict of metrics to calculate for the report

    expense_by_category: dict[str, float] = {row[0]: row[1] for row in (
        df_expense_2601
        .group_by("category_group")
        .agg(pl.col("amount").sum().abs().alias("total_amount"))
        .sort("total_amount", descending=True)
        ).iter_rows()}

    # add total expenses to the dict
    expense_by_category["Total"] = df_expense_2601.select(pl.col("amount").sum().abs()).item()

    expense_by_category
    return


@app.cell
def _(df_records, pl):
    # dict of last 6-month average monthly expenses by category group calculated as arithmetic mean of expenses per month for the specific category group in the last 6 months (from 2025-07-01 to 2025-12-31)

    df_expense_6m = (
        df_records
            .filter(
                  (pl.col("category_name") != "Transfer")   # filters out transfers between my own accounts - they are shown as expense/income with specific category "Transfer"
                & (pl.col("recordType") == "expense")       # limits to expenses only
                & (pl.col("recordDate") >= pl.date(2025, 7, 1))
                & (pl.col("recordDate") < pl.date(2026, 1, 1))
                )       
    )

    expense_6m_by_month_category = (
        df_expense_6m
        .with_columns(pl.col("recordDate").dt.month().alias("month"))
        .group_by(["month", "category_group"])
        .agg(pl.col("amount").sum().abs().alias("total_amount"))
        .sort(["category_group", "month"])
    )

    expense_6m_mean_by_category = (
        expense_6m_by_month_category
        .group_by("category_group")
        .agg(pl.col("total_amount").median().alias("avg_monthly_expense"))
        .sort("avg_monthly_expense", descending=True)
    )

    expense_6m_mean_by_category_dict: dict[str, float] = {row[0]: row[1] for row in expense_6m_mean_by_category.iter_rows()}
    expense_6m_mean_by_category_dict
    return


@app.cell
def _():
    # from redmail import gmail

    # gmail.username = os.environ['GMAIL_USERNAME']  # your Gmail address
    # gmail.password = os.environ['GMAIL_APP_PASSWORD']  # 16-char app password from Google Account

    # gmail.send(
    #     receivers=["juraj.paterek@gmail.com"],
    #     subject="This month's spendings",
    #     # prepare sarcastic report on my current month spending based on the expense_by_category dict with '\t category ... amount CZK' format for each category and a final line with total expenses same format but bold, and add a sarcastic comment on total spend if the amount is above 75000 CZK. Start with a greeting and end with a positive note if the total spend is below 75000 CZK.

    #     html=f"""
    #     <p>Hi Juraj,</p>
    #     <p>Here is your spending report for this month:</p>
    #     <ul>
    #     {''.join([f"<li><b>{category}</b>: {amount:.2f} CZK</li>" for category, amount in expense_by_category.items() if category != "Total"])}
    #     </ul>
    #     <p><b>Total: {expense_by_category['Total']:.2f} CZK</b></p>
    #     <p>{'Wow, you really went all out this month! Maybe consider cutting back on some expenses next month?' if expense_by_category['Total'] > 75000 else 'Great job keeping your expenses in check this month! Keep it up!'}</p>
    #     <p>Have a great day!</p>    
    #     """,   
    # )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
