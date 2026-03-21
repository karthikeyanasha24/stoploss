"""
Data models for trades, price logs, and stats.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Optional


@dataclass
class Trade:
    id: Optional[int]
    ticker: str
    strike_price: float
    option_type: str  # CALL | PUT
    expiry_date: dt.date
    entry_price: float
    entry_time: dt.datetime
    analyst_name: str
    status: str  # ACTIVE | CLOSED
    tracking_start_time: dt.datetime
    take_profit_targets: tuple[float, ...] = ()
    # Exit prices in sheet row order (chronological TP1 = first value > entry in this list).
    take_profit_targets_order: tuple[float, ...] = ()
    # Optional: manually logged lowest premium before TP1 (from sheet column).
    lowest_price_before_tp1_manual: Optional[float] = None


@dataclass
class PriceLog:
    id: Optional[int]
    trade_id: int
    timestamp: dt.datetime
    price: float


@dataclass
class TradeStats:
    trade_id: int
    lowest_price: float
    highest_price: float
    max_drawdown_percent: float
    last_updated: dt.datetime
    last_price: Optional[float] = None
    price_source: Optional[str] = None
    """First time option quote reached TP1 (chronological) — set by tracker."""
    tp_hit_at: Optional[dt.datetime] = None
    tp_hit_price: Optional[float] = None
    """Frozen min premium before first TP touch (set once when tp_hit_at is recorded)."""
    lowest_price_before_tp1: Optional[float] = None
    """Timestamp of when the running lowest_price was last updated to a new low."""
    lowest_price_at: Optional[dt.datetime] = None
