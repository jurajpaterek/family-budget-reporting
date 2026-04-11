from requests import get
from datetime import datetime


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
                response = get(
                    f"{self.api_url}/records", headers=headers, params=params
                ).json()
            except Exception as e:
                print(f"Error occurred while fetching records: {e}")
                raise e

            records.extend(response["records"])

            if "nextOffset" in response.keys():
                params["offset"] = response["nextOffset"]
            else:
                break

        return records

    def get_records_current_month(self):
        today = datetime.today()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        return self.get_records_in_range(start_date, end_date)
