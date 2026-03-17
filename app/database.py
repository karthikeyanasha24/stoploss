"""
SQLite database: trades, price_logs, trade_stats.
"""
from __future__ import annotations

import datetime as dt
import sqlite3
from pathlib import Path
from typing import List, Optional

from . import config
from .models import Trade, TradeStats

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
    entry_time: Optional[dt.datetime] = None,
) -> Optional[int]:
    """Returns trade id or None if duplicate."""
    entry_time = entry_time or dt.datetime.utcnow()
    tracking_start = dt.datetime.utcnow()
    try:
        with _connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO trades (ticker, strike_price, option_type, expiry_date, entry_price,
                    entry_time, analyst_name, status, tracking_start_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                """,
                (
                    ticker,
                    strike_price,
                    option_type,
                    expiry_date.isoformat(),
                    entry_price,
                    entry_time.isoformat(),
                    analyst_name,
                    tracking_start.isoformat(),
                ),
            )
            conn.commit()
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


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
    """Returns (Trade, max_drawdown_percent, last_price, price_source, lowest_price) for each trade."""
    with _connect() as conn:
        cur = conn.execute("""
            SELECT t.*, s.max_drawdown_percent, s.last_price, s.price_source, s.lowest_price
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
            out.append(
                (
                    trade,
                    float(dd) if dd is not None else None,
                    float(lp) if lp is not None else None,
                    str(ps),
                    float(low) if low is not None else None,
                )
            )
        return out


def get_trade_by_id(trade_id: int) -> Optional[Trade]:
    with _connect() as conn:
        cur = conn.execute("SELECT * FROM trades WHERE id = ?", (trade_id,))
        r = cur.fetchone()
        return _row_to_trade(r) if r else None


def _row_to_trade(r: sqlite3.Row) -> Trade:
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
            return TradeStats(trade_id=trade_id, lowest_price=entry_price, highest_price=entry_price, max_drawdown_percent=0.0, last_price=None, last_updated=dt.datetime.fromisoformat(now))
        last_price = row["last_price"] if "last_price" in row.keys() else None
        return TradeStats(
            trade_id=row["trade_id"],
            lowest_price=row["lowest_price"],
            highest_price=row["highest_price"],
            max_drawdown_percent=row["max_drawdown_percent"],
            last_price=float(last_price) if last_price is not None else None,
            last_updated=dt.datetime.fromisoformat(row["last_updated"]),
        )


def update_trade_stats(
    trade_id: int,
    lowest_price: float,
    highest_price: float,
    max_drawdown_percent: float,
    last_price: Optional[float] = None,
    price_source: Optional[str] = None,
) -> None:
    """price_source: 'live' when market open, 'last' when market closed (last available price)."""
    now = dt.datetime.utcnow().isoformat()
    src = price_source or "last"
    with _connect() as conn:
        conn.execute(
            """INSERT INTO trade_stats (trade_id, lowest_price, highest_price, max_drawdown_percent, last_price, price_source, last_updated)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(trade_id) DO UPDATE SET
                 lowest_price = excluded.lowest_price,
                 highest_price = excluded.highest_price,
                 max_drawdown_percent = excluded.max_drawdown_percent,
                 last_price = excluded.last_price,
                 price_source = excluded.price_source,
                 last_updated = excluded.last_updated
            """,
            (trade_id, lowest_price, highest_price, max_drawdown_percent, last_price, src, now),
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


def get_trade_stats(trade_id: int) -> Optional[TradeStats]:
    with _connect() as conn:
        cur = conn.execute("SELECT * FROM trade_stats WHERE trade_id = ?", (trade_id,))
        r = cur.fetchone()
        if r is None:
            return None
        lp = r["last_price"] if "last_price" in r.keys() else None
        return TradeStats(
            trade_id=r["trade_id"],
            lowest_price=r["lowest_price"],
            highest_price=r["highest_price"],
            max_drawdown_percent=r["max_drawdown_percent"],
            last_price=float(lp) if lp is not None else None,
            last_updated=dt.datetime.fromisoformat(r["last_updated"]),
        )
