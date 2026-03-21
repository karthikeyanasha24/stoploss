"""
Version B: Forward Stop-Loss Analysis System.
Syncs trades from Google Sheets, tracks prices every 60s, runs stop-% analysis after 7 days.
Optional FastAPI: GET /trades, GET /analysis, GET /stats/{trade_id}
"""
from __future__ import annotations

import datetime as dt
import logging
import os
import sys
from pathlib import Path

# Allow running as script or module
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "app"

from starlette.requests import Request

from . import config
from .api_client import MarketDataAPI
from .database import init_schema, insert_trade
from .logger import LOG_BUFFER, configure_logging
from .scheduler import create_scheduler
from .sheet_loader import load_trades_from_sheet, load_all_trades_from_sheet_verbose

logger = logging.getLogger(__name__)


def sync_sheet_to_db() -> int:
    """Load trades from Google Sheet, insert new ones. Returns count added."""
    trades = load_trades_from_sheet()
    logger.info("--------------------------------------------------------------------------------Loaded %d candidate trades from Google Sheet", len(trades))
    added = 0
    today = dt.date.today()
    for t in trades:
        tps = t.get("take_profit_targets") or []
        logger.info(
            "Sheet row -> ticker=%s strike=%s type=%s expiry=%s entry=%s trade_date=%s analyst=%s take_profits=%s",
            t.get("ticker"),
            t.get("strike_price"),
            t.get("option_type"),
            t.get("expiry_date"),
            t.get("entry_price"),
            t.get("trade_date"),
            t.get("analyst_name"),
            len(tps),
        )
        if t["expiry_date"] < today:
            logger.info(
                "Skipping expired trade from sheet (expiry %s is before today %s): %s",
                t["expiry_date"],
                today,
                t.get("ticker"),
            )
            continue
        trade_date = t.get("trade_date")
        entry_time = None
        if isinstance(trade_date, dt.date):
            # Use sheet date at midnight as entry_time so dashboard filters work by sheet date
            entry_time = dt.datetime.combine(trade_date, dt.time.min)
        trade_id = insert_trade(
            ticker=t["ticker"],
            strike_price=t["strike_price"],
            option_type=t["option_type"],
            expiry_date=t["expiry_date"],
            entry_price=t["entry_price"],
            analyst_name=t["analyst_name"],
            take_profit_targets=t.get("take_profit_targets", []),
            entry_time=entry_time,
        )
        if trade_id is not None:
            added += 1
            logger.info("Inserted trade into DB with id=%s for ticker=%s", trade_id, t.get("ticker"))
        else:
            logger.info(
                "Trade already exists in DB, not inserting duplicate for ticker=%s, strike=%s, expiry=%s, analyst=%s",
                t.get("ticker"),
                t.get("strike_price"),
                t.get("expiry_date"),
                t.get("analyst_name"),
            )
    return added


def create_app():
    """FastAPI app: dashboard, settings API, GET /trades, /analysis, /stats/{id}."""
    from fastapi import FastAPI, HTTPException

    from . import analysis, database, settings_store

    app = FastAPI(title="Version B Stop-Loss Analysis API")

    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles

    static_dir = Path(__file__).parent / "static"
    if (static_dir / "assets").exists():
        app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    def _serve_app():
        return FileResponse(static_dir / "index.html")

    @app.get("/")
    def index():
        return _serve_app()

    @app.get("/trades")
    def trades_page():
        return _serve_app()

    @app.get("/analysis")
    def analysis_page():
        return _serve_app()

    @app.get("/analytics")
    def analytics_page():
        return _serve_app()

    @app.get("/portfolio")
    def portfolio_page():
        return _serve_app()

    @app.get("/dashboard")
    def dashboard_page():
        return _serve_app()

    @app.get("/settings")
    def settings_page():
        return _serve_app()

    @app.get("/logs")
    def logs_page():
        return _serve_app()

    @app.get("/sheet-reference")
    def sheet_reference_page():
        return _serve_app()

    @app.get("/trade/{trade_id}")
    def trade_page(trade_id: str):
        return _serve_app()

    @app.get("/api/settings")
    def get_settings_api():
        """Return current effective config (store + env). API_KEY masked."""
        out = {
            "API_PROVIDER": config.API_PROVIDER,
            "API_KEY": "********" if config.API_KEY else "",
            "SPREADSHEET_ID": config.SPREADSHEET_ID,
            "GOOGLE_CREDENTIALS_PATH": config.GOOGLE_CREDENTIALS_PATH,
            "POLLING_INTERVAL": config.POLLING_INTERVAL,
            "MARKET_TIMEZONE": config.MARKET_TIMEZONE,
            "MARKET_OPEN": config.MARKET_OPEN,
            "MARKET_CLOSE": config.MARKET_CLOSE,
            "ANALYSIS_DAYS": config.ANALYSIS_DAYS,
            "MOCK_API": config.MOCK_API,
            "PAPER_TRADING": config.PAPER_TRADING,
        }
        return out

    @app.post("/api/settings")
    def save_settings_api(data: dict):
        allowed = {
            "API_PROVIDER", "API_KEY", "SPREADSHEET_ID", "GOOGLE_CREDENTIALS_PATH",
            "POLLING_INTERVAL", "MARKET_TIMEZONE", "MARKET_OPEN", "MARKET_CLOSE",
            "ANALYSIS_DAYS", "MOCK_API", "PAPER_TRADING",
        }
        s = settings_store.get_settings() or {}
        for k, v in data.items():
            if k not in allowed:
                continue
            if k == "API_KEY" and (not v or str(v).strip() in ("", "********")):
                continue  # keep existing key
            if k == "MOCK_API":
                s[k] = v in (True, "true", "1", "yes")
            elif k == "PAPER_TRADING":
                s[k] = v in (True, "true", "1", "yes")
            elif k == "POLLING_INTERVAL":
                try:
                    s[k] = int(v) if str(v).strip() else 300
                except (ValueError, TypeError):
                    s[k] = 300
            elif k == "ANALYSIS_DAYS":
                try:
                    s[k] = int(v) if str(v).strip() else 7
                except (ValueError, TypeError):
                    s[k] = 7
            else:
                s[k] = v if v is not None else ""
        settings_store.save_settings(s)
        config.reload_config()
        return {"ok": True}

    @app.post("/api/settings/credentials")
    async def upload_credentials(request: Request):
        form = await request.form()
        file = form.get("file")
        if not file or not hasattr(file, "read"):
            raise HTTPException(400, "Please upload a JSON file")
        if not (hasattr(file, "filename") and file.filename and str(file.filename).lower().endswith(".json")):
            raise HTTPException(400, "Please upload a .json file")
        content = await file.read()
        if not settings_store.save_credentials(content):
            raise HTTPException(400, "Invalid JSON or credentials format")
        return {"ok": True}

    @app.get("/api/trades")
    def list_trades():
        rows = database.get_all_trades_with_stats()
        out = []
        for t, dd, lp, ps, low in rows:
            tp_metrics = database.get_take_profit_metrics(t)
            out.append(
                {
                    "id": t.id,
                    "ticker": t.ticker,
                    "strike_price": t.strike_price,
                    "option_type": t.option_type,
                    "expiry_date": t.expiry_date.isoformat(),
                    "entry_time": t.entry_time.isoformat(),
                    "entry_price": t.entry_price,
                    "analyst_name": t.analyst_name,
                    "status": t.status,
                    "take_profit_targets": list(t.take_profit_targets),
                    "take_profit_target_price": tp_metrics["take_profit_target_price"],
                    "take_profit_hit_at": tp_metrics["take_profit_hit_at"],
                    "take_profit_hit_price": tp_metrics["take_profit_hit_price"],
                    "drawdown_before_take_profit_price": tp_metrics["drawdown_before_take_profit_price"],
                    "drawdown_before_take_profit_percent": tp_metrics["drawdown_before_take_profit_percent"],
                    # Lowest price seen after entry (client-facing live drawdown value)
                    "drawdown_price": low,
                    # Overall max drawdown since entry
                    "max_drawdown_percent": dd,
                    "current_price": lp,
                    "current_price_source": ps,
                }
            )
        return out

    @app.get("/api/analysis")
    def get_analysis():
        return analysis.run_analysis()

    @app.get("/api/stats/{trade_id}")
    def get_stats(trade_id: int):
        trade = database.get_trade_by_id(trade_id)
        if not trade:
            raise HTTPException(404, "Trade not found")
        stats = database.get_trade_stats(trade_id)
        tp_metrics = database.get_take_profit_metrics(trade)
        out = {
            "trade_id": trade_id,
            "ticker": trade.ticker,
            "entry_price": trade.entry_price,
            "take_profit_targets": list(trade.take_profit_targets),
        }
        if stats:
            out["stats"] = {
                "lowest_price": stats.lowest_price,
                "highest_price": stats.highest_price,
                "max_drawdown_percent": stats.max_drawdown_percent,
                "current_price": stats.last_price,
                "take_profit_target_price": tp_metrics["take_profit_target_price"],
                "take_profit_hit_at": tp_metrics["take_profit_hit_at"],
                "take_profit_hit_price": tp_metrics["take_profit_hit_price"],
                "drawdown_before_take_profit_price": tp_metrics["drawdown_before_take_profit_price"],
                "drawdown_before_take_profit_percent": tp_metrics["drawdown_before_take_profit_percent"],
            }
        else:
            out["stats"] = None
        return out

    @app.get("/api/logs")
    def get_logs():
        """Return recent log lines for live dashboard display."""
        return {"logs": list(LOG_BUFFER)}

    @app.get("/api/sheet-reference")
    def get_sheet_reference():
        """Return all trades from sheet with status and reason for each."""
        try:
            result = load_all_trades_from_sheet_verbose()
            return result
        except Exception as e:
            logger.exception("Sheet reference failed: %s", e)
            return {"error": str(e), "sheets": []}

    @app.post("/api/sync")
    def sync_now():
        """Re-run sheet-to-DB sync. Use when Dashboard shows 0 trades but Sheet Reference works."""
        try:
            added = sync_sheet_to_db()
            return {"ok": True, "added": added}
        except Exception as e:
            logger.exception("Sync failed: %s", e)
            return {"ok": False, "error": str(e), "added": 0}

    @app.get("/api/debug/sheet-parse")
    def debug_sheet_parse():
        """
        Diagnostic endpoint: shows raw column detection and take profit parsing
        for each worksheet tab. Visit this URL to see exactly what the parser finds.
        """
        import gspread
        from google.oauth2.service_account import Credentials
        from pathlib import Path as _Path
        from . import config as _cfg
        from .sheet_loader import (
            _get_client, _header_looks_like_trade_row, _column_index,
            _find_exit_column_index, _normalize_sheet_rows, _is_anchor_row,
            _row_cell, _extract_exit_prices_from_cell, _clean_currency,
            _parse_ticker_strike, _collect_exit_prices_multi_row, _parse_date,
        )

        if not _cfg.SPREADSHEET_ID:
            return {"error": "SPREADSHEET_ID not set"}

        try:
            client = _get_client()
            workbook = client.open_by_key(_cfg.SPREADSHEET_ID)
        except Exception as e:
            return {"error": str(e)}

        sheets_out = []
        for ws in workbook.worksheets():
            try:
                rows = ws.get_all_values()
            except Exception as e:
                sheets_out.append({"sheet": ws.title, "error": str(e)})
                continue

            if not rows:
                sheets_out.append({"sheet": ws.title, "rows": 0, "header_found": False})
                continue

            header_idx = None
            for i, row in enumerate(rows[:15]):
                if _header_looks_like_trade_row(row):
                    header_idx = i
                    break

            if header_idx is None:
                sheets_out.append({
                    "sheet": ws.title,
                    "total_rows": len(rows),
                    "header_found": False,
                    "first_3_rows": [list(r) for r in rows[:3]],
                })
                continue

            headers = rows[header_idx]
            col_date = _column_index(headers, ["date"])
            col_ticker = _column_index(headers, ["ticker", "ticker/strike", "strike"])
            col_entry = _column_index(headers, ["entry"])
            col_exit = _find_exit_column_index(headers, col_entry)

            rows_norm = _normalize_sheet_rows(rows, headers, col_date, col_ticker, col_entry, col_exit)

            trades_found = []
            i = header_idx + 1
            while i < len(rows_norm):
                row = rows_norm[i]
                if col_ticker is None or col_entry is None:
                    break
                if not _is_anchor_row(row, col_ticker, col_entry, col_date):
                    i += 1
                    continue
                entry_price = _clean_currency(_row_cell(row, col_entry))
                if entry_price is None or entry_price <= 0:
                    i += 1
                    continue
                ticker_raw = _row_cell(row, col_ticker)
                # Collect exit cell values for this trade (anchor + rows below)
                exit_cells = []
                exit_cells.append(_row_cell(rows_norm[i], col_exit))
                j = i + 1
                while j < len(rows_norm):
                    r2 = rows_norm[j]
                    if _is_anchor_row(r2, col_ticker, col_entry, col_date):
                        break
                    exit_cells.append(_row_cell(r2, col_exit))
                    j += 1
                tps = _collect_exit_prices_multi_row(
                    rows_norm, i, col_ticker, col_entry, col_exit, header_idx, col_date
                )
                trades_found.append({
                    "row": i,
                    "ticker_raw": ticker_raw,
                    "entry_price": entry_price,
                    "exit_column_index": col_exit,
                    "exit_cells_raw": exit_cells,
                    "take_profit_targets": tps,
                })
                i += 1

            sheets_out.append({
                "sheet": ws.title,
                "total_rows": len(rows),
                "header_row_index": header_idx,
                "header_row": list(headers),
                "col_date": col_date,
                "col_ticker": col_ticker,
                "col_entry": col_entry,
                "col_exit": col_exit,
                "trades_parsed": len(trades_found),
                "trades": trades_found,
            })

        return {"sheets": sheets_out}

    return app


def main() -> None:
    configure_logging()
    init_schema()

    api_serve = os.getenv("API_SERVE", "false").lower() == "true"
    has_api_key = bool(config.API_KEY) or config.MOCK_API

    def _run_uvicorn():
        import socket
        import uvicorn
        base_port = int(os.getenv("PORT", "8000"))
        for offset in range(10):
            port = base_port + offset
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("", port))
            except OSError:
                continue
            logger.info("Starting server on http://0.0.0.0:%s", port)
            app = create_app()
            uvicorn.run(app, host="0.0.0.0", port=port)
            return
        logger.error("Could not bind to port %s-%s. Stop other instances: taskkill /PID <pid> /F", base_port, base_port + 9)
        sys.exit(1)

    # Setup mode: serve dashboard only when no API key (user can configure)
    if api_serve and not has_api_key:
        logger.info("No API key. Serving dashboard only — configure at http://localhost:%s", os.getenv("PORT", "8000"))
        _run_uvicorn()
        return

    if not has_api_key:
        logger.error("API_KEY not set. Set via dashboard or .env, or use MOCK_API=true")
        sys.exit(1)

    added = sync_sheet_to_db()
    logger.info("Synced sheet -> DB: %d new trades", added)

    api = MarketDataAPI()
    scheduler = create_scheduler(api)
    scheduler.start()
    logger.info("Scheduler started (tracker every %ss, analysis every 24h)", config.POLLING_INTERVAL)

    if api_serve:
        _run_uvicorn()
    else:
        try:
            import signal
            signal.pause()
        except AttributeError:
            while True:
                __import__("time").sleep(60)
        finally:
            scheduler.shutdown(wait=False)


if __name__ == "__main__":
    main()
