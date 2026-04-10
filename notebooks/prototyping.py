import marimo

__generated_with = "0.22.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    from dotenv import load_dotenv
    from requests import get
    import polars as pl

    import marimo as mo

    return get, load_dotenv, mo, os, pl


@app.cell
def _(load_dotenv, os):
    # load API token from .env file
    load_dotenv()
    API_TOKEN = os.environ['WALLET_API_TOKEN']

    # load API BASE URL
    API_URL = os.environ['WALLET_BASE_URL']
    return API_TOKEN, API_URL


@app.cell
def _(API_TOKEN, API_URL, get):
    def get_records_in_range(start_date, end_date):

        headers = {
            'Authorization': f'Bearer {API_TOKEN}',
        }

        params = {
            'recordDate': f'gte.{start_date},lte.{end_date}',
            'limit': '200',
            'offset': '0',
        }

        records = []

        while True:
            try:
                response = get(f'{API_URL}/records', headers=headers, params=params).json()
            except Exception as e:
                break

            records.extend(response['records'])

            if 'nextOffset' in response.keys():         
                params['offset'] = response['nextOffset']
            else:
                break

        # return records
        return records

    return (get_records_in_range,)


@app.cell
def _(get_records_in_range):
    records = get_records_in_range('2025-04-01', '2025-12-31')
    return (records,)


@app.cell
def _(pl, records):
    # load records list to polars dataframe
    df = pl.DataFrame(records)

    df = df.with_columns(
        pl.col("category").struct.field("name").alias("category_name")
    ).with_columns(
        pl.col("category").struct.field("color").alias("category_color")
    ).with_columns(
        pl.col("labels")
        .list.eval(pl.element().struct.field("name"))
        .alias("labels_names")
            ).select(
            pl.col([
                "recordDate",
                "amount",
                "baseAmount",
                "note",
                "category",
                "category_name",
                "category_color",
                "labels",
                "labels_names",
                "recordType",
                "recordState",
                "paymentType",
                "createdAt",
                "updatedAt",
                "payer",
                "payee",
                "id",
                "accountId",
            ])
        )
    return (df,)


@app.cell
def _(df, pl):
    # check if all expense records have labels

    (
        df.filter(
            pl.col("recordType").str.contains("expense")
            & pl.col("labels").is_null()
            & ~pl.col("category_name").str.contains("Transfer")
        ).select(
            pl.col(
                [
                    "note",
                    "amount",
                    "category_name",
                    "labels_names",
                    "recordDate",
                    "recordType",
                    "paymentType",
                    "payee",
                ]
            )
        )
    )
    return


@app.cell
def _(df, pl):
    unique_categories_trueexpense = set(
        df
            .filter(pl.col('labels_names').list.contains("TrueExpense"))
            .select(pl.col('category_name')).unique().sort('category_name')
            ['category_name']
    )

    unique_categories_not_trueexpense = set(
        df
            .filter(~pl.col('labels_names').list.contains("TrueExpense"))
            .select(pl.col('category_name')).unique().sort('category_name')
            ['category_name']
    )

    # print sets sizes
    print(f"Categories with TrueExpense label: {len(unique_categories_trueexpense)}")
    print(f"Categories without TrueExpense label: {len(unique_categories_not_trueexpense)}")

    # crossection of categories with and without TrueExpense label
    intersection = unique_categories_trueexpense.intersection(unique_categories_not_trueexpense)
    print(f"Categories with and without TrueExpense label: {len(intersection)}")

    # categories in without TrueExpense label but not in with TrueExpense label
    difference = unique_categories_not_trueexpense.difference(unique_categories_trueexpense)
    print(f"Categories without TrueExpense label but not in with TrueExpense label: {len(difference)}")
    difference
    return difference, intersection


@app.cell
def _(df, difference, pl):
    # expenses with category in the difference set
    df.filter(
        # pl.col('recordType').str.contains("expense") &
        # ~pl.col('labels_names').list.contains("TrueExpense") &
        pl.col('category_name').is_in(difference)
    ).select(
        pl.col(
            [
                "note",
                "amount",
                "category_name",
                "labels_names",
                "recordDate",
                "recordType",
                "paymentType",
                "payee",
            ]
        )
    )
    return


@app.cell
def _(df, intersection, pl):
    # filter records without label TrueExpense but with category in the intersection
    df.filter(
        ~pl.col('labels_names').list.contains("TrueExpense") &
        pl.col('category_name').is_in(intersection)
    ).select(
        pl.col(
            [
                "note",
                "amount",
                "category_name",
                "labels_names",
                "recordDate",
                "recordType",
                "paymentType",
                "payee",
            ]
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    find a filter that will lead to TrueExpense label subse
    """)
    return


@app.cell
def _(df, pl):
    df_ala_trueexpense = (
        df
        .filter(
            pl.col('recordType').str.contains("expense") &
            ~pl.col('labels_names').list.contains('Refund/Refunded') &
            ~pl.col('labels_names').list.contains('Datamole')
        )
    )

    df_trueexpense = (
        df
        .filter(
            pl.col('labels_names').list.contains('TrueExpense')
        )
    )
    return df_ala_trueexpense, df_trueexpense


@app.cell
def _(df_ala_trueexpense, df_trueexpense, pl):
    # verify what rows are missing or are extra in df_ala_trueexpense compared to df_trueexpense

    trueexpense_ids = df_trueexpense['id'].to_list()
    ala_trueexpense_ids = df_ala_trueexpense['id'].to_list()

    missing_in_ala = df_trueexpense.filter(~pl.col('id').is_in(ala_trueexpense_ids))

    extra_in_ala = df_ala_trueexpense.filter(~pl.col('id').is_in(trueexpense_ids))

    print(f"Missing in ala_trueexpense: {missing_in_ala.shape[0]} records")
    print(f"Extra in ala_trueexpense: {extra_in_ala.shape[0]} records")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    set monthly budgets on:
    - total spend
    - groceries
    - shopping
    - leisure

    set yearly budgets on:
    - total spend
    - shopping
    - leisure
    """)
    return


@app.cell
def _(df, pl):
    # show me recordType 'expense' and category 'Transfer'
    df.filter(
        pl.col('recordType').str.contains("expense") &
        pl.col('category_name').str.contains("Transfer")
    ).select(
        pl.col(
            [
                "note",
                "amount",
                "category_name",
                "labels_names",
                "recordDate",
                "recordType",
                "paymentType",
                "payee",
            ]
        )
    ).sort('note', descending=False)
    return


@app.cell
def _(df, pl):
    # pie chart of expenses divided by category_color and in the second level by category_name, excluding Transfer category and grouping small categories into "Other"

    # Group by category_color and category_name, summing amounts
    category_color_sums = (
        df
        .filter(
            pl.col('recordType').str.contains("expense") &
            ~pl.col('category_name').str.contains("Transfer")
        )
        .group_by(['category_color', 'category_name'])
        .agg(pl.col('amount').struct.field('value').sum().abs().alias('total_amount'))
    )

    # Group small categories into "Other"
    threshold = 0.00  # categories below 1% go into "Other"
    total = category_color_sums['total_amount'].sum()
    category_color_sums_refined = category_color_sums.with_columns(
        pl.when(pl.col('total_amount') / total < threshold)
        .then(pl.lit('Other'))
        .otherwise(pl.col('category_name'))
        .alias('category_name')
    ).group_by(['category_color', 'category_name']).agg(
        pl.col('total_amount').sum()
    ).sort('total_amount', descending=True)

    # Plot
    import plotly.express as px
    fig_color = px.sunburst(
        category_color_sums_refined.to_pandas(),
        path=['category_color', 'category_name'],
        values='total_amount',
        title='Expenses by Category Color and Name',
    )
    fig_color.update_traces(
        textinfo='label+percent parent',
    )
    fig_color.update_layout(
        title_font_size=20,
        margin=dict(t=80, b=80, l=80, r=80),
    )
    fig_color.show()
    return


@app.cell
def _(get_records_in_range):
    def get_current_month_records():
        from datetime import datetime
        today = datetime.today()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        return get_records_in_range(start_date, end_date)

    return (get_current_month_records,)


@app.cell
def _(get_current_month_records, pl):
    food_n_drinks = ["Bar cafe", "Restaurants & fast food", "Groceries"]

    current_month_records = get_current_month_records()
    df_current_month = pl.DataFrame(current_month_records)

    df_current_month = df_current_month.with_columns(
        pl.col("category").struct.field("name").alias("category_name"),
        pl.col("baseAmount").struct.field("currencyCode").alias("currencyCode"),
        pl.col("baseAmount").struct.field("value").alias("amount"),
    ).select(
        pl.col(
            [
                "id",
                "recordDate",
                "category_name",
                "amount",
                "currencyCode",
                "note",
                "recordState",
                "recordType",
                "paymentType",
                "payee",
                "payer",
                # "accountId",
                # "baseAmount",
                # "category",
                # "createdAt",
                # "updatedAt",
            ]
        )
    )

    # .abs().sum() of amount for category_name in food_n_drinks
    total_food_n_drinks = (
        df_current_month
        .filter(
            pl.col('recordType').str.contains("expense") &
            pl.col('category_name').is_in(food_n_drinks)
        )
        .select(pl.col('amount').abs().sum().alias('total_amount'))
    )['total_amount'][0]

    total_food_n_drinks
    return (total_food_n_drinks,)


@app.cell
def _(os, total_food_n_drinks):
    from redmail import gmail

    gmail.username = os.environ['GMAIL_USERNAME']  # your Gmail address
    gmail.password = os.environ['GMAIL_APP_PASSWORD']  # 16-char app password from Google Account

    gmail.send(
        receivers=["juraj.paterek@gmail.com"],
        subject="Food & drinks current month report",
        # html content of the email, funny message if total_food_n_drinks is above 10000, otherwise a congratulatory message
        html=f"""<p>Hi Juraj,</p>
    <p>Your total spend on food and drinks for the current month is <b>{total_food_n_drinks:.2f} EUR</b>.</p>
    <p>{'Wow, you are on fire! Keep it up!' if total_food_n_drinks < 10000 else 'Careful, you are spending a lot on food and drinks! Consider cooking at home more often.'}</p>
    <p>Best regards,<br>Your Marimo Copilot</p>""",   
    )


    return


if __name__ == "__main__":
    app.run()
