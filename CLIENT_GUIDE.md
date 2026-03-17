# Stop-Loss Analysis System — Client Guide

## What This System Does

This is a **monitoring and analytics dashboard** for options trades. It:

1. **Tracks your trades** — Pulls active trades from your Google Sheet and monitors their option prices over time.
2. **Records price movement** — For each trade, it logs the lowest price, highest price, and max drawdown (how far the option dropped from your entry).
3. **Recommends stop-loss levels** — After enough data (7+ days by default), it analyzes which stop-loss % (e.g. 15%, 20%, 30%) would have been hit vs. survived, and suggests a balanced level.
4. **Displays everything in a dashboard** — Dashboard, Analysis, Logs, and Settings pages.

**Important:** This system does **not** place trades or execute orders. It only **monitors** and **analyzes**. You make your own trading decisions.

---

## Paper Trading vs. Live Trading

### Paper Trading (Sandbox)

- **What it is:** A fake-money environment for testing.
- **Data:** Uses Tradier’s **sandbox** API — paper account, delayed/demo prices.
- **Use when:** You want to test the system, add fake trades, or avoid touching real money.
- **Setup:** Enable "Paper Trading (Sandbox)" in Settings and use your **Tradier sandbox token**.

### Live Trading

- **What it is:** Real market data and real trading environment.
- **Data:** Uses Tradier’s **live** API — real-time prices, real account.
- **Use when:** You are ready to monitor real positions and want accurate prices and analysis.
- **Setup:** Disable "Paper Trading" in Settings and use your **Tradier production token**.

|                    | Paper Trading           | Live Trading              |
|--------------------|-------------------------|---------------------------|
| Token              | Sandbox token           | Production token          |
| Prices             | Demo/delayed            | Real-time                 |
| Risk               | No real money           | Real positions            |
| Best for           | Testing, demos          | Real monitoring/analysis  |

---

## How It Works (Step by Step)

1. **Connect Google Sheet**  
   Add your spreadsheet ID and credentials. Trades (ticker, strike, type, expiry, entry, analyst) are loaded from the sheet.

2. **Connect Tradier**  
   Add your Tradier API token in Settings. Choose Paper or Live based on whether you’re testing or monitoring real trades.

3. **Background tracking**  
   While the market is open, the system polls Tradier every few minutes (e.g. 5 min), gets option prices, and logs them.

4. **Dashboard**  
   - Total active trades, trades being tracked, trades ready for analysis  
   - Table of all active trades with drill-down to details

5. **Analysis page**  
   - Recommended stop %  
   - Table of stop levels vs. hit rate and survival rate  
   - Optional bar chart

6. **Logs**  
   Recent application logs for troubleshooting.

---

## Settings Overview

| Setting               | Purpose                                           |
|-----------------------|---------------------------------------------------|
| API Provider          | Must be **Tradier** for this setup                |
| Paper Trading         | ON = sandbox, OFF = live                          |
| API Key / Token       | Tradier token (sandbox or production)             |
| Spreadsheet ID        | Google Sheet containing your trades               |
| Polling Interval      | How often prices are fetched (seconds)            |
| Market Open/Close     | Times when tracking runs (e.g. 09:30–16:00 ET)    |
| Analysis Days         | Minimum days of tracking before analysis runs     |

---

## Getting Tradier Tokens

1. Sign up at [tradier.com](https://tradier.com).
2. Go to [API settings](https://web.tradier.com/user/api).
3. Copy:
   - **Sandbox token** → for Paper Trading (ON)
   - **Production token** → for Live (Paper Trading OFF)

Keep tokens private and never share them.

---

## Summary for Your Client

> "This dashboard tracks our options trades, records how their prices move over time, and uses that data to recommend stop-loss levels. We connect it to our Google Sheet and Tradier. We can run it in **paper mode** for testing or in **live mode** for real monitoring. It doesn’t place any trades; it only monitors and analyzes so we can make better decisions."
