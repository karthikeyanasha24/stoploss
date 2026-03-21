#!/usr/bin/env python3
"""
Debug helper: print Google Sheet column layout and FULL raw/normalized rows.

Run from the folder that contains app/ (e.g. version_b/version_b):

  python scripts/inspect_google_sheet.py
  python scripts/inspect_google_sheet.py --sheet "March WK 1"
  python scripts/inspect_google_sheet.py --sheet "Feb Week 4" --rows 50
  python scripts/inspect_google_sheet.py --dump-entire-sheet   # ignore header; print every row as-is

Requires .env with SPREADSHEET_ID and Google credentials (same as the main app).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Project root = parent of scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.chdir(ROOT)

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from app import config
from app.sheet_loader import (
    HEADER_SCAN_ROWS,
    _column_index,
    _find_exit_column_index,
    _find_lowest_before_tp_column_index,
    _header_looks_like_trade_row,
    _looks_like_sparse_exit_continuation,
    _normalize_sheet_rows,
    _get_client,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Google Sheet — full row dump for trade/Exit debugging")
    parser.add_argument("--sheet", type=str, default="", help="Worksheet title (default: all worksheets)")
    parser.add_argument(
        "--rows",
        type=int,
        default=0,
        help="How many data rows to print after header (0 = ALL rows to end of sheet)",
    )
    parser.add_argument(
        "--header-scan",
        type=int,
        default=HEADER_SCAN_ROWS,
        help="How many top rows to scan for Date/Ticker/Entry header row (same as sheet loader)",
    )
    parser.add_argument(
        "--dump-entire-sheet",
        action="store_true",
        help="Skip header logic; print every row in the tab with full cell lists (raw only)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="",
        help="Write output to this file as well as stdout (useful for huge sheets)",
    )
    args = parser.parse_args()

    if not config.SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID is not set in .env")
        sys.exit(1)

    out_lines: list[str] = []

    def emit(s: str = "") -> None:
        print(s)
        out_lines.append(s)

    client = _get_client()
    wb = client.open_by_key(config.SPREADSHEET_ID)
    worksheets = [wb.worksheet(args.sheet)] if args.sheet else wb.worksheets()

    for ws in worksheets:
        emit("=" * 100)
        emit(f"TAB: {ws.title!r}  (id={ws.id})  row_count={ws.row_count}  col_count={ws.col_count}")
        emit("=" * 100)
        rows = ws.get_all_values()
        if not rows:
            emit("(empty worksheet)\n")
            continue

        if args.dump_entire_sheet:
            emit(f"MODE: dump entire sheet — {len(rows)} rows (no normalization)\n")
            for i, row in enumerate(rows):
                emit(f"--- row_index={i}  len={len(row)}")
                emit(f"    FULL RAW = {row!r}")
                emit()
            emit()
            continue

        header_idx = None
        scan_upto = min(len(rows), max(1, args.header_scan))
        for i, row in enumerate(rows[:scan_upto]):
            if _header_looks_like_trade_row(row):
                header_idx = i
                break
        if header_idx is None:
            emit(f"No trade-like header in first {scan_upto} rows. Use --dump-entire-sheet to see raw grid.\n")
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
        col_min_bt = _find_lowest_before_tp_column_index(headers)

        emit(f"header_row_index={header_idx}")
        emit(f"len(headers)={len(headers)}  total_rows_in_range={len(rows)}")
        emit("Column map:")
        for j, h in enumerate(headers):
            emit(f"  [{j:2d}] {h!r}")
        emit()
        emit(
            f"col_date={col_date}  col_ticker={col_ticker}  col_entry={col_entry}  "
            f"col_exit={col_exit}  col_min_before_tp1={col_min_bt}"
        )
        emit()

        norm = _normalize_sheet_rows(
            rows, headers, col_date, col_ticker, col_entry, col_exit, col_min_bt
        )
        if args.rows <= 0:
            end_i = len(rows)
        else:
            end_i = min(len(rows), header_idx + 1 + args.rows)
        emit(
            f"Printing rows row_index {header_idx} .. {end_i - 1} "
            f"({'ALL' if args.rows <= 0 else args.rows} rows after header). "
            f"FULL raw and FULL norm (all columns).\n"
        )

        for i in range(header_idx, end_i):
            raw = rows[i]
            nrm = norm[i]
            sparse = _looks_like_sparse_exit_continuation(list(raw), col_exit) if col_exit is not None else False
            exit_raw = raw[col_exit] if col_exit is not None and col_exit < len(raw) else "<missing>"
            exit_nrm = nrm[col_exit] if col_exit is not None and col_exit < len(nrm) else "<missing>"
            emit(f"--- row_index={i}  len_raw={len(raw)}  len_norm={len(nrm)}  sparse_exit_continuation={sparse}")
            emit(f"    FULL RAW  = {raw!r}")
            emit(f"    FULL NORM = {nrm!r}")
            if col_exit is not None:
                emit(f"    Exit[col_exit={col_exit}] raw={exit_raw!r}  norm={exit_nrm!r}")
            emit()

        emit()

    emit("Done. If Exit is <missing> on raw rows but present after norm, the loader fix is working.")
    emit(
        "Optional column: add 'Lowest Price Before TP1' (or Min Before TP1 / MAE) for manual "
        "max-adverse-excursion when you do not have full price logs."
    )
    emit("After code changes, refresh all take_profit_targets in SQLite from the sheet:")
    emit("  POST http://localhost:8000/api/sync  (re-pulls Google Sheet and upserts TP levels for existing trades)")
    emit("  PowerShell:  Invoke-RestMethod -Uri http://localhost:8000/api/sync -Method POST")
    emit("  curl:        curl -X POST http://localhost:8000/api/sync")

    if args.output:
        out_path = Path(args.output)
        out_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
        print(f"\n[Wrote {len(out_lines)} lines to {out_path.resolve()}]", file=sys.stderr)


if __name__ == "__main__":
    main()
