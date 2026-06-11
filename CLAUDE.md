# Family Budget Reporting — Project Memory

## Project Goals (priority order)
1. **Learn** — OOP, Polars, Marimo, GitHub Actions, Docker, `uv` by building
2. **SE habits** — clean code, tests, CI/CD, security, modularity, production standards
3. **Ship** — automated family budget report delivered via email

Teaching approach: ask questions and let the developer reason to answers. Never just give the solution. Bar the exception of code generation tasks.

---

## Current State
- Version: `0.0.1` tagged and live; v0.0.2 in progress on branch `setup-metrics`
- Pipeline runs daily, sends email with food & drinks spend for current month
- uv workflow confirmed working; Docker workflow removed
- Branch protection on main: PRs required, `test` status check must pass

---

## Tech Stack
- **Python**: 3.12 (pinned in `.python-version`)
- **Package manager**: `uv` — always use `uv run`, `uv add`, never `pip`
- **Data**: Polars (never Pandas)
- **API**: BudgetBakers Wallet REST API — Bearer auth, `/records` endpoint
- **Email**: redmail + Gmail app password
- **Secrets**: Bitwarden Secrets Manager → GitHub Actions via `bitwarden/sm-action@v2`
- **Prototyping**: Marimo notebooks in `notebooks/`

---

## Repository Structure
```
family-budget-reporting/
├── .github/
│   └── workflows/
│       ├── report-uv.yml        # daily cron 07:00 UTC, uv direct
│       └── tests.yml            # runs on every PR and push to non-main
├── notebooks/
│   ├── __marimo__/              # Marimo session state (auto-generated)
│   ├── layouts/                 # Marimo slide layouts (auto-generated)
│   └── prototyping.py           # Marimo notebook for prototyping
├── src/
│   ├── client.py                # WalletClient — API interaction
│   ├── config.py                # secrets validation, logging setup, constants
│   ├── email_sender.py          # EmailSender — email delivery via redmail
│   ├── report.py                # ReportBuilder — transformation + metrics
│   └── main.py                  # entry point — wires everything together
├── tests/
│   ├── conftest.py              # shared pytest fixtures (make_record)
│   ├── test_client.py           # WalletClient tests with mocking
│   └── test_report.py           # ReportBuilder tests
├── Dockerfile                   # production container, python:3.12-slim + uv
├── pyproject.toml               # prod + dev dependency groups
├── uv.lock                      # deterministic lock — always commit this
├── README.md
└── Claude.md                    # this file
```

---

## Architecture Decisions (do not relitigate without good reason)

- **`uv` over pip/venv** — deterministic, fast, reproducible
- **Polars over Pandas** — performance, expression API, no chained assignment issues
- **Redmail + Gmail** — already wired and working, no need to change for MVP
- **No Jinja2 yet** — f-strings sufficient until email template exceeds ~30 lines or needs loops
- **No Plotly/kaleido yet** — coming in v0.0.3
- **Dockerfile at repo root** — not in `.github/workflows/`
- **Single uv workflow** — Docker workflow was removed after comparison; uv is simpler and sufficient
- **`report-uv.yml` uses uv directly** — no Docker, secrets injected as env vars
- **Tests require no secrets** — mocks and fixtures only, no real API calls in tests

---

## Class Responsibilities (Single Responsibility Principle)

| Class | File | Responsibility |
|---|---|---|
| `WalletClient` | `client.py` | Fetch records from BudgetBakers API |
| `ReportBuilder` | `report.py` | Transform records into DataFrame, calculate metrics |
| `EmailSender` | `email_sender.py` | Assemble and send email |
| `config.py` | — | Load + validate secrets, set constants, configure logging |
| `main.py` | — | Wire everything together, entry point only |

---

## OOP Conventions Established
- Always use dependency injection — pass dependencies in, never reach for globals
- `__init__` receives what the class needs, stores as `self.x`
- Module-level constants in `config.py` are `ALL_CAPS`
- No hardcoded values inside classes — config belongs in `config.py` or passed as args
- `if __name__ == "__main__":` always wraps `main()` call in entry points

---

## OOP Concepts Covered (do not re-teach)
- Class, instance, `__init__`, `self`
- Attributes vs methods
- Single Responsibility Principle (the S in SOLID)
- Dependency injection
- Module-level variables and their problems

## OOP Concepts Still Ahead (teach when the project naturally needs them)
- Encapsulation — next natural opportunity
- `__str__` / `__repr__` — v0.0.2
- Dataclasses — v0.0.3 when `ReportData` object is needed
- Decorators — v0.0.4 with `tenacity` retry logic
- Inheritance + Abstract Base Classes — v0.5 when second report type is added

---

## SE Habits Established
- `logging` module — never `print()` in production code
- Secrets validation at startup in `config.py`
- `response.raise_for_status()` + response shape validation in API client
- `pytest` for all logic — fixtures in `conftest.py`, mocks via `unittest.mock`
- `uv add --dev` for dev dependencies, never in `[project.dependencies]`
- Dead comments removed, no leftover prototype code in `src/`

---

## Versioned Roadmap

### v0.0.2 — Richer report (CURRENT)
- Category breakdown table in email
- Month-over-month spend comparison
- Prototype in Marimo first, then productise
- Teaches: Polars `group_by`/`join`/`sort`, `__str__`/`__repr__`

### v0.0.3 — Charts
- Plotly trend chart as PNG in email via kaleido
- Marimo for interactive prototyping before productising
- Teaches: dataclasses (`ReportData`), Marimo reactive workflow

### v0.0.4 — Robustness
- Retry logic with `tenacity` (exponential backoff)
- Idempotency — prevent duplicate emails
- `mypy` in CI
- Teaches: decorators

### v0.5 — Multiple report types
- Weekly summary alongside monthly
- Teaches: inheritance, abstract base classes, GitHub Actions matrix builds

### v1.0 — Observability
- Structured JSON logging
- Failure notifications
- Auto-versioning on merge to main
- SOLID retrospective

---

## Development Workflow
1. Open new branch from main
2. Prototype in `notebooks/prototyping.py` using Marimo
3. Productise into `src/` once logic is confirmed
4. Write tests before or alongside code — never after
5. Push → `Tests` workflow runs automatically
6. Open PR → tests must pass, then merge

## IMPORTANT: Always run tests before suggesting a merge
```bash
uv run pytest tests/
```

---

## Key Commands
```bash
uv run src/main.py          # run the report locally
uv run pytest tests/        # run test suite
uv add <package>            # add production dependency
uv add --dev <package>      # add dev dependency
uv sync                     # sync environment to lock file
marimo edit notebooks/prototyping.py  # open Marimo notebook
```

---

## What NOT to do
- Never use `pip install` — always `uv add`
- Never use Pandas — Polars only
- Never hardcode secrets — always via environment variables
- Never push directly to main — always PR
- Never skip tests for "small" changes
- Never add complexity before it's needed (YAGNI)
- Never use `print()` in `src/` — use `logging`