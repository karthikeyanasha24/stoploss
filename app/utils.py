"""
Market hours and drawdown calculation.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

import pytz

from . import config


def get_market_tz():
    return pytz.timezone(config.MARKET_TIMEZONE)


def is_market_open(now_utc: Optional[dt.datetime] = None) -> bool:
    if now_utc is None:
        now_utc = dt.datetime.utcnow().replace(tzinfo=pytz.utc)
    tz = get_market_tz()
    now_local = now_utc.astimezone(tz)
    if now_local.weekday() >= 5:  # Sat=5, Sun=6
        return False
    oh, om = map(int, config.MARKET_OPEN.split(":"))
    ch, cm = map(int, config.MARKET_CLOSE.split(":"))
    open_t = now_local.replace(hour=oh, minute=om, second=0, microsecond=0)
    close_t = now_local.replace(hour=ch, minute=cm, second=0, microsecond=0)
    return open_t <= now_local <= close_t


def max_drawdown_percent(entry_price: float, lowest_price: float) -> float:
    """
    Drawdown from entry to lowest: ((entry - lowest) / entry) * 100.
    Unit-testable.
    """
    if entry_price <= 0:
        return 0.0
    if lowest_price >= entry_price:
        return 0.0
    return ((entry_price - lowest_price) / entry_price) * 100.0
