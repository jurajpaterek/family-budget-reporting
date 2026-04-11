import logging
from redmail import gmail

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(
        self,
        gmail_username: str,
        gmail_password: str,
        gmail_receivers: list[str],
        monthly_food_n_drinks_threshold: float,
        total_food_n_drinks: float,
    ):
        self.gmail_username = gmail_username
        self.gmail_password = gmail_password
        self.gmail_receivers = gmail_receivers
        self.monthly_food_n_drinks_threshold = monthly_food_n_drinks_threshold
        self.total_food_n_drinks = total_food_n_drinks

    def send_report_via_email(self):
        gmail.username = self.gmail_username
        gmail.password = self.gmail_password

        gmail.send(
            receivers=self.gmail_receivers,
            subject="Food & drinks current month report",
            html=f"""<p>Hi Juraj,</p>
                <p>Your total spend on food and drinks for the current month is <b>{self.total_food_n_drinks:.2f} CZK</b>.</p>
                <p>{"Wow, you are on fire! Keep it up!" if self.total_food_n_drinks < self.monthly_food_n_drinks_threshold else "Careful, you are spending a lot on food and drinks! Consider cooking at home more often."}</p>
                <p>Best regards,<br>Your Marimo Copilot</p>""",
        )
