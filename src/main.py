import config
from client import WalletClient
from report import ReportBuilder
from email_sender import EmailSender


def main():
    print("Starting family budget reporting...")
    # initiate client and fetch records for the current month
    client = WalletClient(
        api_token=config.API_TOKEN,
        api_url=config.API_URL)
    records_current_month = client.get_records_current_month()
    print(f"\t ... fetched {len(records_current_month)} records for the current month.")

    # create report builder and generate report
    report_builder = ReportBuilder(
        records=records_current_month,
    )
    total_food_n_drinks = report_builder.current_month_food_spend()
    print(f"\t ... total food and drinks spend for the current month: {total_food_n_drinks:.2f} CZK")

    # send report via email
    email_sender = EmailSender(
        gmail_username=config.GMAIL_USERNAME,
        gmail_password=config.GMAIL_PASSWORD,
        gmail_receivers=config.GMAIL_RECEIVERS,
        monthly_food_n_drinks_threshold=config.MONTHLY_FOOD_N_DRINKS_THRESHOLD,
        total_food_n_drinks=total_food_n_drinks,
    )
    email_sender.send_report_via_email()
    print(f"\t ... report sent to: {', '.join(config.GMAIL_RECEIVERS)}")


if __name__ == "__main__":
    main()
