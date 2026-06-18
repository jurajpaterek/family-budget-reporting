import logging
from datetime import datetime
from redmail import gmail

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(
        self,
        gmail_username: str,
        gmail_password: str,
        gmail_receivers: list[str],
        monthly_total_budget: float,
        expense_by_category: dict[str, float],
        obligatory_status: list[dict],
        last_7_days: list[dict],
    ):
        self.gmail_username = gmail_username
        self.gmail_password = gmail_password
        self.gmail_receivers = gmail_receivers
        self.monthly_total_budget = monthly_total_budget
        self.expense_by_category = expense_by_category
        self.obligatory_status = obligatory_status
        self.last_7_days = last_7_days

    def _build_records_table(self) -> str:
        if not self.last_7_days:
            return "<p><i>No records in the last 7 days.</i></p>"

        rows = ""
        for r in self.last_7_days:
            color = "red" if r["record_type"] == "expense" else ("green" if r["record_type"] == "income" else "black")
            rows += (
                f"<tr>"
                f"<td>{r['date']}</td>"
                f"<td>{r['category_name']}</td>"
                f"<td>{r['category_group']}</td>"
                f"<td>{r['account_name']}</td>"
                f"<td>{', '.join(r['labels_names'])}</td>"
                f"<td>{r['note']}</td>"
                f"<td style='color:{color}'>{r['amount']:.2f} CZK</td>"
                f"</tr>"
            )

        return (
            "<table border='1' cellpadding='4' cellspacing='0' style='border-collapse:collapse;font-size:13px'>"
            "<tr style='background:#f0f0f0'>"
            "<th>Date</th><th>Category</th><th>Group</th><th>Account</th><th>Labels</th><th>Note</th><th>Amount</th>"
            "</tr>"
            + rows
            + "</table>"
            "<p style='font-size:13px'>More details available "
            "<a href='https://web.budgetbakers.com/records'>online</a>.</p>"
        )

    def send_report_via_email(self):
        gmail.username = self.gmail_username
        gmail.password = self.gmail_password

        month = datetime.today().strftime("%B")
        total = self.expense_by_category["Total"]

        category_rows = "".join([
            f"<li><b>{category}</b>: {amount:.2f} CZK</li>"
            for category, amount in self.expense_by_category.items()
            if category != "Total"
        ])

        obligatory_rows = "".join([
            f"<li><b>{item['label']}</b>: {item['amount']:.2f} CZK ✅</li>"
            if item["paid"]
            else f"<li><b>{item['label']}</b>: - ❌</li>"
            for item in self.obligatory_status
        ])

        gmail.send(
            receivers=self.gmail_receivers,
            subject=f"Ongoing expense report - {month}",
            html=f"""<p>Hi Juraj,</p>
                <p>Here is your expense breakdown for the month of {month}:</p>
                <p><b>Expenses by category</b> (obligatory expenses excluded):</p>
                <ul>{category_rows}</ul>
                <p><b>Regular obligatory expenses:</b></p>
                <ul>{obligatory_rows}</ul>
                <p><b>Total: {total:.2f} CZK</b></p>
                <p>{"Wow, you really went all out this month! Maybe consider cutting back on some expenses next month?" if total > self.monthly_total_budget else "Great job keeping your expenses in check this month! Keep it up!"}</p>
                <p><b>Recent transactions:</b></p>
                {self._build_records_table()}
                <p>Have a great day!</p>""",
        )
