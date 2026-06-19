# Family Budget Reporting

Automated pipeline that fetches expense records from the BudgetBakers Wallet API, calculates monthly spend by category, and emails a summary report to the family.

## How it works

```
BudgetBakers API → WalletClient → ReportBuilder → EmailSender → Gmail
```

Runs every Tuesday and Saturday at 18:00 UTC via GitHub Actions. Secrets are pulled from Bitwarden Secrets Manager at runtime — no credentials stored in the repo.

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/) — package manager
- BudgetBakers Wallet API token
- Gmail account with an [app password](https://support.google.com/accounts/answer/185833) enabled

## Setup

```bash
uv sync
```

## Configuration

Copy `.env.example` to `.env` and fill in the values (or export as environment variables):

| Variable | Description |
|---|---|
| `WALLET_API_TOKEN` | BudgetBakers Wallet Bearer token |
| `GMAIL_USERNAME` | Gmail address used to send the report |
| `GMAIL_APP_PASSWORD` | Gmail app password (not the account password) |

## Usage

```bash
uv run src/main.py       # send the report
uv run pytest tests/     # run the test suite
```

## Automated delivery

The GitHub Actions workflow (`report-uv.yml`) runs every Tuesday and Saturday at 18:00 UTC and can also be triggered manually via `workflow_dispatch`. Secrets are injected at runtime from Bitwarden — no secrets are stored in GitHub.

## Tech stack

- **Polars** — data transformation
- **redmail** — email delivery
- **uv** — dependency management and script runner
- **pytest** — testing (all tests run without real API calls)
