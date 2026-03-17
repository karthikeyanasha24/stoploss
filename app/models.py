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
