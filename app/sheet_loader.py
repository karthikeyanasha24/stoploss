"""
Load trade alerts from Google Sheets. Service account, dynamic header detection.
Normalize ticker/strike/option_type/expiry/entry; reject invalid rows.
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any, List, Optional, Tuple

from . import config

logger = __import__("logging").getLogger(__name__)


def _get_client():
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    # Prefer credentials from env vars (no credentials.json file needed)
    info = config.GOOGLE_CREDENTIALS_FROM_ENV
    if info:
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    # Fallback to file path
    path = Path(config.GOOGLE_CREDENTIALS_PATH)
    if not path.is_file():
        raise FileNotFoundError(f"Credentials not found: {path}")
    creds = Credentials.from_service_account_file(str(path), scopes=scopes)
    return gspread.authorize(creds)


def _clean_currency(val: Any) -> Optional[float]:
    if val is None or (isinstance(val, float) and str(val) == "nan"):
        return None
    s = str(val).strip().replace("$", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _looks_like_futures(ticker_raw: str) -> bool:
    """Detect futures-style lines (e.g. 'ES Long 6035', 'ES Long 6110') that are not options."""
    if not ticker_raw or not str(ticker_raw).strip():
        return False
    s = re.sub(r"^Bought\s+", "", str(ticker_raw), flags=re.IGNORECASE).strip()
    # Pattern: Ticker + Long|Short + number (no C/P) — e.g. "ES Long 6035"
    if re.search(r"^[A-Za-z]+\s+(Long|Short)\s+\d+(?:\.\d+)?", s, re.IGNORECASE):
        return True
    # Known futures symbols with a number but no C/P (e.g. "ES 6035")
    if re.match(r"^(ES|NQ|MES|MNQ|CL|GC)\s+\d+(?:\.\d+)?", s, re.IGNORECASE):
        return True
    return False


def _parse_ticker_strike(s: str) -> Optional[Tuple[str, float, str, Optional[dt.date]]]:
    """Parse 'Bought SPX 6020C', 'QQQ 525C Exp:01/31/2025'. Returns (ticker, strike, type, expiry)."""
    if not s or not str(s).strip():
        return None
    s = re.sub(r"^Bought\s+", "", str(s), flags=re.IGNORECASE).strip()
    m = re.search(r"([A-Za-z]+)\s+(\d+)\s*([CP])", s, re.IGNORECASE)
    if not m:
        return None
    ticker = m.group(1).upper()
    strike = float(m.group(2))
    opt_type = "CALL" if m.group(3).upper() == "C" else "PUT"
    expiry = None
    em = re.search(r"Exp:\s*\(?(\d{1,2}/\d{1,2}/\d{2,4})\)?", s, re.IGNORECASE)
    if em:
        ds = em.group(1)
        try:
            if len(ds.split("/")[-1]) == 2:
                expiry = dt.datetime.strptime(ds, "%m/%d/%y").date()
            else:
                expiry = dt.datetime.strptime(ds, "%m/%d/%Y").date()
        except ValueError:
            pass
    return ticker, strike, opt_type, expiry


def _parse_date(val: Any) -> Optional[dt.date]:
    if val is None:
        return None
    s = str(val).strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _header_looks_like_trade_row(row: List[Any]) -> bool:
    combined = " ".join(str(c).lower() for c in row if c)
    return any(x in combined for x in ("date", "ticker", "entry", "strike", "expiry", "direction"))


def _column_index(header_row: List[Any], aliases: List[str]) -> Optional[int]:
    for i, cell in enumerate(header_row):
        c = str(cell).strip().lower()
        for a in aliases:
            if a in c:
                return i
    return None


def load_trades_from_sheet() -> List[dict]:
    """
    Connect to Google Sheet, read all worksheets, detect header, normalize rows.
    Returns list of dicts: ticker, strike_price, option_type, expiry_date, entry_price, trade_date, analyst_name.
    """
    if not config.SPREADSHEET_ID:
        logger.warning("SPREADSHEET_ID not set")
        return []

    try:
        client = _get_client()
        workbook = client.open_by_key(config.SPREADSHEET_ID)
    except Exception as e:
        logger.error("Failed to open spreadsheet: %s", e)
        return []

    out: List[dict] = []
    for ws in workbook.worksheets():
        try:
            rows = ws.get_all_values()
        except Exception as e:
            logger.warning("Failed to read sheet %s: %s", ws.title, e)
            continue
        if not rows:
            continue

        header_idx = None
        for i, row in enumerate(rows[:15]):
            if _header_looks_like_trade_row(row):
                header_idx = i
                break
        if header_idx is None:
            continue

        headers = rows[header_idx]
        col_date = _column_index(headers, ["date"])
        col_ticker = _column_index(headers, ["ticker", "ticker/strike", "strike"])
        col_entry = _column_index(headers, ["entry"])
        col_direction = _column_index(headers, ["direction", "call/put"])

        if col_ticker is None or col_entry is None:
            continue

        for row in rows[header_idx + 1 :]:
            if len(row) <= max(col_ticker, col_entry):
                continue
            entry_price = _clean_currency(row[col_entry] if col_entry < len(row) else None)
            if entry_price is None or entry_price <= 0:
                continue

            ticker_raw = row[col_ticker] if col_ticker < len(row) else ""
            parsed = _parse_ticker_strike(ticker_raw)
            if not parsed:
                continue
            ticker, strike_price, option_type, expiry_date = parsed
            if not expiry_date:
                continue

            trade_date = None
            if col_date is not None and col_date < len(row):
                trade_date = _parse_date(row[col_date])

            out.append({
                "ticker": ticker,
                "strike_price": strike_price,
                "option_type": option_type,
                "expiry_date": expiry_date,
                "entry_price": entry_price,
                "trade_date": trade_date,
                "analyst_name": ws.title,
            })
    return out


def load_all_trades_from_sheet_verbose() -> dict:
    """
    Load all trades from all worksheets with status and reason.
    Returns: { sheets: [ { name, trades: [ { ticker_raw, ticker, strike, option_type, expiry_date, entry_price, status, reason } ] } ] }
    """
    if not config.SPREADSHEET_ID:
        return {"error": "SPREADSHEET_ID not set", "sheets": []}

    try:
        client = _get_client()
        workbook = client.open_by_key(config.SPREADSHEET_ID)
    except Exception as e:
        return {"error": str(e), "sheets": []}

    today = dt.date.today()
    out_sheets = []

    for ws in workbook.worksheets():
        try:
            rows = ws.get_all_values()
        except Exception as e:
            out_sheets.append({"name": ws.title, "error": str(e), "trades": []})
            continue
        if not rows:
            out_sheets.append({"name": ws.title, "trades": []})
            continue

        header_idx = None
        for i, row in enumerate(rows[:15]):
            if _header_looks_like_trade_row(row):
                header_idx = i
                break
        if header_idx is None:
            out_sheets.append({"name": ws.title, "trades": [], "skip_reason": "No trade-like header found"})
            continue

        headers = rows[header_idx]
        col_date = _column_index(headers, ["date"])
        col_ticker = _column_index(headers, ["ticker", "ticker/strike", "strike"])
        col_entry = _column_index(headers, ["entry"])
        if col_ticker is None or col_entry is None:
            out_sheets.append({"name": ws.title, "trades": [], "skip_reason": "Missing Ticker or Entry column"})
            continue

        sheet_trades = []
        for row in rows[header_idx + 1:]:
            if len(row) <= max(col_ticker, col_entry):
                continue
            ticker_raw = (row[col_ticker] if col_ticker < len(row) else "").strip()
            if not ticker_raw:
                continue

            entry_price = _clean_currency(row[col_entry] if col_entry < len(row) else None)
            if entry_price is None or entry_price <= 0:
                sheet_trades.append({
                    "ticker_raw": ticker_raw,
                    "ticker": None,
                    "strike": None,
                    "option_type": None,
                    "expiry_date": None,
                    "entry_price": None,
                    "status": "invalid_entry",
                    "reason": "Missing or invalid entry price — ensure Entry column has a valid number",
                })
                continue

            parsed = _parse_ticker_strike(ticker_raw)
            if not parsed:
                if _looks_like_futures(ticker_raw):
                    sheet_trades.append({
                        "ticker_raw": ticker_raw,
                        "ticker": None,
                        "strike": None,
                        "option_type": None,
                        "expiry_date": None,
                        "entry_price": float(entry_price),
                        "status": "futures",
                        "reason": "Futures or index level — only options (e.g. SPX 6020C Exp:01/31/2025) are tracked on dashboard",
                    })
                else:
                    sheet_trades.append({
                        "ticker_raw": ticker_raw,
                        "ticker": None,
                        "strike": None,
                        "option_type": None,
                        "expiry_date": None,
                        "entry_price": float(entry_price),
                        "status": "parse_failed",
                        "reason": "Could not parse Ticker/Strike — use format like SPX 6020C or QQQ 525C Exp:01/31/2025 (C=Call, P=Put)",
                    })
                continue

            ticker, strike_price, option_type, expiry_date = parsed
            strike_f = float(strike_price) if strike_price is not None else None
            if not expiry_date:
                sheet_trades.append({
                    "ticker_raw": ticker_raw,
                    "ticker": ticker,
                    "strike": strike_f,
                    "option_type": option_type,
                    "expiry_date": None,
                    "entry_price": float(entry_price),
                    "status": "no_expiry",
                    "reason": "No expiry (Exp:) in Ticker/Strike — add Exp:MM/DD/YYYY to be tracked on dashboard",
                })
                continue

            if expiry_date < today:
                sheet_trades.append({
                    "ticker_raw": ticker_raw,
                    "ticker": ticker,
                    "strike": strike_f,
                    "option_type": option_type,
                    "expiry_date": expiry_date.isoformat(),
                    "entry_price": float(entry_price),
                    "status": "expired",
                    "reason": f"Expired on {expiry_date.isoformat()} — only active (non-expired) options appear on dashboard",
                })
                continue

            sheet_trades.append({
                "ticker_raw": ticker_raw,
                "ticker": ticker,
                "strike": strike_f,
                "option_type": option_type,
                "expiry_date": expiry_date.isoformat(),
                "entry_price": float(entry_price),
                "status": "on_dashboard",
                "reason": "Active trade — tracked on dashboard",
            })

        out_sheets.append({"name": ws.title, "trades": sheet_trades})

    return {"error": None, "sheets": out_sheets}
