from dotenv import load_dotenv
import os
import logging

# validate and load secrets from .env file
load_dotenv()
required = ["WALLET_API_TOKEN", "GMAIL_USERNAME", "GMAIL_APP_PASSWORD"]
missing = [key for key in required if not os.getenv(key)]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {missing}")

API_URL = "https://rest.budgetbakers.com/wallet/v1/api/"
API_TOKEN = os.getenv("WALLET_API_TOKEN")
GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# define constants
GMAIL_RECEIVERS = ["juraj.paterek@gmail.com"]
MONTHLY_TOTAL_BUDGET = 90000  # CZK

OBLIGATORY_EXPENSES = [
    {
        "label": "Rent",
        "counterparty": "2869677033/0800",
        "category": "Rent",
        "amount_min": None,
        "amount_max": None,
    },
    {
        "label": "Scholarship",
        "counterparty": "1035870393/5500",
        "category": "Education & development",
        "amount_min": -15000,
        "amount_max": -5000,
    },
]

# setup logging
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler])