import logging
import polars as pl

logger = logging.getLogger(__name__)


class ReportBuilder:
    def __init__(self, records: list[dict]):
        self._records = records
        self._df = self._create_dataframe()

    def _create_dataframe(self) -> pl.DataFrame:
        return (
            pl.DataFrame(data=self._records)
            .with_columns(
                pl.col("category").struct.field("name").alias("category_name"),
                pl.col("category").struct.field("group").struct.field("name").alias("category_group"),
                pl.col("amount").struct.field("value").alias("amount"),
                pl.col("amount").struct.field("currencyCode").alias("currencyCode"),
            )
            .select(
                pl.col([
                    "id",
                    "recordDate",
                    "category_name",
                    "category_group",
                    "amount",
                    "currencyCode",
                    "recordType",
                ])
            )
        )

    def current_month_expenses_by_category(self) -> dict[str, float]:
        result = (
            self._df
            .filter(
                (pl.col("recordType") == "expense")
                & (pl.col("category_name") != "Transfer")
            )
            .group_by("category_group")
            .agg(pl.col("amount").sum().abs().alias("total_amount"))
            .sort("total_amount", descending=True)
        )
        breakdown = {row[0]: row[1] for row in result.iter_rows()}
        breakdown["Total"] = sum(breakdown.values())
        return breakdown

    def __repr__(self) -> str:
        return f"ReportBuilder(records={len(self._records)})"
