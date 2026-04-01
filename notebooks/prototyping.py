import marimo

__generated_with = "0.22.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    from dotenv import load_dotenv

    return load_dotenv, os


@app.cell
def _(load_dotenv, os):
    # load API token from .env file
    load_dotenv()
    API_TOKEN = os.environ['WALLET_API_TOKEN']

    # load API BASE URL
    API_URL = os.environ['WALLET_BASE_URL']
    return API_TOKEN, API_URL


@app.cell
def _(API_TOKEN, API_URL):
    from requests import get

    response = get(
        f"{API_URL}records",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
    )
    print(f"Status: {response.status_code}")
    print(response.text[:500])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
