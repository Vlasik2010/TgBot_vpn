# VPN Sales Telegram Bot

A production-ready Telegram bot written in **Python&nbsp;3** that automates the sale and delivery of WireGuard VPN configurations to end-users.

---

## Features

* Modern, reliable [aiogram](https://github.com/aiogram/aiogram) asynchronous framework.
* Supports **Crypto Pay** (official TON-based Telegram payments).
* Fully automated WireGuard peer provisioning & revocation.
* Simple SQLite database (can be upgraded to PostgreSQL).
* Clean, modular codebase with type hints & pydantic settings.
* Docker-ready for effortless deployment.

## Quick start (local)

```bash
# 1. Clone repository
git clone <this-repo> vpn-bot
cd vpn-bot

# 2. Create & activate virtualenv (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy env template & fill in tokens / paths
cp .env.example .env
nano .env  # or your favourite editor

# 5. Initialise database (SQLite file will be created automatically)
alembic upgrade head  # optional – pre-generated migrations

# 6. Run the bot
python -m vpn_bot
```

## Deployment (Docker)

Provided `docker-compose.yml` launches the bot and a PostgreSQL instance:

```bash
docker compose up -d --build
```

> Make sure to edit `.env` and `docker-compose.yml` with real secrets before running in production.

## Folder structure

```
vpn_bot/
├── __init__.py
├── config.py          # pydantic settings
├── main.py            # entry-point
├── database.py        # SQLAlchemy engine/session
├── models.py          # ORM models
├── utils/
│   ├── wireguard.py   # WG peer management helpers
│   └── payment.py     # Crypto Pay API wrapper
├── handlers/
│   ├── __init__.py
│   ├── start.py       # /start & help messages
│   └── purchase.py    # buying flow
└── keyboards/
    └── inline.py      # inline keyboards
```

## Payments

The default implementation uses [Crypto Pay](https://t.me/CryptoBot) – an official Telegram mini-app for TON payments available worldwide (including Russia). You may plug in **Stripe**, **YooMoney**, **QIWI API**, or any other provider by replacing `vpn_bot/utils/payment.py`.

## WireGuard automation

`vpn_bot/utils/wireguard.py` manipulates peers via the `wg` CLI (present on most Linux distros). The account under which the bot runs must have sufficient privileges (usually `CAP_NET_ADMIN` or root). In production, run the bot on the same VPS as the WireGuard interface or expose the socket through [wg-access-server](https://github.com/freifunkMUC/wg-access-server).

## Security recommendations

1. **Run everything inside Docker** and drop unneeded capabilities.
2. Store secrets in environment variables or a secret manager.
3. Use HTTPS / SNI proxies if exposing anything to the Internet.

## License

MIT – feel free to use, modify, and profit 🚀
