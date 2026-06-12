# Changelog

All notable changes to this project will be documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.1]
### Added
- Obligatory expense tracking: rent and scholarship separated from discretionary breakdown
- Each obligatory item shows ✅ with amount if paid this month, ❌ if not detected
- `OBLIGATORY_EXPENSES` config constant with counterparty + category matching criteria

### Changed
- `current_month_expenses_by_category()` excludes obligatory from category groups; Total includes them
- Cron schedule changed temporarily back to daily for debugging purpose and time updated to 18:00 UTC
- Email subject changed to `Ongoing expense report - {Month}`

## [0.2.0] — 2026-06-11
### Added
- Category breakdown by group in email (Food & Drinks, Shopping, Housing, etc.), sorted by spend descending
- `README.md`, `CHANGELOG.md`, `.env.example`
- `__repr__` on `ReportBuilder`
- Encapsulation: internal DataFrame `_df` is private

### Changed
- Category groups now read directly from `category.group.name` in each record — separate `/categories` API call removed
- Cron schedule changed from daily to Tuesdays and Saturdays at 07:00 UTC
- Monthly budget threshold raised to 90,000 CZK (was 10,000)
- Email subject is now dynamic: `{Month} spendings - ongoing report`

## [0.1.0] — 2026-04-13
### Added
- Monthly report pipeline: fetch records from BudgetBakers API → calculate food & drinks spend → send email
- `WalletClient` — Bearer auth, `/records` endpoint, response validation
- `ReportBuilder` — Polars-based transformation and metrics
- `EmailSender` — HTML email delivery via redmail + Gmail
- `config.py` — secrets validation at startup, logging setup, module-level constants
- GitHub Actions workflow (`report-uv.yml`) — daily cron at 07:00 UTC, secrets from Bitwarden
- Dockerfile — `python:3.12-slim` + uv production container
- pytest suite — `WalletClient` and `ReportBuilder` tests, all mocked (no real API calls)

### Removed
- Docker workflow (`report-docker.yml`) — uv workflow is simpler and sufficient
