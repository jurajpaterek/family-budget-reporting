import logging
import config
from client import WalletClient
from report import ReportBuilder
from email_sender import EmailSender

logger = logging.getLogger(__name__)


def main():
    logger.info("Starting family budget reporting...")

    client = WalletClient(api_token=config.API_TOKEN, api_url=config.API_URL)

    records = client.get_records_current_month()
    logger.info(f"\t ... fetched {len(records)} records for the current month.")

    report_builder = ReportBuilder(records=records, obligatory_expenses=config.OBLIGATORY_EXPENSES)
    logger.info(f"\t ... {report_builder!r}")

    expense_by_category = report_builder.current_month_expenses_by_category()
    logger.info(f"\t ... total spend: {expense_by_category.get('Total', 0):.2f} CZK across {len(expense_by_category) - 1} categories.")

    obligatory_status = report_builder.current_month_obligatory_status()
    paid_count = sum(1 for item in obligatory_status if item["paid"])
    logger.info(f"\t ... obligatory expenses: {paid_count}/{len(obligatory_status)} paid.")

    email_sender = EmailSender(
        gmail_username=config.GMAIL_USERNAME,
        gmail_password=config.GMAIL_PASSWORD,
        gmail_receivers=config.GMAIL_RECEIVERS,
        monthly_total_budget=config.MONTHLY_TOTAL_BUDGET,
        expense_by_category=expense_by_category,
        obligatory_status=obligatory_status,
    )
    email_sender.send_report_via_email()
    logger.info(f"\t ... report sent to: {', '.join(config.GMAIL_RECEIVERS)}")


if __name__ == "__main__":
    main()
