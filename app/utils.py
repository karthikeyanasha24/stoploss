"""
Market hours and drawdown calculation.
"""
from __future__ import annotations

import datetime as dt
from typing import Iterable, Optional, Sequence

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


def normalize_take_profit_targets(targets: Iterable[object]) -> list[float]:
    cleaned: list[float] = []
    seen: set[float] = set()
    for target in targets:
        if target is None:
            continue
        try:
            value = float(str(target).strip().replace("$", "").replace(",", ""))
        except ValueError:
            continue
        if value <= 0:
            continue
        rounded = round(value, 4)
        if rounded in seen:
            continue
        seen.add(rounded)
        cleaned.append(rounded)
    cleaned.sort()
    return cleaned


def first_take_profit_target(entry_price: float, take_profit_targets: Sequence[float]) -> Optional[float]:
    for target in normalize_take_profit_targets(take_profit_targets):
        if target > entry_price:
            return target
    return None


def compute_take_profit_metrics(
    entry_price: float,
    take_profit_targets: Sequence[float],
    price_logs: Sequence[tuple[str, float]],
) -> dict:
    """Measure drawdown from alert until the first take-profit target is hit."""
    target_price = first_take_profit_target(entry_price, take_profit_targets)
    out = {
        "take_profit_target_price": target_price,
        "take_profit_hit_at": None,
        "take_profit_hit_price": None,
        "drawdown_before_take_profit_price": None,
        "drawdown_before_take_profit_percent": None,
    }
    if target_price is None:
        return out

    # Lowest premium strictly BEFORE first time price reaches the first TP (do not fold the hit tick into the min).
    lowest_before_target = entry_price
    for timestamp, price in price_logs:
        if price >= target_price:
            out["take_profit_hit_at"] = timestamp
            out["take_profit_hit_price"] = price
            out["drawdown_before_take_profit_price"] = lowest_before_target
            out["drawdown_before_take_profit_percent"] = max_drawdown_percent(entry_price, lowest_before_target)
            return out
        lowest_before_target = min(lowest_before_target, price)

    return out
