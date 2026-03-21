"""
Load trade alerts from Google Sheets. Service account, dynamic header detection.
Normalize ticker/strike/option_type/expiry/entry; reject invalid rows.
"""
from __future__ import annotations

import datetime as dt
import re
import time
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple

from . import config

logger = __import__("logging").getLogger(__name__)

# Must match inspect_google_sheet.py (tabs often have title rows before Date/Ticker/Entry header).
HEADER_SCAN_ROWS = 80

# Space out per-tab reads to reduce 429 "Read requests per minute per user" when many worksheets exist.
_SHEET_READ_INTERVAL_SEC = 1.25


def _get_all_values_throttled(ws, sheet_index: int):
    """Read all cells from a worksheet; throttle across tabs and retry on quota errors."""
    if sheet_index > 0:
        time.sleep(_SHEET_READ_INTERVAL_SEC)
    delay = 2.0
    for attempt in range(6):
        try:
            return ws.get_all_values()
        except Exception as e:
            err = str(e).lower()
            if ("429" in str(e) or "quota" in err) and attempt < 5:
                logger.warning(
                    "Sheets read backoff tab=%s attempt=%s: %s",
                    getattr(ws, "title", "?"),
                    attempt + 1,
                    e,
                )
                time.sleep(delay)
                delay = min(delay * 1.5, 90.0)
                continue
            raise


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
    # Do not treat size / P&L columns as take-profit levels
    if normalized in {"numbers", "number", "qty", "quantity", "contracts", "size"}:
        return False
    if any(x in normalized for x in ("profit", "loss", "remark", "status", "maxprofit")):
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
    """Match 'Exit' / 'Exit price' but not 'Expiry'."""
    c = str(header_cell).strip().lower()
    if "expiry" in c:
        return False
    n = _normalize_header(header_cell)
    if n == "exit" or (n.startswith("exit") and "expiry" not in c):
        return True
    if "exit" not in c:
        return False
    return True


def _find_lowest_before_tp_column_index(header_row: List[Any]) -> Optional[int]:
    """
    Optional column: lowest premium after entry before TP1 (manual journal / MAE).
    Aliases: 'Lowest Price Before TP1', 'Min Before TP1', 'MAE', etc.
    """
    for i, cell in enumerate(header_row):
        c = str(cell).strip().lower()
        if "expiry" in c:
            continue
        n = _normalize_header(cell)
        if n in ("lowestbeforetp1", "minbeforetp1", "lowbeforetp1", "minpricetp1", "lowestbeforetp"):
            return i
        if "lowest" in c and "tp" in c and "before" in c:
            return i
        if "min" in c and "before" in c and "tp" in c:
            return i
        if n == "mae":
            return i
        if "max adverse" in c:
            return i
        if "lowest price" in c and "before" in c:
            return i
    return None


def _header_looks_like_numbers_or_size_column(header_cell: Any) -> bool:
    """Entry → Numbers → Exit layouts: detect the middle 'Numbers' / contracts column."""
    n = _normalize_header(header_cell)
    if n in {"numbers", "number", "qty", "quantity", "contracts", "size"}:
        return True
    s = str(header_cell).strip().lower()
    return "position" in s and "%" in s


# Option premium band for TP detection (typical short-dated options)
TP_PREMIUM_MIN = 0.1
TP_PREMIUM_MAX = 100.0
_INFER_SAMPLE_ROWS = 10


def _find_exit_column_index_explicit(header_row: List[Any], col_entry: Optional[int]) -> Optional[int]:
    """Header-based Exit / Take Profit / TP1 — no guessing from Entry+1."""
    for i, cell in enumerate(header_row):
        if _column_has_exit_alias(cell):
            return i
    for i, cell in enumerate(header_row):
        n = _normalize_header(cell)
        if not n:
            continue
        if n in ("takeprofit", "takeprofits", "takeprofitlevels"):
            return i
        if n == "tp":
            return i
        if n.startswith("tp") and len(n) <= 4 and n[2:].isdigit():
            return i
    idx = _column_index(header_row, ["tp1", "tp2", "take profit", "target", "targets"])
    if idx is not None:
        return idx
    return None


def _find_exit_column_index_fallback(header_row: List[Any], col_entry: Optional[int]) -> Optional[int]:
    """Entry → Exit or Entry → Numbers → Exit when headers are minimal."""
    if col_entry is None:
        return None
    j1 = col_entry + 1
    j2 = col_entry + 2
    if j1 < len(header_row) and _header_looks_like_numbers_or_size_column(header_row[j1]):
        if j2 < len(header_row) and (
            _column_has_exit_alias(header_row[j2])
            or _normalize_header(header_row[j2]) == "exit"
        ):
            return j2
    if j1 < len(header_row):
        return j1
    return None


def _extract_tp_values_for_inference(cell_val: Any) -> List[float]:
    """Currency-like values in typical option premium range for exit-column scoring."""
    if cell_val is None or not str(cell_val).strip():
        return []
    s0 = str(cell_val).strip()
    if re.fullmatch(r"[\s\-]*\d+(?:\.\d+)?\s*%", s0):
        return []
    out: list[float] = []
    for m in re.finditer(r"\$\s*(\d+(?:\.\d+)?)", s0.replace(",", "")):
        try:
            v = float(m.group(1))
            if TP_PREMIUM_MIN <= v <= TP_PREMIUM_MAX:
                out.append(round(v, 4))
        except ValueError:
            continue
    if out:
        return out
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(?:%|\s+\d+\s*%|\s*$)", s0)
    if m:
        try:
            raw = m.group(1)
            v = float(raw)
            if "." not in raw and v < 10:
                return []
            if TP_PREMIUM_MIN <= v <= TP_PREMIUM_MAX:
                return [round(v, 4)]
        except ValueError:
            pass
    return []


def _infer_exit_column_from_sample_rows(
    rows: List[List[Any]],
    header_idx: int,
    col_entry: int,
    col_ticker: Optional[int],
    col_date: Optional[int],
    header_width: int,
) -> Optional[int]:
    """
    When there is no explicit Exit header, find the column with the most premium-like values
    in the first rows after the header (anchor + continuation rows).
    """
    start = header_idx + 1
    end = min(len(rows), header_idx + 1 + _INFER_SAMPLE_ROWS)
    scores: dict[int, int] = {}
    for ri in range(start, end):
        row = rows[ri]
        if not row:
            continue
        max_c = min(len(row), header_width)
        for c in range(max_c):
            if c == col_entry:
                continue
            if col_ticker is not None and c == col_ticker:
                continue
            if col_date is not None and c == col_date:
                continue
            vals = _extract_tp_values_for_inference(row[c] if c < len(row) else None)
            if vals:
                scores[c] = scores.get(c, 0) + len(vals)

    candidates = [c for c, s in scores.items() if s >= 2]
    if not candidates:
        # Sparse tabs: only one row in the sample may have exits — still pick best column
        singles = [(c, s) for c, s in scores.items() if s >= 1]
        if not singles:
            return None
        best_score = max(s for _, s in singles)
        contenders = [c for c, s in singles if s == best_score]
        if len(contenders) == 1:
            return contenders[0]
        return min(contenders, key=lambda c: abs(c - col_entry))
    best = max(scores[c] for c in candidates)
    top = [c for c in candidates if scores[c] == best]
    if len(top) == 1:
        return top[0]
    return min(top, key=lambda c: abs(c - col_entry))


def _find_exit_column_index(
    header_row: List[Any],
    col_entry: Optional[int] = None,
    sample_rows: Optional[List[List[Any]]] = None,
    header_idx: int = 0,
    col_ticker: Optional[int] = None,
    col_date: Optional[int] = None,
) -> Optional[int]:
    """
    Locate Exit / take-profit price column.
    1) Explicit header (Exit, Take Profit, TP1, …)
    2) Else infer from first ~10 data rows (most $ / decimal premiums in range)
    3) Else Entry+1 / Entry → Numbers → Exit fallback
    """
    explicit = _find_exit_column_index_explicit(header_row, col_entry)
    if explicit is not None:
        return explicit
    if (
        sample_rows
        and col_entry is not None
        and header_idx < len(sample_rows)
    ):
        inferred = _infer_exit_column_from_sample_rows(
            sample_rows,
            header_idx,
            col_entry,
            col_ticker,
            col_date,
            max(len(header_row), col_entry + 8),
        )
        if inferred is not None:
            return inferred
    return _find_exit_column_index_fallback(header_row, col_entry)


def _row_cell(row: List[Any], col: Optional[int]) -> str:
    if col is None or col >= len(row):
        return ""
    return str(row[col]).strip() if row[col] is not None else ""


def _extract_relaxed_tp_premiums_from_cell(val: Any) -> List[float]:
    """
    Bare decimals in [TP_PREMIUM_MIN, TP_PREMIUM_MAX] when $ not used (e.g. '4.70' or '4.70 20%').
    Requires a decimal part (x.xx) so Numbers column integers like contract counts are ignored.
    """
    if val is None or not str(val).strip():
        return []
    s0 = str(val).strip()
    if "$" in s0:
        return []
    if re.fullmatch(r"[\s\-]*\d+(?:\.\d+)?\s*%", s0):
        return []
    m = re.match(r"^\s*(\d+\.\d+)\s*(?:%|\s+\d+\s*%|\s*$)", s0)
    if not m:
        return []
    try:
        v = float(m.group(1))
    except ValueError:
        return []
    if TP_PREMIUM_MIN <= v <= TP_PREMIUM_MAX:
        return [round(v, 4)]
    return []


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
            raw = m2.group(1)
            v = float(raw)
            if "$" not in s0 and "." not in raw:
                # Bare integers without $ (e.g. "10", "20", "30") are contract counts,
                # not option premiums — reject all of them regardless of magnitude.
                return []
            if v >= 100:
                return []
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
    (sometimes with Date still filled). Only rows with a positive Entry cell count as anchors;
    otherwise multi-row TP scanning would stop at the first continuation line.
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

    # Ticker parses but no positive entry: continuation row (often repeats ticker + date with exits
    # on the same row) — must NOT be treated as a new anchor or multi-row TP collection stops early.
    return False


def _dedupe_sorted_prices(prices: List[float]) -> List[float]:
    seen: set[float] = set()
    out: list[float] = []
    for p in sorted(prices):
        r = round(p, 4)
        if r > 0 and r not in seen:
            seen.add(r)
            out.append(r)
    return out


def _dedupe_preserve_order(prices: List[float]) -> List[float]:
    """Unique exit prices in first-seen order (sheet / time order for TP1)."""
    seen: set[float] = set()
    out: list[float] = []
    for p in prices:
        r = round(p, 4)
        if r > 0 and r not in seen:
            seen.add(r)
            out.append(r)
    return out


def _find_profit_loss_column_index(header_row: List[Any]) -> Optional[int]:
    """Column like 'Profit/Loss' on March-style logs — used to skip TP extraction when status is Loss."""
    for i, h in enumerate(header_row):
        s = str(h).strip().lower()
        if "exit" in s and "expiry" not in s:
            continue
        if "profit" in s and "loss" in s:
            return i
        n = _normalize_header(h)
        if n in ("profitloss", "pl", "pnl"):
            return i
    return None


def _anchor_profit_loss_is_loss(rows: List[List[Any]], anchor_idx: int, header_row: List[Any]) -> bool:
    """If the anchor row marks Profit/Loss as plain 'Loss', do not attach take-profit targets."""
    col = _find_profit_loss_column_index(header_row)
    if col is None:
        return False
    row = rows[anchor_idx]
    if col >= len(row):
        return False
    cell = str(row[col]).strip().lower()
    if not cell:
        return False
    if cell == "loss":
        return True
    if cell.startswith("loss") and "profit" not in cell:
        return True
    return False


def _column_is_noise_for_tp_pattern_scan(header_cell: Any) -> bool:
    """
    Skip columns that never contain exit premiums (Date, Remarks, P/L summary).
    Do not skip Exit / Numbers / TP — even if header text contains '%' elsewhere.
    """
    if header_cell is None:
        return False
    if _column_has_exit_alias(header_cell):
        return False
    s = str(header_cell).strip().lower()
    if not s:
        return False
    n = _normalize_header(header_cell)
    if n == "date":
        return True
    if "remark" in s:
        return True
    if "max profit" in s or "max profit (loss)" in s:
        return True
    if "profit" in s and "loss" in s and "exit" not in s:
        return True
    if s == "direction" or n.startswith("direction"):
        return True
    return False


def _extract_tp_candidates_from_row_pattern(
    row: List[Any],
    header_row: List[Any],
    col_entry: int,
    col_min_before_tp1: Optional[int],
) -> List[float]:
    """
    Pattern-based: pull premium-like values from every cell except Entry (and manual MAE column).
    When the row is width-aligned with the header, skip known non-exit columns (Date, P/L, Remarks).
    Short / sparse continuation rows are not aligned — scan all cells so misaligned exits still parse.
    """
    out: list[float] = []
    aligned = len(row) >= len(header_row) and len(header_row) > 0
    for j, cell in enumerate(row):
        if j == col_entry:
            continue
        if col_min_before_tp1 is not None and j == col_min_before_tp1:
            continue
        if aligned and j < len(header_row) and _column_is_noise_for_tp_pattern_scan(header_row[j]):
            continue
        out.extend(_extract_exit_prices_from_cell(cell))
        out.extend(_extract_relaxed_tp_premiums_from_cell(cell))
    return out


def _filter_tp_candidates_for_long_option(candidates: Iterable[float], entry: float) -> List[float]:
    """
    Keep only values that are plausible take-profit *premiums* for a long option vs entry:
    strictly above entry, within typical premium band (excludes strike/index noise, huge P/L %).
    """
    out: list[float] = []
    for v in candidates:
        try:
            x = float(v)
        except (TypeError, ValueError):
            continue
        if x <= entry:
            continue
        if x < TP_PREMIUM_MIN or x > TP_PREMIUM_MAX:
            continue
        out.append(round(x, 4))
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
        cell = _row_cell(row, j)
        out.extend(_extract_exit_prices_from_cell(cell))
        out.extend(_extract_relaxed_tp_premiums_from_cell(cell))
    return out


def _collect_exit_prices_multi_row(
    rows: List[List[Any]],
    anchor_idx: int,
    col_ticker: int,
    col_entry: int,
    col_exit: Optional[int],
    header_idx: int,
    col_date: Optional[int] = None,
    entry_price: Optional[float] = None,
    col_min_before_tp1: Optional[int] = None,
) -> Tuple[List[float], List[float]]:
    """
    Block-based take-profit extraction (pattern + row relationships), not Exit-column-only.

    For the trade block starting at anchor_idx (anchor row + continuation rows until the next
    anchor), scan cells for premium-like values, skip Entry / MAE / noisy header columns when
    aligned, merge legacy TP1/TP2 header columns, then keep only values strictly above entry
    and within TP_PREMIUM_MIN..TP_PREMIUM_MAX.

    col_exit is still used by _normalize_sheet_rows for sparse row left-padding; extraction does
    not require a correct Exit index when entry_price is known.
    """
    if entry_price is None or entry_price <= 0:
        return [], []

    header_row = rows[header_idx] if header_idx < len(rows) else []
    if _anchor_profit_loss_is_loss(rows, anchor_idx, header_row):
        return [], []

    collected: list[float] = []

    j = anchor_idx
    while j < len(rows):
        row = rows[j]
        if j > anchor_idx and _is_anchor_row(row, col_ticker, col_entry, col_date):
            break
        collected.extend(
            _extract_tp_candidates_from_row_pattern(
                row, header_row, col_entry, col_min_before_tp1
            )
        )
        j += 1

    # Legacy: extra TP columns (TP1, TP2, …) on the header row
    if header_idx < len(rows):
        collected.extend(_parse_take_profit_values(rows[header_idx], rows[anchor_idx]))

    filtered = _filter_tp_candidates_for_long_option(collected, float(entry_price))
    ordered = _dedupe_preserve_order(filtered)
    sorted_unique = _dedupe_sorted_prices(filtered)
    return sorted_unique, ordered


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
    # Bare decimal premium (e.g. 4.70) or '4.70 20%' in first cell
    if re.match(r"^\s*\d+(?:\.\d+)?\s*$", fs):
        return True
    if re.match(r"^\s*\d+(?:\.\d+)?\s*%", fs):
        return True
    if re.match(r"^\s*\d+(?:\.\d+)?\s+\d+\s*%", fs):
        return True
    # Two cells: [decimal, percentage]
    if len(row) >= 2:
        a = str(row[0]).strip() if row[0] is not None else ""
        b = str(row[1]).strip() if row[1] is not None else ""
        if re.match(r"^\s*\d+(?:\.\d+)?\s*$", a) and re.fullmatch(r"\d+(?:\.\d+)?\s*%", b):
            return True
    return False


def _normalize_sheet_rows(
    rows: List[List[Any]],
    headers: List[Any],
    col_date: Optional[int],
    col_ticker: int,
    col_entry: int,
    col_exit: Optional[int],
    col_min_before_tp1: Optional[int] = None,
) -> List[List[Any]]:
    """
    gspread often omits **trailing** empty cells (right-pad) and sometimes **leading** empties
    on continuation rows (left-pad so Exit column index matches the header).
    """
    width = len(headers)
    for c in (col_date, col_ticker, col_entry, col_exit, col_min_before_tp1):
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
    col_min_before_tp1: Optional[int] = None,
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

        t_sorted, t_order = _collect_exit_prices_multi_row(
            rows,
            i,
            col_ticker,
            col_entry,
            col_exit,
            header_idx,
            col_date,
            entry_price=float(ep),
            col_min_before_tp1=col_min_before_tp1,
        )
        manual_min: Optional[float] = None
        if col_min_before_tp1 is not None and col_min_before_tp1 < len(row):
            manual_min = _clean_currency(row[col_min_before_tp1])

        last_emitted_ticker_raw = effective

        out.append({
            "ticker": ticker,
            "strike_price": strike_price,
            "option_type": option_type,
            "expiry_date": expiry_date,
            "entry_price": ep,
            "take_profit_targets": t_sorted,
            "take_profit_targets_order": t_order,
            "lowest_price_before_tp1_manual": manual_min,
            "trade_date": trade_date,
        })
        i += 1

    return out


def _merge_duplicate_trades(trades: List[dict]) -> List[dict]:
    """
    The same option can appear more than once per workbook (repeated blocks, summary lines,
    or the same alert pasted twice). SQLite UNIQUE is (ticker, strike, option_type, expiry, analyst)
    — not entry_price — so the last row synced used to wipe take_profit_targets if it parsed
    with no exits. Merge all exits for the same key (union, preserve first-seen order).
    """
    by_key: dict[tuple, dict] = {}
    order_keys: list[tuple] = []
    for t in trades:
        k = (
            t["ticker"],
            round(float(t["strike_price"]), 4),
            t["option_type"],
            t["expiry_date"],
            t["analyst_name"],
        )
        if k not in by_key:
            by_key[k] = dict(t)
            order_keys.append(k)
            continue
        cur = by_key[k]
        a = list(cur.get("take_profit_targets") or [])
        b = list(t.get("take_profit_targets") or [])
        oa = list(cur.get("take_profit_targets_order") or [])
        ob = list(t.get("take_profit_targets_order") or [])
        merged_sorted = _dedupe_sorted_prices(a + b)
        if not merged_sorted:
            merged_sorted = _dedupe_sorted_prices(a) if a else _dedupe_sorted_prices(b)
        merged_order = _dedupe_preserve_order(oa + ob)
        if not merged_order:
            merged_order = merged_sorted
        cur["take_profit_targets"] = merged_sorted
        cur["take_profit_targets_order"] = merged_order
        if cur.get("lowest_price_before_tp1_manual") is None and t.get("lowest_price_before_tp1_manual"):
            cur["lowest_price_before_tp1_manual"] = t["lowest_price_before_tp1_manual"]
        if cur.get("trade_date") is None and t.get("trade_date"):
            cur["trade_date"] = t["trade_date"]
    return [by_key[k] for k in order_keys]


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
    for idx, ws in enumerate(workbook.worksheets()):
        try:
            rows = _get_all_values_throttled(ws, idx)
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
        col_exit = _find_exit_column_index(
            headers,
            col_entry,
            sample_rows=rows,
            header_idx=header_idx,
            col_ticker=col_ticker,
            col_date=col_date,
        )
        col_min_before_tp1 = _find_lowest_before_tp_column_index(headers)

        if col_ticker is None or col_entry is None:
            continue

        if getattr(config, "SHEET_PARSE_DEBUG", False):
            logger.info(
                "sheet parse [%s]: col_date=%s col_ticker=%s col_entry=%s col_exit=%s",
                ws.title,
                col_date,
                col_ticker,
                col_entry,
                col_exit,
            )

        rows = _normalize_sheet_rows(
            rows, headers, col_date, col_ticker, col_entry, col_exit, col_min_before_tp1
        )

        for t in _trade_dicts_from_sheet_rows(
            rows, header_idx, col_date, col_ticker, col_entry, col_exit, col_min_before_tp1
        ):
            if getattr(config, "SHEET_PARSE_DEBUG", False):
                logger.info(
                    "sheet parse [%s]: ticker=%s strike=%s entry=%s TPs=%s order=%s",
                    ws.title,
                    t.get("ticker"),
                    t.get("strike_price"),
                    t.get("entry_price"),
                    t.get("take_profit_targets"),
                    t.get("take_profit_targets_order"),
                )
            out.append({**t, "analyst_name": (ws.title or "").strip()})
    return _merge_duplicate_trades(out)


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

    for idx, ws in enumerate(workbook.worksheets()):
        try:
            rows = _get_all_values_throttled(ws, idx)
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
        col_exit = _find_exit_column_index(
            headers,
            col_entry,
            sample_rows=rows,
            header_idx=header_idx,
            col_ticker=col_ticker,
            col_date=col_date,
        )
        col_min_before_tp1 = _find_lowest_before_tp_column_index(headers)
        if col_ticker is None or col_entry is None:
            out_sheets.append({"name": ws.title, "trades": [], "skip_reason": "Missing Ticker or Entry column"})
            continue

        rows = _normalize_sheet_rows(
            rows, headers, col_date, col_ticker, col_entry, col_exit, col_min_before_tp1
        )

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
            t_sorted, t_order = _collect_exit_prices_multi_row(
                rows,
                anchor_idx,
                col_ticker,
                col_entry,
                col_exit,
                header_idx,
                col_date,
                entry_price=float(ep),
                col_min_before_tp1=col_min_before_tp1,
            )
            manual_min: Optional[float] = None
            if col_min_before_tp1 is not None and col_min_before_tp1 < len(rows[anchor_idx]):
                manual_min = _clean_currency(rows[anchor_idx][col_min_before_tp1])

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
                        "take_profit_targets": t_sorted,
                        "take_profit_targets_order": t_order,
                        "lowest_price_before_tp1_manual": manual_min,
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
                        "take_profit_targets": t_sorted,
                        "take_profit_targets_order": t_order,
                        "lowest_price_before_tp1_manual": manual_min,
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
                    "take_profit_targets": t_sorted,
                    "take_profit_targets_order": t_order,
                    "lowest_price_before_tp1_manual": manual_min,
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
                    "take_profit_targets": t_sorted,
                    "take_profit_targets_order": t_order,
                    "lowest_price_before_tp1_manual": manual_min,
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
                "take_profit_targets": t_sorted,
                "take_profit_targets_order": t_order,
                "lowest_price_before_tp1_manual": manual_min,
                "status": "on_dashboard",
                "reason": "Active trade — tracked on dashboard",
            })
            i += 1

        out_sheets.append({"name": ws.title, "trades": sheet_trades})

    return {"error": None, "sheets": out_sheets}
