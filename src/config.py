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
MONTHLY_FOOD_N_DRINKS_THRESHOLD = 10000 #CZK

# setup logging
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler])