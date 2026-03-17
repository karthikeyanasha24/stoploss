# Version B — Project Overview

**What This Project Does** — A concise document for alignment and sharing.

---

## End Goal & Purpose

**Version B** is a **forward stop-loss analysis system for option trades**. It helps you:

1. **Track option trades** loaded from a Google Sheet
2. **Monitor live option prices** during market hours
3. **Analyze stop-loss levels** (15%, 20%, 25%, 30%, 35%, 40%) after a configurable number of days
4. **Recommend a preferred stop-loss level** based on historical hit/survival rates

**It does NOT (currently):**

- Perform historical backtesting
- Execute live stop-loss orders
- Integrate with Interactive Brokers (IBKR) or any broker for trade execution

---

## How It Works

### 1. Data Source

- **Google Sheets** — Trades are loaded from a spreadsheet
- The sheet is configured via `SPREADSHEET_ID` and Google service account credentials
- Supported formats: e.g. `"Bought SPX 6020C"`, `"QQQ 525C Exp:01/31/2025"`
- Dynamic header detection for ticker, strike, option type (Call/Put), expiry, entry price

### 2. Price Tracking

- During **US market hours** (09:30–16:00 ET by default)
- **Every 60 seconds** (configurable via `POLLING_INTERVAL`):
  - Fetches live option price from market data API (Alpha Vantage, Massive, or Finnhub)
  - Logs price to SQLite
  - Updates trade stats: lowest price, highest price, max drawdown %

### 3. Stop-Loss Analysis

- **After 7 days** (configurable via `ANALYSIS_DAYS`) of tracking a trade:
  - Simulates each stop level (15%–40%)
  - Computes hit rate: what % of trades would have triggered that stop
  - Suggests a recommended stop % (e.g. lowest with &lt;50% hit rate)
  - Helps balance capital preservation vs. avoiding premature stop-outs

### 4. Dashboard & API

- **Web dashboard** (React SPA): trades list, trade details, analysis results, logs, settings
- **REST API** for programmatic access
- **Settings page** to configure API keys, spreadsheet, market hours, polling interval, credentials upload

---

## Tech Stack

| Layer    | Technology                         |
|----------|------------------------------------|
| Backend  | Python 3.11+, FastAPI, SQLite      |
| Frontend | React 19, TypeScript, Vite, Tailwind |
| Data     | Google Sheets (input), SQLite (storage) |
| Market   | Alpha Vantage, Massive, or Finnhub API |

---

## Configuration Highlights

| Setting         | Purpose                              |
|-----------------|--------------------------------------|
| `API_PROVIDER`  | Market data provider (alphavantage, massive, finnhub) |
| `API_KEY`       | Market data API key                  |
| `SPREADSHEET_ID`| Google Sheet with trades             |
| `ANALYSIS_DAYS` | Days before analysis runs (default: 7) |
| `POLLING_INTERVAL` | Seconds between price checks (default: 300) |
| `API_SERVE`     | If `true`, starts web server + dashboard |

---

## Running the Project

```bash
cd version_b
python -m app.main
```

**With dashboard & API:**

```bash
API_SERVE=true python -m app.main
```

---

## Project Layout (Key Parts)

```
version_b/
├── app/
│   ├── main.py          # Entry point, sync, scheduler, FastAPI
│   ├── sheet_loader.py  # Google Sheets → trades
│   ├── api_client.py    # Market data (AV, Massive, Finnhub)
│   ├── tracker.py       # Price fetching and logging
│   ├── analysis.py      # Stop-loss simulation and recommendation
│   ├── database.py      # SQLite (trades, price_logs, trade_stats)
│   └── config.py        # Environment and settings
├── frontend/            # React dashboard
├── data/                # DB, settings.json, credentials
└── logs/                # Application logs
```

---

## Alignment Notes

- **Market subscription** — User already pays for market data; the system uses Alpha Vantage, Massive, or Finnhub (configurable).
- **IBKR integration** — Not yet implemented; this project focuses on analysis and recommendations, not broker execution.
- **Forward-looking** — Analyzes trades from today onward, no historical backtesting.

---

*Last updated: February 2025*
