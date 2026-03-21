#!/usr/bin/env python3
"""
Read the configured Google Spreadsheet and dump every worksheet with ALL cell data.

Uses the same credentials and SPREADSHEET_ID as the app (.env / settings).

Run from the project root that contains app/ (e.g. version_b/version_b):

  python scripts/dump_all_sheets.py
  python scripts/dump_all_sheets.py --format json -o all_sheets.json
  python scripts/dump_all_sheets.py --sheet "March WK 1"
  python scripts/dump_all_sheets.py --format json --pretty

Requires SPREADSHEET_ID and Google service account access to the sheet.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.chdir(ROOT)

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from app import config
from app.sheet_loader import _get_client


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dump all data from each worksheet in the Google Spreadsheet (raw grid)."
    )
    parser.add_argument(
        "--sheet",
        type=str,
        default="",
        help="Only this worksheet title (default: every worksheet).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "csv"),
        default="text",
        help="text = human-readable; json = one JSON object; csv = one CSV per sheet in a folder",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="",
        help="Write output here (stdout only if omitted for text; required for json/csv batch).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON (indent=2).",
    )
    args = parser.parse_args()

    if not config.SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID is not set (.env)", file=sys.stderr)
        sys.exit(1)

    client = _get_client()
    wb = client.open_by_key(config.SPREADSHEET_ID)
    worksheets = [wb.worksheet(args.sheet)] if args.sheet else wb.worksheets()

    if args.format == "json":
        payload = {
            "spreadsheet_id": config.SPREADSHEET_ID,
            "spreadsheet_title": wb.title,
            "sheets": [],
        }
        for ws in worksheets:
            rows = ws.get_all_values()
            payload["sheets"].append(
                {
                    "title": ws.title,
                    "worksheet_id": ws.id,
                    "row_count": ws.row_count,
                    "col_count": ws.col_count,
                    "num_rows_with_data": len(rows),
                    "rows": rows,
                }
            )
        text = json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None)
        if args.output:
            Path(args.output).write_text(text + "\n", encoding="utf-8")
            print(f"Wrote JSON to {Path(args.output).resolve()}", file=sys.stderr)
        else:
            print(text)
        return

    if args.format == "csv":
        out_dir = Path(args.output) if args.output else Path("sheet_dumps")
        out_dir.mkdir(parents=True, exist_ok=True)
        for ws in worksheets:
            rows = ws.get_all_values()
            safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in ws.title)[:80]
            path = out_dir / f"{safe_name}.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                for row in rows:
                    w.writerow(row)
            print(f"Wrote {len(rows)} rows -> {path.resolve()}", file=sys.stderr)
        return

    # text
    buf: list[str] = []

    def emit(s: str = "") -> None:
        buf.append(s)
        print(s)

    emit(f"Spreadsheet: {wb.title!r}")
    emit(f"ID: {config.SPREADSHEET_ID}")
    emit()

    for ws in worksheets:
        rows = ws.get_all_values()
        emit("=" * 100)
        emit(
            f"SHEET: {ws.title!r}  worksheet_id={ws.id}  "
            f"declared_rows={ws.row_count}  cols={ws.col_count}  "
            f"rows_returned_by_get_all_values={len(rows)}"
        )
        emit("=" * 100)
        if not rows:
            emit("(empty — no cells)")
            emit()
            continue
        for i, row in enumerate(rows):
            emit(f"[{i:5d}] ({len(row)} cells) {row!r}")
        emit()

    if args.output:
        Path(args.output).write_text("\n".join(buf) + "\n", encoding="utf-8")
        print(f"\n[Wrote {len(buf)} lines to {Path(args.output).resolve()}]", file=sys.stderr)


if __name__ == "__main__":
    main()
