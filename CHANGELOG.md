# Changelog

All notable changes to this project will be documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — v0.0.2
### Planned
- Category breakdown table in email
- Month-over-month spend comparison

## [0.0.1] — 2026-04-12
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
