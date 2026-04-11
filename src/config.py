from dotenv import load_dotenv
import os
import logging

# load secrets from .env file
load_dotenv()
API_TOKEN = os.getenv("WALLET_API_TOKEN")
API_URL = os.getenv("WALLET_BASE_URL")
GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# define constants
GMAIL_RECEIVERS = ["juraj.paterek@gmail.com"]
MONTHLY_FOOD_N_DRINKS_THRESHOLD = 10000 #CZK

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler])