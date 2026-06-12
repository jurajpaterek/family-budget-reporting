import logging
from requests import get
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class WalletClient:
    def __init__(self, api_token: str, api_url: str):
        self.api_token = api_token
        self.api_url = api_url

    def get_records_in_range(self, start_date, end_date):
        headers = {
            "Authorization": f"Bearer {self.api_token}",
        }
        params = {
            "recordDate": f"gte.{start_date},lte.{end_date}",
            "limit": "200",
            "offset": "0",
        }

        records = []

        while True:
            try:
                raw = get(f"{self.api_url}/records", headers=headers, params=params)
                raw.raise_for_status()
                response = raw.json()
            except Exception as e:
                logger.error(f"Error occurred while fetching records: {e}")
                raise e

            if "records" not in response:
                raise ValueError(f"Unexpected response format: 'records' key missing. Got: {response}")

            records.extend(response["records"])

            if "nextOffset" in response.keys():
                params["offset"] = response["nextOffset"]
            else:
                break

        return records

    def get_records_current_month(self):
        today = datetime.today()
        first_of_month = today.replace(day=1)
        seven_days_ago = today - timedelta(days=6)
        start = min(first_of_month, seven_days_ago)
        start_date = start.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        return self.get_records_in_range(start_date, end_date)

