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

# Must match inspect_google_sheet.py (tabs often have title rows before Date/Ticker/Entry header).
HEADER_SCAN_ROWS = 80


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
    """Parse 'Bought SPX 6020C', 'QQQ 525C Exp:01/31/2025', 'GOOGL 317.50C (Exp:...)'. Returns (ticker, strike, type, expiry)."""
    if not s or not str(s).strip():
        return None
    s = re.sub(r"^Bought\s+", "", str(s), flags=re.IGNORECASE).strip()
    # Allow decimal strikes: 317.50C, 42.50C
    m = re.search(r"([A-Za-z]+)\s+(\d+(?:\.\d+)?)\s*([CP])\b", s, re.IGNORECASE)
    if not m:
        return None
    ticker = m.group(1).upper()
    strike = float(m.group(2))
    opt_type = "CALL" if m.group(3).upper() == "C" else "PUT"
    expiry = None
    em = re.search(r"Exp[:;]\s*\(?(\d{1,2}/\d{1,2}/\d{2,4})\)?", s, re.IGNORECASE)
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


def _normalize_header(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def _is_take_profit_header(value: Any) -> bool:
    normalized = _normalize_header(value)
    if not normalized:
        return False
    return (
        normalized in {"tp", "target", "targets", "takeprofit", "takeprofits"}
        or normalized.startswith("tp")
        or normalized.startswith("target")
        or normalized.startswith("takeprofit")
    )


def _parse_take_profit_values(headers: List[Any], row: List[Any]) -> List[float]:
    targets: list[float] = []
    for idx, header in enumerate(headers):
        if not _is_take_profit_header(header) or idx >= len(row):
            continue
        cell = row[idx]
        if cell is None or not str(cell).strip():
            continue
        values = re.findall(r"\d+(?:\.\d+)?", str(cell).replace(",", ""))
        targets.extend(float(v) for v in values)
    # Preserve only unique positive values in ascending order.
    unique_targets = sorted({round(v, 4) for v in targets if v > 0})
    return unique_targets


def _column_has_exit_alias(header_cell: Any) -> bool:
    """Match 'Exit' but not 'Expiry'."""
    c = str(header_cell).strip().lower()
    if "exit" not in c:
        return False
    if "expiry" in c:
        return False
    return True


def _find_exit_column_index(header_row: List[Any], col_entry: Optional[int] = None) -> Optional[int]:
    """Locate Exit / take-profit price column. Many sheets use 'Take Profit' without the word 'exit'."""
    for i, cell in enumerate(header_row):
        if _column_has_exit_alias(cell):
            return i
    for i, cell in enumerate(header_row):
        n = _normalize_header(cell)
        if not n:
            continue
        # "Take Profit", "Take Profits", "TP", "TP1" — but not Ticker
        if n in ("takeprofit", "takeprofits", "takeprofitlevels"):
            return i
        if n == "tp":
            return i
        if n.startswith("tp") and len(n) <= 4 and n[2:].isdigit():
            return i
    # Legacy: separate TP columns or Target
    idx = _column_index(header_row, ["tp1", "tp2", "take profit", "target", "targets"])
    if idx is not None:
        return idx
    # Layout fallback: column immediately to the right of Entry (typical: Exit, then Numbers / %)
    if col_entry is not None:
        j = col_entry + 1
        if j < len(header_row):
            return j
    return None


def _row_cell(row: List[Any], col: Optional[int]) -> str:
    if col is None or col >= len(row):
        return ""
    return str(row[col]).strip() if row[col] is not None else ""


def _extract_exit_prices_from_cell(val: Any) -> List[float]:
    """Pull option take-profit prices from Exit column cells like '$2.75 (30%)' — ignore bare % numbers."""
    if val is None or not str(val).strip():
        return []
    s0 = str(val).strip()
    # Skip pure percentage cells (Numbers column)
    if re.fullmatch(r"[\s\-]*\d+(?:\.\d+)?\s*%", s0):
        return []
    s = s0.replace(",", "")
    out: list[float] = []
    # 1) Explicit $ premiums — avoids reading "30" from "(30%)"
    for m in re.finditer(r"\$\s*(\d+(?:\.\d+)?)", s):
        try:
            v = float(m.group(1))
            if 0 < v <= 50000:
                out.append(round(v, 4))
        except ValueError:
            continue
    if out:
        return out
    # 2) No $: bare decimal before % or whitespace (e.g. "2.75 30%")
    m2 = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(?:\(|%|$)", s)
    if m2:
        try:
            v = float(m2.group(1))
            if 0 < v <= 50000:
                return [round(v, 4)]
        except ValueError:
            pass
    return []


def _is_anchor_row(
    row: List[Any],
    col_ticker: int,
    col_entry: int,
    col_date: Optional[int] = None,
) -> bool:
    """
    A main trade row (not an Exit/Numbers continuation row).
    Continuation rows usually have an empty Ticker cell, or repeat the ticker with empty Entry
    and empty Date (merged cells). Anchors have a positive Entry and/or a Date when Entry is blank.
    """
    ticker_raw = _row_cell(row, col_ticker)
    if not ticker_raw:
        return False
    tl = ticker_raw.strip().lower()
    if tl in ("ticker/strike", "ticker", "strike", "date", "entry", "exit"):
        return False
    if "trade log" in tl:
        return False

    ep = _clean_currency(_row_cell(row, col_entry))
    if ep is not None and ep > 0:
        return True

    parsed = _parse_ticker_strike(ticker_raw)
    if parsed is None:
        return False

    # Parsed ticker but no Entry: either invalid_entry (has Date) or merged continuation (no Date)
    if col_date is not None:
        return bool(_row_cell(row, col_date).strip())
    return True


def _dedupe_sorted_prices(prices: List[float]) -> List[float]:
    seen: set[float] = set()
    out: list[float] = []
    for p in sorted(prices):
        r = round(p, 4)
        if r > 0 and r not in seen:
            seen.add(r)
            out.append(r)
    return out


def _exit_prices_fallback_cells_to_right_of_entry(row: List[Any], col_entry: int) -> List[float]:
    """
    If Exit column index is off by one or the sheet uses an unlabeled TP cell, premiums often sit
    immediately to the right of Entry (Exit, then Numbers/%). Scan a few cells without pulling
    unrelated columns far to the right.
    """
    out: list[float] = []
    start = col_entry + 1
    end = min(len(row), start + 8)
    for j in range(start, end):
        out.extend(_extract_exit_prices_from_cell(_row_cell(row, j)))
    return out


def _collect_exit_prices_multi_row(
    rows: List[List[Any]],
    anchor_idx: int,
    col_ticker: int,
    col_entry: int,
    col_exit: Optional[int],
    header_idx: int,
    col_date: Optional[int] = None,
) -> List[float]:
    """
    Collect Exit column prices for a trade whose anchor row is at anchor_idx.
    Trades span multiple rows: take profits are in the Exit column on the anchor row
    and continuation rows BELOW (Google Sheets layout). Rows above the anchor belong
    to the previous trade and must not be included.
    """
    if col_exit is None:
        return []

    collected: list[float] = []

    def _add_exit_cells_for_row(row: List[Any]) -> None:
        cell = _row_cell(row, col_exit)
        parsed = _extract_exit_prices_from_cell(cell) if cell else []
        if parsed:
            collected.extend(parsed)
        else:
            collected.extend(_exit_prices_fallback_cells_to_right_of_entry(row, col_entry))

    # Anchor row
    _add_exit_cells_for_row(rows[anchor_idx])

    # Rows below anchor until next anchor
    j = anchor_idx + 1
    while j < len(rows):
        row = rows[j]
        if _is_anchor_row(row, col_ticker, col_entry, col_date):
            break
        _add_exit_cells_for_row(row)
        j += 1

    # Also merge legacy same-row TP columns if present
    hdr = rows[header_idx] if header_idx < len(rows) else []
    collected.extend(_parse_take_profit_values(hdr, rows[anchor_idx]))

    return _dedupe_sorted_prices(collected)


def _header_looks_like_trade_row(row: List[Any]) -> bool:
    combined = " ".join(str(c).lower() for c in row if c)
    return any(x in combined for x in ("date", "ticker", "entry", "strike", "expiry", "direction"))


def _column_index(header_row: List[Any], aliases: List[str]) -> Optional[int]:
    """
    Prefer exact normalized header matches; then substring matches with exclusions.
    Substring 'entry' must not match 'Re-entry' (mis-detects Entry column and shifts Exit).
    """
    alias_norms = [_normalize_header(a) for a in aliases if _normalize_header(a)]
    for i, cell in enumerate(header_row):
        n = _normalize_header(cell)
        for an in alias_norms:
            if n == an:
                return i
    for i, cell in enumerate(header_row):
        c = str(cell).strip().lower()
        for a in aliases:
            a = a.strip().lower()
            if not a:
                continue
            if a not in c:
                continue
            if a == "entry" and re.search(r"\bre-?\s*entry\b", c, re.IGNORECASE):
                continue
            return i
    return None


def _looks_like_sparse_exit_continuation(row: List[Any], col_exit: Optional[int]) -> bool:
    """
    Google Sheets often returns continuation rows as a *short* array like ['$10.50', '30%']
    with **no leading empty cells**. Right-padding puts $10.50 at index 0 instead of col_exit.
    Detect rows that should be left-padded so Exit lines up with the header Exit column.
    """
    if col_exit is None or not row:
        return False
    if len(row) >= col_exit + 1:
        return False
    fs = str(row[0]).strip() if row[0] is not None else ""
    if not fs:
        return False
    if _parse_date(fs) is not None:
        return False
    if re.match(r"^\s*Bought\s+", fs, re.IGNORECASE):
        return False
    if re.match(r"^(Loss|Profit|Stopped\s+out)\s*$", fs, re.IGNORECASE):
        return False
    # ES / futures $6,035 style — not option TP continuation
    v = _clean_currency(fs)
    if v is not None and v >= 3000:
        return False
    if re.match(r"^\$\s*[\d,]+(?:\.\d+)?", fs):
        return True
    return False


def _normalize_sheet_rows(
    rows: List[List[Any]],
    headers: List[Any],
    col_date: Optional[int],
    col_ticker: int,
    col_entry: int,
    col_exit: Optional[int],
) -> List[List[Any]]:
    """
    gspread often omits **trailing** empty cells (right-pad) and sometimes **leading** empties
    on continuation rows (left-pad so Exit column index matches the header).
    """
    width = len(headers)
    for c in (col_date, col_ticker, col_entry, col_exit):
        if c is not None:
            width = max(width, c + 1)
    out: List[List[Any]] = []
    for r in rows:
        row = list(r)
        if col_exit is not None and _looks_like_sparse_exit_continuation(row, col_exit):
            row = [""] * col_exit + row
        if len(row) < width:
            row.extend([""] * (width - len(row)))
        out.append(row)
    return out


def _trade_dicts_from_sheet_rows(
    rows: List[List[Any]],
    header_idx: int,
    col_date: Optional[int],
    col_ticker: int,
    col_entry: int,
    col_exit: Optional[int],
) -> List[dict]:
    """
    Walk normalized rows and emit one dict per option trade.

    Many tabs split one alert across rows: 'Bought QQQ 630C' → 'Exp; 12/31/2025' → row with
    Date + Entry + Exit but **empty Ticker cell**. We carry pending ticker text forward and
    reuse the last emitted ticker for orphan rows that only add another entry (same chain).
    """
    out: List[dict] = []
    pending_parts: List[str] = []
    last_emitted_ticker_raw: Optional[str] = None

    i = header_idx + 1
    while i < len(rows):
        row = rows[i]
        max_col = max(col_ticker, col_entry)
        if len(row) <= max_col:
            i += 1
            continue

        tr = _row_cell(row, col_ticker).strip()
        ep = _clean_currency(row[col_entry] if col_entry < len(row) else None)

        # Expiry continuation in the ticker column (e.g. "Exp: 12/26/2025" or "Exp; 12/31/2025")
        if tr and re.match(r"(?i)^exp[:;]", tr):
            if pending_parts:
                pending_parts.append(tr)
            i += 1
            continue

        # Option line on its own row (no entry on this row) — start/refresh pending ticker
        if tr and _parse_ticker_strike(tr) and (ep is None or ep <= 0):
            pending_parts = [tr]
            i += 1
            continue

        if ep is None or ep <= 0:
            i += 1
            continue

        had_pending_for_empty_ticker = (not tr) and bool(pending_parts)
        # Must be computed before clearing pending_parts on full ticker+entry rows
        can_split_row = (not tr) and (
            bool(pending_parts) or bool(last_emitted_ticker_raw)
        )

        # Full row with ticker + entry — drop stale split state from a prior block
        if tr and ep > 0:
            pending_parts = []

        effective = tr if tr else ""
        if not effective:
            if pending_parts:
                effective = " ".join(pending_parts)
            elif last_emitted_ticker_raw:
                effective = last_emitted_ticker_raw

        if not effective:
            i += 1
            continue

        is_anchor = _is_anchor_row(row, col_ticker, col_entry, col_date)
        if not is_anchor and not can_split_row:
            i += 1
            continue

        parsed = _parse_ticker_strike(effective)
        if not parsed:
            if had_pending_for_empty_ticker:
                pending_parts = []
            i += 1
            continue
        ticker, strike_price, option_type, expiry_date = parsed
        if not expiry_date:
            if had_pending_for_empty_ticker:
                pending_parts = []
            i += 1
            continue

        if had_pending_for_empty_ticker:
            pending_parts = []

        trade_date = None
        if col_date is not None and col_date < len(row):
            trade_date = _parse_date(row[col_date])

        take_profit_targets = _collect_exit_prices_multi_row(
            rows, i, col_ticker, col_entry, col_exit, header_idx, col_date
        )

        last_emitted_ticker_raw = effective

        out.append({
            "ticker": ticker,
            "strike_price": strike_price,
            "option_type": option_type,
            "expiry_date": expiry_date,
            "entry_price": ep,
            "take_profit_targets": take_profit_targets,
            "trade_date": trade_date,
        })
        i += 1

    return out


def load_trades_from_sheet() -> List[dict]:
    """
    Connect to Google Sheet, read all worksheets, detect header, normalize rows.
    Returns list of dicts: ticker, strike_price, option_type, expiry_date, entry_price,
    take_profit_targets, trade_date, analyst_name.
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
        scan_upto = min(len(rows), HEADER_SCAN_ROWS)
        for i, row in enumerate(rows[:scan_upto]):
            if _header_looks_like_trade_row(row):
                header_idx = i
                break
        if header_idx is None:
            logger.warning("No trade-like header in first %d rows of sheet %s — skipping tab", scan_upto, ws.title)
            continue

        headers = rows[header_idx]
        col_date = _column_index(headers, ["date"])
        col_ticker = _column_index(headers, ["ticker", "ticker/strike", "strike"])
        col_entry = _column_index(headers, ["entry"])
        col_exit = _find_exit_column_index(headers, col_entry)

        if col_ticker is None or col_entry is None:
            continue

        rows = _normalize_sheet_rows(rows, headers, col_date, col_ticker, col_entry, col_exit)

        for t in _trade_dicts_from_sheet_rows(
            rows, header_idx, col_date, col_ticker, col_entry, col_exit
        ):
            out.append({**t, "analyst_name": ws.title})
    return out


def load_all_trades_from_sheet_verbose() -> dict:
    """
    Load all trades from all worksheets with status and reason.
    Returns: { sheets: [ { name, trades: [ { ticker_raw, ticker, strike, option_type,
    expiry_date, entry_price, take_profit_targets, status, reason } ] } ] }
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
        scan_upto = min(len(rows), HEADER_SCAN_ROWS)
        for i, row in enumerate(rows[:scan_upto]):
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
        col_exit = _find_exit_column_index(headers, col_entry)
        if col_ticker is None or col_entry is None:
            out_sheets.append({"name": ws.title, "trades": [], "skip_reason": "Missing Ticker or Entry column"})
            continue

        rows = _normalize_sheet_rows(rows, headers, col_date, col_ticker, col_entry, col_exit)

        sheet_trades = []
        pending_parts: List[str] = []
        last_emitted_ticker_raw: Optional[str] = None

        i = header_idx + 1
        while i < len(rows):
            row = rows[i]
            if len(row) <= max(col_ticker, col_entry):
                i += 1
                continue

            tr = _row_cell(row, col_ticker).strip()
            ep = _clean_currency(row[col_entry] if col_entry < len(row) else None)

            if tr and re.match(r"(?i)^exp[:;]", tr):
                if pending_parts:
                    pending_parts.append(tr)
                i += 1
                continue

            if tr and _parse_ticker_strike(tr) and (ep is None or ep <= 0):
                pending_parts = [tr]
                i += 1
                continue

            if ep is None or ep <= 0:
                i += 1
                continue

            had_pending_for_empty_ticker = (not tr) and bool(pending_parts)
            can_split_row = (not tr) and (
                bool(pending_parts) or bool(last_emitted_ticker_raw)
            )

            if tr and ep > 0:
                pending_parts = []

            effective = tr if tr else ""
            if not effective:
                if pending_parts:
                    effective = " ".join(pending_parts)
                elif last_emitted_ticker_raw:
                    effective = last_emitted_ticker_raw

            if not effective:
                i += 1
                continue

            is_anchor = _is_anchor_row(row, col_ticker, col_entry, col_date)
            if not is_anchor and not can_split_row:
                i += 1
                continue

            anchor_idx = i
            take_profit_targets = _collect_exit_prices_multi_row(
                rows, anchor_idx, col_ticker, col_entry, col_exit, header_idx, col_date
            )

            ticker_raw = effective
            parsed = _parse_ticker_strike(effective)
            if not parsed:
                if had_pending_for_empty_ticker:
                    pending_parts = []
                if _looks_like_futures(effective):
                    sheet_trades.append({
                        "ticker_raw": ticker_raw,
                        "ticker": None,
                        "strike": None,
                        "option_type": None,
                        "expiry_date": None,
                        "entry_price": float(ep),
                        "take_profit_targets": take_profit_targets,
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
                        "entry_price": float(ep),
                        "take_profit_targets": take_profit_targets,
                        "status": "parse_failed",
                        "reason": "Could not parse Ticker/Strike — use format like SPX 6020C or QQQ 525C Exp:01/31/2025 (C=Call, P=Put)",
                    })
                i += 1
                continue

            ticker, strike_price, option_type, expiry_date = parsed
            strike_f = float(strike_price) if strike_price is not None else None
            if not expiry_date:
                if had_pending_for_empty_ticker:
                    pending_parts = []
                sheet_trades.append({
                    "ticker_raw": ticker_raw,
                    "ticker": ticker,
                    "strike": strike_f,
                    "option_type": option_type,
                    "expiry_date": None,
                    "entry_price": float(ep),
                    "take_profit_targets": take_profit_targets,
                    "status": "no_expiry",
                    "reason": "No expiry (Exp:) in Ticker/Strike — add Exp:MM/DD/YYYY to be tracked on dashboard",
                })
                i += 1
                continue

            if had_pending_for_empty_ticker:
                pending_parts = []

            last_emitted_ticker_raw = effective

            if expiry_date < today:
                sheet_trades.append({
                    "ticker_raw": ticker_raw,
                    "ticker": ticker,
                    "strike": strike_f,
                    "option_type": option_type,
                    "expiry_date": expiry_date.isoformat(),
                    "entry_price": float(ep),
                    "take_profit_targets": take_profit_targets,
                    "status": "expired",
                    "reason": f"Expired on {expiry_date.isoformat()} — only active (non-expired) options appear on dashboard",
                })
                i += 1
                continue

            sheet_trades.append({
                "ticker_raw": ticker_raw,
                "ticker": ticker,
                "strike": strike_f,
                "option_type": option_type,
                "expiry_date": expiry_date.isoformat(),
                "entry_price": float(ep),
                "take_profit_targets": take_profit_targets,
                "status": "on_dashboard",
                "reason": "Active trade — tracked on dashboard",
            })
            i += 1

        out_sheets.append({"name": ws.title, "trades": sheet_trades})

    return {"error": None, "sheets": out_sheets}
