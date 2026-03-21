"""
SQLite database: trades, price_logs, trade_stats.
"""
from __future__ import annotations

import datetime as dt
import json
import sqlite3
from pathlib import Path
from typing import List, Optional

from . import config
from .models import Trade, TradeStats
from .utils import compute_take_profit_metrics, normalize_take_profit_targets


def _trade_stats_from_row(r: sqlite3.Row) -> TradeStats:
    lp = r["last_price"] if "last_price" in r.keys() else None
    ps = r["price_source"] if "price_source" in r.keys() else None
    tp_hit: Optional[dt.datetime] = None
    if "tp_hit_at" in r.keys() and r["tp_hit_at"]:
        try:
            tp_hit = dt.datetime.fromisoformat(str(r["tp_hit_at"]))
        except (TypeError, ValueError):
            tp_hit = None
    thp = r["tp_hit_price"] if "tp_hit_price" in r.keys() else None
    lb1 = r["lowest_price_before_tp1"] if "lowest_price_before_tp1" in r.keys() else None
    lpa_raw = r["lowest_price_at"] if "lowest_price_at" in r.keys() else None
    lpa: Optional[dt.datetime] = None
    if lpa_raw:
        try:
            lpa = dt.datetime.fromisoformat(str(lpa_raw))
        except (TypeError, ValueError):
            lpa = None
    return TradeStats(
        trade_id=r["trade_id"],
        lowest_price=float(r["lowest_price"]),
        highest_price=float(r["highest_price"]),
        max_drawdown_percent=float(r["max_drawdown_percent"]),
        last_price=float(lp) if lp is not None else None,
        last_updated=dt.datetime.fromisoformat(r["last_updated"]),
        price_source=str(ps) if ps else None,
        tp_hit_at=tp_hit,
        tp_hit_price=float(thp) if thp is not None else None,
        lowest_price_before_tp1=float(lb1) if lb1 is not None else None,
        lowest_price_at=lpa,
    )

logger = __import__("logging").getLogger(__name__)


def _connect() -> sqlite3.Connection:
    Path(config.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: Optional[sqlite3.Connection] = None) -> None:
    close = conn is None
    conn = conn or _connect()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                strike_price REAL NOT NULL,
                option_type TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                entry_price REAL NOT NULL,
                take_profit_targets TEXT NOT NULL DEFAULT '[]',
                entry_time TEXT NOT NULL,
                analyst_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                tracking_start_time TEXT NOT NULL,
                UNIQUE(ticker, strike_price, option_type, expiry_date, analyst_name)
            );
            CREATE TABLE IF NOT EXISTS price_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER NOT NULL REFERENCES trades(id),
                timestamp TEXT NOT NULL,
                price REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS trade_stats (
                trade_id INTEGER PRIMARY KEY REFERENCES trades(id),
                lowest_price REAL NOT NULL,
                highest_price REAL NOT NULL,
                max_drawdown_percent REAL NOT NULL DEFAULT 0,
                last_price REAL,
                price_source TEXT,
                last_updated TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_price_logs_trade_id ON price_logs(trade_id);
            CREATE INDEX IF NOT EXISTS ix_price_logs_timestamp ON price_logs(timestamp);
        """)
        # Migration: add last_price to trade_stats if missing (existing DBs)
        try:
            conn.execute("ALTER TABLE trades ADD COLUMN take_profit_targets TEXT NOT NULL DEFAULT '[]'")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        # Migration: add last_price to trade_stats if missing (existing DBs)
        try:
            conn.execute("ALTER TABLE trade_stats ADD COLUMN last_price REAL")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # column already exists
        # Migration: add price_source ('live'|'last') if missing
        try:
            conn.execute("ALTER TABLE trade_stats ADD COLUMN price_source TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        # Backfill last_price from price_logs for rows that have drawdown but missing last_price
        try:
            conn.execute("""
                UPDATE trade_stats
                SET last_price = (
                    SELECT price FROM price_logs
                    WHERE price_logs.trade_id = trade_stats.trade_id
                    ORDER BY timestamp DESC LIMIT 1
                )
                WHERE last_price IS NULL
                AND EXISTS (
                    SELECT 1 FROM price_logs WHERE price_logs.trade_id = trade_stats.trade_id
                )
            """)
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute(
                "ALTER TABLE trades ADD COLUMN take_profit_targets_order TEXT NOT NULL DEFAULT '[]'"
            )
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute(
                "ALTER TABLE trades ADD COLUMN lowest_price_before_tp1_manual REAL"
            )
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE trade_stats ADD COLUMN tp_hit_at TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE trade_stats ADD COLUMN tp_hit_price REAL")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE trade_stats ADD COLUMN lowest_price_before_tp1 REAL")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE trade_stats ADD COLUMN lowest_price_at TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        conn.commit()
    finally:
        if close:
            conn.close()


def insert_trade(
    ticker: str,
    strike_price: float,
    option_type: str,
    expiry_date: dt.date,
    entry_price: float,
    analyst_name: str,
    take_profit_targets: Optional[list[float]] = None,
    take_profit_targets_order: Optional[list[float]] = None,
    lowest_price_before_tp1_manual: Optional[float] = None,
    entry_time: Optional[dt.datetime] = None,
) -> Optional[int]:
    """Returns trade id or None if duplicate."""
    entry_time = entry_time or dt.datetime.utcnow()
    tracking_start = dt.datetime.utcnow()
    tps = normalize_take_profit_targets(take_profit_targets or [])
    take_profit_targets_json = json.dumps(tps)
    order_raw = take_profit_targets_order if take_profit_targets_order is not None else list(tps)
    take_profit_order_json = json.dumps([round(float(x), 4) for x in order_raw])
    try:
        with _connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO trades (ticker, strike_price, option_type, expiry_date, entry_price,
                    take_profit_targets, take_profit_targets_order, lowest_price_before_tp1_manual,
                    entry_time, analyst_name, status, tracking_start_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                """,
                (
                    ticker,
                    strike_price,
                    option_type,
                    expiry_date.isoformat(),
                    entry_price,
                    take_profit_targets_json,
                    take_profit_order_json,
                    lowest_price_before_tp1_manual,
                    entry_time.isoformat(),
                    analyst_name,
                    tracking_start.isoformat(),
                ),
            )
            conn.commit()
            return cur.lastrowid
    except sqlite3.IntegrityError:
        # Caller (sync) always runs update_trade_sheet_fields so TPs refresh every sync.
        return None


def update_trade_take_profit_targets(
    ticker: str,
    strike_price: float,
    option_type: str,
    expiry_date: dt.date,
    analyst_name: str,
    take_profit_targets: list[float],
) -> None:
    update_trade_sheet_fields(
        ticker=ticker,
        strike_price=strike_price,
        option_type=option_type,
        expiry_date=expiry_date,
        analyst_name=analyst_name,
        take_profit_targets=take_profit_targets,
        take_profit_targets_order=None,
        lowest_price_before_tp1_manual=None,
        only_targets=True,
    )


def update_trade_sheet_fields(
    ticker: str,
    strike_price: float,
    option_type: str,
    expiry_date: dt.date,
    analyst_name: str,
    take_profit_targets: list[float],
    take_profit_targets_order: Optional[list[float]] = None,
    lowest_price_before_tp1_manual: Optional[float] = None,
    only_targets: bool = False,
) -> None:
    """Refresh TPs from sheet; when only_targets=True, only update take_profit_targets column."""
    tps = normalize_take_profit_targets(take_profit_targets)
    order_src: list[float]
    if take_profit_targets_order is not None:
        order_src = [round(float(x), 4) for x in take_profit_targets_order]
    else:
        order_src = list(tps)

    with _connect() as conn:
        row = conn.execute(
            """
            SELECT take_profit_targets, take_profit_targets_order FROM trades
            WHERE ticker = ? AND strike_price = ? AND option_type = ? AND expiry_date = ? AND analyst_name = ?
            """,
            (ticker, strike_price, option_type, expiry_date.isoformat(), analyst_name),
        ).fetchone()

    if row:
        try:
            existing_raw = json.loads(row["take_profit_targets"] or "[]")
        except (json.JSONDecodeError, TypeError):
            existing_raw = []
        existing_tps = normalize_take_profit_targets(existing_raw)
        if not tps and existing_tps:
            tps = existing_tps
            try:
                eo = json.loads(row["take_profit_targets_order"] or "[]")
                order_src = [round(float(x), 4) for x in eo if x is not None]
            except (json.JSONDecodeError, TypeError, ValueError):
                order_src = list(tps)
            if getattr(config, "SHEET_PARSE_DEBUG", False):
                logger.info(
                    "DB TP preserve: kept existing TPs for %s %s %s (parsed empty)",
                    ticker,
                    strike_price,
                    expiry_date.isoformat(),
                )

    targets_json = json.dumps(tps)
    if only_targets:
        with _connect() as conn:
            cur = conn.execute(
                """
                UPDATE trades
                SET take_profit_targets = ?
                WHERE ticker = ? AND strike_price = ? AND option_type = ? AND expiry_date = ? AND analyst_name = ?
                """,
                (
                    targets_json,
                    ticker,
                    strike_price,
                    option_type,
                    expiry_date.isoformat(),
                    analyst_name,
                ),
            )
            conn.commit()
            if cur.rowcount == 0:
                logger.warning(
                    "update_trade_sheet_fields (targets only): no row matched for %s %s %s %s %s",
                    ticker,
                    strike_price,
                    option_type,
                    expiry_date.isoformat(),
                    analyst_name,
                )
        return

    order_json = json.dumps(order_src)
    with _connect() as conn:
        cur = conn.execute(
            """
            UPDATE trades
            SET take_profit_targets = ?,
                take_profit_targets_order = ?,
                lowest_price_before_tp1_manual = ?
            WHERE ticker = ? AND strike_price = ? AND option_type = ? AND expiry_date = ? AND analyst_name = ?
            """,
            (
                targets_json,
                order_json,
                lowest_price_before_tp1_manual,
                ticker,
                strike_price,
                option_type,
                expiry_date.isoformat(),
                analyst_name,
            ),
        )
        conn.commit()
        if cur.rowcount == 0:
            logger.warning(
                "update_trade_sheet_fields: no row matched for %s %s %s %s %s",
                ticker,
                strike_price,
                option_type,
                expiry_date.isoformat(),
                analyst_name,
            )


def get_active_trades() -> List[Trade]:
    with _connect() as conn:
        cur = conn.execute(
            "SELECT * FROM trades WHERE status = 'ACTIVE' ORDER BY id"
        )
        return [_row_to_trade(r) for r in cur.fetchall()]


def get_all_trades() -> List[Trade]:
    with _connect() as conn:
        cur = conn.execute("SELECT * FROM trades ORDER BY id")
        return [_row_to_trade(r) for r in cur.fetchall()]


def get_all_trades_with_stats() -> List[tuple]:
    """Returns (Trade, max_drawdown_percent, last_price, price_source, lowest_price,
    tp_hit_at, tp_hit_price, lowest_price_before_tp1, lowest_price_at) for each trade."""
    with _connect() as conn:
        cur = conn.execute("""
            SELECT t.*, s.max_drawdown_percent, s.last_price, s.price_source, s.lowest_price,
                   s.tp_hit_at, s.tp_hit_price, s.lowest_price_before_tp1, s.lowest_price_at
            FROM trades t
            LEFT JOIN trade_stats s ON t.id = s.trade_id
            ORDER BY t.id
        """)
        out = []
        for r in cur.fetchall():
            trade = _row_to_trade(r)
            dd = r["max_drawdown_percent"]
            lp = r["last_price"] if "last_price" in r.keys() else None
            ps = r["price_source"] if "price_source" in r.keys() and r["price_source"] else "last"
            low = r["lowest_price"] if "lowest_price" in r.keys() else None
            tp_hit_at = r["tp_hit_at"] if "tp_hit_at" in r.keys() else None
            tp_hit_price = r["tp_hit_price"] if "tp_hit_price" in r.keys() else None
            lowest_btp = r["lowest_price_before_tp1"] if "lowest_price_before_tp1" in r.keys() else None
            lowest_price_at = r["lowest_price_at"] if "lowest_price_at" in r.keys() else None
            out.append(
                (
                    trade,
                    float(dd) if dd is not None else None,
                    float(lp) if lp is not None else None,
                    str(ps),
                    float(low) if low is not None else None,
                    str(tp_hit_at) if tp_hit_at else None,
                    float(tp_hit_price) if tp_hit_price is not None else None,
                    float(lowest_btp) if lowest_btp is not None else None,
                    str(lowest_price_at) if lowest_price_at else None,
                )
            )
        return out


def get_trade_by_id(trade_id: int) -> Optional[Trade]:
    with _connect() as conn:
        cur = conn.execute("SELECT * FROM trades WHERE id = ?", (trade_id,))
        r = cur.fetchone()
        return _row_to_trade(r) if r else None


def _row_to_trade(r: sqlite3.Row) -> Trade:
    raw_targets = r["take_profit_targets"] if "take_profit_targets" in r.keys() else "[]"
    try:
        take_profit_targets = tuple(normalize_take_profit_targets(json.loads(raw_targets or "[]")))
    except (TypeError, ValueError, json.JSONDecodeError):
        take_profit_targets = ()
    raw_order = r["take_profit_targets_order"] if "take_profit_targets_order" in r.keys() else "[]"
    try:
        loaded = json.loads(raw_order or "[]")
        take_profit_targets_order = tuple(round(float(x), 4) for x in loaded if x is not None)
    except (TypeError, ValueError, json.JSONDecodeError):
        take_profit_targets_order = ()
    manual = None
    if "lowest_price_before_tp1_manual" in r.keys() and r["lowest_price_before_tp1_manual"] is not None:
        try:
            manual = float(r["lowest_price_before_tp1_manual"])
        except (TypeError, ValueError):
            manual = None
    return Trade(
        id=r["id"],
        ticker=r["ticker"],
        strike_price=r["strike_price"],
        option_type=r["option_type"],
        expiry_date=dt.datetime.strptime(r["expiry_date"], "%Y-%m-%d").date(),
        entry_price=r["entry_price"],
        entry_time=dt.datetime.fromisoformat(r["entry_time"]),
        analyst_name=r["analyst_name"],
        status=r["status"],
        tracking_start_time=dt.datetime.fromisoformat(r["tracking_start_time"]),
        take_profit_targets=take_profit_targets,
        take_profit_targets_order=take_profit_targets_order,
        lowest_price_before_tp1_manual=manual,
    )


def insert_price_log(trade_id: int, price: float, timestamp: Optional[dt.datetime] = None) -> None:
    ts = timestamp or dt.datetime.utcnow()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO price_logs (trade_id, timestamp, price) VALUES (?, ?, ?)",
            (trade_id, ts.isoformat(), price),
        )
        conn.commit()


def get_or_create_trade_stats(trade_id: int, entry_price: float) -> TradeStats:
    with _connect() as conn:
        cur = conn.execute("SELECT * FROM trade_stats WHERE trade_id = ?", (trade_id,))
        row = cur.fetchone()
        now = dt.datetime.utcnow().isoformat()
        if row is None:
            conn.execute(
                """INSERT INTO trade_stats (trade_id, lowest_price, highest_price, max_drawdown_percent, last_price, last_updated)
                   VALUES (?, ?, ?, 0, NULL, ?)""",
                (trade_id, entry_price, entry_price, now),
            )
            conn.commit()
            return TradeStats(
                trade_id=trade_id,
                lowest_price=entry_price,
                highest_price=entry_price,
                max_drawdown_percent=0.0,
                last_price=None,
                last_updated=dt.datetime.fromisoformat(now),
            )
        return _trade_stats_from_row(row)


def update_trade_stats(
    trade_id: int,
    lowest_price: float,
    highest_price: float,
    max_drawdown_percent: float,
    last_price: Optional[float] = None,
    price_source: Optional[str] = None,
    tp_hit_at: Optional[str] = None,
    tp_hit_price: Optional[float] = None,
    lowest_price_before_tp1: Optional[float] = None,
    lowest_price_at: Optional[str] = None,
) -> None:
    """price_source: 'live' when market open, 'last' when market closed (last available price).

    tp_hit_at / tp_hit_price / lowest_price_before_tp1: pass only when recording first TP touch;
    NULLs preserve existing row values (COALESCE).

    lowest_price_at: timestamp of the cycle that produced a new running low.  The SQL CASE
    ensures it is only overwritten when excluded.lowest_price is strictly lower than the stored one.
    """
    now = dt.datetime.utcnow().isoformat()
    src = price_source or "last"
    with _connect() as conn:
        conn.execute(
            """INSERT INTO trade_stats (trade_id, lowest_price, highest_price, max_drawdown_percent, last_price, price_source, last_updated,
                   tp_hit_at, tp_hit_price, lowest_price_before_tp1, lowest_price_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(trade_id) DO UPDATE SET
                 lowest_price = excluded.lowest_price,
                 highest_price = excluded.highest_price,
                 max_drawdown_percent = excluded.max_drawdown_percent,
                 last_price = excluded.last_price,
                 price_source = excluded.price_source,
                 last_updated = excluded.last_updated,
                 tp_hit_at = COALESCE(trade_stats.tp_hit_at, excluded.tp_hit_at),
                 tp_hit_price = COALESCE(trade_stats.tp_hit_price, excluded.tp_hit_price),
                 lowest_price_before_tp1 = COALESCE(trade_stats.lowest_price_before_tp1, excluded.lowest_price_before_tp1),
                 lowest_price_at = CASE
                     WHEN trade_stats.lowest_price_at IS NULL THEN excluded.lowest_price_at
                     WHEN excluded.lowest_price < trade_stats.lowest_price THEN excluded.lowest_price_at
                     ELSE trade_stats.lowest_price_at
                 END
            """,
            (
                trade_id,
                lowest_price,
                highest_price,
                max_drawdown_percent,
                last_price,
                src,
                now,
                tp_hit_at,
                tp_hit_price,
                lowest_price_before_tp1,
                lowest_price_at,
            ),
        )
        conn.commit()


def get_trades_for_analysis(min_tracking_days: int) -> List[Trade]:
    """Trades that have been tracked for at least min_tracking_days."""
    cutoff = (dt.datetime.utcnow() - dt.timedelta(days=min_tracking_days)).isoformat()
    with _connect() as conn:
        cur = conn.execute(
            "SELECT * FROM trades WHERE tracking_start_time <= ? ORDER BY id",
            (cutoff,),
        )
        return [_row_to_trade(r) for r in cur.fetchall()]


def get_price_logs(trade_id: int) -> List[tuple]:
    """Returns list of (timestamp, price)."""
    with _connect() as conn:
        cur = conn.execute(
            "SELECT timestamp, price FROM price_logs WHERE trade_id = ? ORDER BY timestamp",
            (trade_id,),
        )
        return [(r["timestamp"], r["price"]) for r in cur.fetchall()]


def get_take_profit_metrics(trade: Trade) -> dict:
    if trade.id is None:
        return compute_take_profit_metrics(
            trade.entry_price,
            trade.take_profit_targets,
            [],
            lowest_price_before_tp1_manual=trade.lowest_price_before_tp1_manual,
            take_profit_targets_order=trade.take_profit_targets_order or (),
        )
    return compute_take_profit_metrics(
        trade.entry_price,
        trade.take_profit_targets,
        get_price_logs(trade.id),
        lowest_price_before_tp1_manual=trade.lowest_price_before_tp1_manual,
        take_profit_targets_order=trade.take_profit_targets_order or (),
    )


def get_trade_stats(trade_id: int) -> Optional[TradeStats]:
    with _connect() as conn:
        cur = conn.execute("SELECT * FROM trade_stats WHERE trade_id = ?", (trade_id,))
        r = cur.fetchone()
        if r is None:
            return None
        return _trade_stats_from_row(r)
