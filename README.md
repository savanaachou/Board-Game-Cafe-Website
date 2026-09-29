# Drinks & Dice

![Tests](https://github.com/savanaachou/Board-Game-Cafe-Website/actions/workflows/tests.yml/badge.svg)

A full-stack reservation and ordering system for a fictional board game café, built with Flask and SQLite. Customers can create an account, sign in, browse the board game and drink menus, make a reservation (optionally reserving a specific game and pre-ordering a drink), and view or cancel their past reservations.

## Features

- **Accounts & auth** — password-based sign-up/sign-in, with passwords hashed (scrypt via Werkzeug) rather than stored in plaintext, and session-based login state.
- **Live board game & drink menus** — served from a normalized SQLite database, rendered client-side via fetch calls.
- **Reservations** — booking a table also lets you reserve an available board game and pre-order a drink; both are tied to the reservation through junction tables (`BoardGameOrders`, `MenuOrders`). Drinks are fully customizable at order time: sweetness (0-100%), hot/cold, ice level (cold only), and toppings (many-to-many via `Toppings`/`MenuOrderToppings`, so more toppings can be added later without a schema change), plus optional free-text special instructions.
- **Cancellation** — deleting a reservation releases any board game it had reserved and cleans up its linked order rows.
- **Relational integrity** — foreign keys are enforced (`PRAGMA foreign_keys = ON`); a customer can only view or cancel their own reservations.

## Tech stack

Python, Flask, SQLite3, vanilla JS/HTML/CSS (no frontend framework/build step).

## Project structure

```
boardGameCafe.py     Flask app: routes, auth, session handling
database.py           All SQL: schema, seeding, queries
helper.py              CSV parsing / type conversion for seed data
templates/             Jinja templates (sign-in, create-account, menu, account-info)
static/                CSS
tests/                  pytest suite (see Testing below)
.github/workflows/      CI: runs the test suite on every push
*.csv                  Seed data for board games, menu items, and demo customers/reservations
```

## Running locally

```bash
pip install -r requirements.txt
python boardGameCafe.py
```

Then open `http://127.0.0.1:5000`. On first run the app creates and seeds `cafe.db` automatically (this file is gitignored — delete it and restart the app any time to reset to seed data).

**Demo login:** customer ID `3`, password `dicebox2026` (or see `Customers.csv` for the other seeded accounts — all share that password). You can also just create a new account from the sign-in page.

## Testing

36 tests covering auth, session handling, board game/menu endpoints, reservation creation and cancellation (including the game-availability and topping-total logic), CSV seed-data parsing, and foreign key enforcement.

```bash
pip install -r requirements-dev.txt
pytest --cov=boardGameCafe --cov=database --cov=helper --cov-report=term-missing
```

Each test runs against its own temporary SQLite database (via the `DATABASE_PATH` environment variable), so tests never touch a real `cafe.db` and never leak state into each other. Runs automatically on every push via GitHub Actions (see `.github/workflows/tests.yml`).

## Deployment

Deployed on [Render](https://render.com)'s free tier as a standard web service:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn boardGameCafe:app`
- Environment variable: `SECRET_KEY` set to a random value (never commit this)

Tables are created/seeded automatically on startup if they don't already exist (`ensure_database()` in `boardGameCafe.py`), so no manual setup step is needed after deploy.

Two known trade-offs of the free tier, worth knowing if the live link feels slow: the instance spins down after 15 minutes of inactivity (first request after that takes ~30-50s to wake up), and the filesystem is ephemeral, so `cafe.db` resets to seed data on every redeploy.

## Notes

- `SECRET_KEY` defaults to a hardcoded dev value locally; always set a real environment variable when deploying.
- This started as a database-design exercise and has since been rebuilt into a standalone project — fixed several correctness bugs in the original (broken auth, un-committed writes, mismatched schema references, un-enforced foreign keys, a UI that collected reservation details it never saved).
