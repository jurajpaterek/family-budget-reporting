import logging
from datetime import date, timedelta
import polars as pl

logger = logging.getLogger(__name__)


class ReportBuilder:
    def __init__(self, records: list[dict], obligatory_expenses: list[dict]):
        self._records = records
        self._obligatory_expenses = obligatory_expenses
        self._df = self._create_dataframe()

    def _build_obligatory_expression(self) -> pl.Expr:
        if not self._obligatory_expenses:
            return pl.lit(False)

        expressions = []
        for item in self._obligatory_expenses:
            expr = (
                pl.col("counterParty").str.contains(item["counterparty"])
                & pl.col("category_name").str.contains(item["category"])
            )
            if item["amount_min"] is not None and item["amount_max"] is not None:
                expr = expr & pl.col("amount").is_between(item["amount_min"], item["amount_max"])
            expressions.append(expr)

        result = expressions[0]
        for expr in expressions[1:]:
            result = result | expr
        return result

    def _create_dataframe(self) -> pl.DataFrame:
        return (
            pl.DataFrame(data=self._records)
            .with_columns(
                pl.col("category").struct.field("name").alias("category_name"),
                pl.col("category").struct.field("group").struct.field("name").alias("category_group"),
                pl.col("amount").struct.field("value").alias("amount"),
                pl.col("amount").struct.field("currencyCode").alias("currencyCode"),
                pl.col("labels").map_elements(
                    lambda labels: [] if labels is None or labels.is_empty() else [item["name"] for item in labels.to_list()],
                    return_dtype=pl.List(pl.Utf8),
                ).alias("labels_names"),
            )
            .with_columns(
                self._build_obligatory_expression().alias("obligatory_regular")
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
                    "counterParty",
                    "obligatory_regular",
                    "note",
                    "accountName",
                    "labels_names",
                ])
            )
        )

    def current_month_expenses_by_category(self) -> dict[str, float]:
        current_month = date.today().strftime("%Y-%m")
        all_expenses = self._df.filter(
              (pl.col("recordType") == "expense")
            & (pl.col("category_name") != "Transfer")
            & (pl.col("recordDate").str.slice(0, 7) == current_month)
            & ~pl.col("labels_names").list.contains("Refund/Refunded")
        )
        result = (
            all_expenses
            .filter(pl.col("obligatory_regular") == False)
            .group_by("category_group")
            .agg(pl.col("amount").sum().abs().alias("total_amount"))
            .sort("total_amount", descending=True)
        )
        breakdown = {row[0]: row[1] for row in result.iter_rows()}
        breakdown["Total"] = all_expenses.select(pl.col("amount").sum().abs()).item()
        return breakdown

    def current_month_obligatory_status(self) -> list[dict]:
        status = []
        for item in self._obligatory_expenses:
            expr = (
                pl.col("counterParty").str.contains(item["counterparty"])
                & pl.col("category_name").str.contains(item["category"])
                & (pl.col("recordType") == "expense")
            )
            if item["amount_min"] is not None and item["amount_max"] is not None:
                expr = expr & pl.col("amount").is_between(item["amount_min"], item["amount_max"])

            matches = self._df.filter(expr)
            if len(matches) > 0:
                status.append({"label": item["label"], "amount": abs(matches["amount"].sum()), "paid": True})
            else:
                status.append({"label": item["label"], "amount": None, "paid": False})
        return status

    def last_7_days_records(self) -> list[dict]:
        cutoff = (date.today() - timedelta(days=6)).isoformat()
        result = (
            self._df
            .filter(pl.col("recordDate").str.slice(0, 10) >= cutoff)
            .sort("recordDate", descending=True)
            .select(["recordDate", "category_name", "category_group", "accountName", "labels_names", "note", "amount", "recordType"])
        )
        return [
            {
                "date": row["recordDate"][:10],
                "category_name": row["category_name"],
                "category_group": row["category_group"],
                "account_name": row["accountName"],
                "labels_names": row["labels_names"],
                "note": row["note"],
                "amount": row["amount"],
                "record_type": row["recordType"],
            }
            for row in result.to_dicts()
        ]

    def __repr__(self) -> str:
        return f"ReportBuilder(records={len(self._records)})"
