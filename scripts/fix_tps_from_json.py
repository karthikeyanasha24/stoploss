"""
Standalone script: read all_sheets.json, parse TPs with the exact same logic
as sheet_loader.py, and write them to the LOCAL copy of the DB.
Then copy the fixed DB back to the mounted folder.
"""
from __future__ import annotations

import json
import sys
import os
import shutil

BASE = "/sessions/gallant-vibrant-goodall/mnt/version_b"
LOCAL_DB = "/sessions/gallant-vibrant-goodall/version_b_local.db"
REMOTE_DB = os.path.join(BASE, "data", "version_b.db")
JSON_PATH = os.path.join(BASE, "all_sheets.json")

sys.path.insert(0, BASE)
os.chdir(BASE)

# Patch DB path BEFORE importing config/database
import importlib
import app.config as cfg
cfg.DB_PATH = LOCAL_DB

from app.sheet_loader import (
    _header_looks_like_trade_row,
    _column_index,
    _find_exit_column_index,
    _find_lowest_before_tp_column_index,
    _normalize_sheet_rows,
    _trade_dicts_from_sheet_rows,
    _merge_duplicate_trades,
    HEADER_SCAN_ROWS,
)
from app.database import init_schema, _connect
import sqlite3, json as _json, datetime as dt


def _direct_write_tps(ticker, strike, option_type, expiry, analyst, tps, order, manual):
    """Write TPs directly — bypasses the 'preserve existing' logic in update_trade_sheet_fields."""
    from app.utils import normalize_take_profit_targets
    clean_tps = normalize_take_profit_targets(tps)
    clean_order = [round(float(x), 4) for x in (order or clean_tps)]
    with _connect() as conn:
        cur = conn.execute(
            """UPDATE trades
               SET take_profit_targets=?,
                   take_profit_targets_order=?,
                   lowest_price_before_tp1_manual=?
               WHERE ticker=? AND strike_price=? AND option_type=? AND expiry_date=? AND analyst_name=?""",
            (_json.dumps(clean_tps), _json.dumps(clean_order), manual,
             ticker, strike, option_type, expiry.isoformat(), analyst),
        )
    return cur.rowcount


def load_from_json():
    with open(JSON_PATH) as f:
        data = json.load(f)

    out = []
    for sheet in data["sheets"]:
        title = sheet.get("title", "").strip()
        rows = sheet.get("rows", [])
        if not rows:
            continue

        header_idx = None
        scan_upto = min(len(rows), HEADER_SCAN_ROWS)
        for i, row in enumerate(rows[:scan_upto]):
            if _header_looks_like_trade_row(row):
                header_idx = i
                break
        if header_idx is None:
            print(f"  [SKIP no header] {title}")
            continue

        headers = rows[header_idx]
        col_date   = _column_index(headers, ["date"])
        col_ticker = _column_index(headers, ["ticker", "ticker/strike", "strike"])
        col_entry  = _column_index(headers, ["entry"])
        col_exit   = _find_exit_column_index(
            headers,
            col_entry,
            sample_rows=rows,
            header_idx=header_idx,
            col_ticker=col_ticker,
            col_date=col_date,
        )
        col_min_before_tp1 = _find_lowest_before_tp_column_index(headers)

        if col_ticker is None or col_entry is None:
            print(f"  [SKIP no cols] {title}")
            continue

        rows_norm = _normalize_sheet_rows(
            rows, headers, col_date, col_ticker, col_entry, col_exit, col_min_before_tp1
        )

        for t in _trade_dicts_from_sheet_rows(
            rows_norm, header_idx, col_date, col_ticker, col_entry, col_exit, col_min_before_tp1
        ):
            out.append({**t, "analyst_name": title})

    return _merge_duplicate_trades(out)


def main():
    print(f"Using DB: {LOCAL_DB}")
    print(f"Source:   {JSON_PATH}\n")

    init_schema()

    trades = load_from_json()
    print(f"Parsed {len(trades)} trades from JSON\n")

    updated = 0
    not_in_db = 0

    for t in trades:
        tps    = t.get("take_profit_targets") or []
        order  = t.get("take_profit_targets_order") or []
        manual = t.get("lowest_price_before_tp1_manual")
        expiry = t["expiry_date"]

        # Check if the row exists in the local DB
        with _connect() as conn:
            row = conn.execute(
                "SELECT id FROM trades WHERE ticker=? AND strike_price=? AND option_type=? AND expiry_date=? AND analyst_name=?",
                (t["ticker"], t["strike_price"], t["option_type"], expiry.isoformat(), t["analyst_name"])
            ).fetchone()

        if not row:
            not_in_db += 1
            continue

        _direct_write_tps(
            ticker=t["ticker"],
            strike=t["strike_price"],
            option_type=t["option_type"],
            expiry=expiry,
            analyst=t["analyst_name"],
            tps=tps,
            order=order,
            manual=manual,
        )
        tp_str = str(tps) if tps else "[]"
        print(f"  OK  {t['analyst_name']:20} {t['ticker']:6} {t['strike_price']:7}  exp={expiry}  TPs={tp_str}")
        updated += 1

    print(f"\nUpdated {updated} trades ({not_in_db} not in DB — skipped)")

    # ── Copy fixed DB back to mounted folder ────────────────────────────────
    print(f"\nCopying fixed DB back to: {REMOTE_DB}")
    shutil.copy2(LOCAL_DB, REMOTE_DB)
    print("Done!")

    # ── Show final state ─────────────────────────────────────────────────────
    print("\n=== Final DB TP state ===")
    with _connect() as conn:
        rows = conn.execute(
            "SELECT analyst_name, ticker, strike_price, expiry_date, take_profit_targets FROM trades ORDER BY analyst_name, ticker"
        ).fetchall()
    for r in rows:
        tps = r[4]
        if tps and tps != "[]":
            print(f"  {r[0]:20} {r[1]:6} {r[2]:7}  exp={r[3]}  TPs={tps}")


if __name__ == "__main__":
    main()
