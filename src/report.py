import polars as pl


class ReportBuilder:
    def __init__(
        self,
        records: list[dict],
    ):
        self.records = records
        self.df_records = self.create_dataframe()

    def create_dataframe(self):
        return (
            pl.DataFrame(data=self.records)
            .with_columns(
                pl.col("category").struct.field("name").alias("category_name"),
                pl.col("baseAmount").struct.field("currencyCode").alias("currencyCode"),
                pl.col("baseAmount").struct.field("value").alias("amount"),
            )
            .select(
                pl.col(
                    [
                        "id",
                        "recordDate",
                        "category_name",
                        "amount",
                        "currencyCode",
                        "recordType",
                        # "note",
                        # "recordState",
                        # "paymentType",
                        # "payee",
                        # "payer",
                        # "accountId",
                        # "baseAmount",
                        # "category",
                        # "createdAt",
                        # "updatedAt",
                    ]
                )
            )
        )
    
    def current_month_food_spend(self) -> float:
        food_n_drinks = ["Bar cafe", "Restaurants & fast food", "Groceries"]

        return self.df_records.filter(
            pl.col("recordType").str.contains("expense")
            & pl.col("category_name").is_in(food_n_drinks)
        ).select(pl.col("amount").abs().sum().alias("total_amount"))["total_amount"][0]
