"""
Market hours and drawdown calculation.
"""
from __future__ import annotations

import datetime as dt
from typing import Iterable, List, Optional, Sequence, TypedDict

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
    Positive magnitude of adverse move: ((entry - lowest) / entry) * 100 when lowest < entry.
    Unit-testable.
    """
    if entry_price <= 0:
        return 0.0
    if lowest_price >= entry_price:
        return 0.0
    return ((entry_price - lowest_price) / entry_price) * 100.0


def signed_return_from_entry(entry_price: float, price: float) -> float:
    """(price - entry) / entry * 100 — negative when price is below entry (underwater)."""
    if entry_price <= 0:
        return 0.0
    return ((price - entry_price) / entry_price) * 100.0


def tp1_upside_percent(entry_price: float, tp1_price: float) -> float:
    """(TP1 - entry) / entry * 100 — distance to first take-profit target."""
    return signed_return_from_entry(entry_price, tp1_price)


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


def first_tp1_chronological(
    entry_price: float,
    take_profit_targets_sorted: Sequence[float],
    take_profit_targets_order: Sequence[float],
) -> Optional[float]:
    """
    TP1 = first exit price **in sheet/time order** that is above entry.
    If order is empty, fall back to smallest TP above entry (sorted list).
    """
    if take_profit_targets_order:
        for p in take_profit_targets_order:
            try:
                v = float(p)
            except (TypeError, ValueError):
                continue
            if v > entry_price:
                return round(v, 4)
    return first_take_profit_target(entry_price, take_profit_targets_sorted)


def compute_take_profit_metrics(
    entry_price: float,
    take_profit_targets: Sequence[float],
    price_logs: Sequence[tuple[str, float]],
    lowest_price_before_tp1_manual: Optional[float] = None,
    take_profit_targets_order: Optional[Sequence[float]] = None,
) -> dict:
    """
    Path to TP1 (not current price):
    - Min before TP1: lowest premium after entry until TP1 is first touched (from price_logs),
      or optional manual value from the sheet column "Lowest Price Before TP1".
    - drawdown_before_tp1_percent_signed = (min - entry) / entry * 100 (negative when underwater).
    - drawdown_before_take_profit_percent = positive MAE magnitude (for stop-% comparisons).
    - tp1_upside_percent = (TP1 - entry) / entry * 100.
    """
    order = take_profit_targets_order if take_profit_targets_order is not None else ()
    target_price = first_tp1_chronological(entry_price, take_profit_targets, order)
    out: dict = {
        "take_profit_target_price": target_price,
        "tp1_upside_percent": None,
        "take_profit_hit_at": None,
        "take_profit_hit_price": None,
        "drawdown_before_take_profit_price": None,
        "drawdown_before_take_profit_percent": None,
        "drawdown_before_tp1_percent_signed": None,
        "min_before_tp1_source": None,
    }
    if target_price is None:
        return out

    out["tp1_upside_percent"] = round(tp1_upside_percent(entry_price, target_price), 4)

    # Manual journal: true min before TP1 without intraday logs
    if lowest_price_before_tp1_manual is not None and lowest_price_before_tp1_manual > 0:
        min_p = lowest_price_before_tp1_manual
        out["drawdown_before_take_profit_price"] = min_p
        out["drawdown_before_take_profit_percent"] = max_drawdown_percent(entry_price, min_p)
        out["drawdown_before_tp1_percent_signed"] = round(signed_return_from_entry(entry_price, min_p), 4)
        out["min_before_tp1_source"] = "manual_sheet"
        return out

    # Price path from logs until first time quote reaches TP1
    lowest_before_target = entry_price
    for timestamp, price in price_logs:
        if price >= target_price:
            out["take_profit_hit_at"] = timestamp
            out["take_profit_hit_price"] = price
            out["drawdown_before_take_profit_price"] = lowest_before_target
            out["drawdown_before_take_profit_percent"] = max_drawdown_percent(entry_price, lowest_before_target)
            out["drawdown_before_tp1_percent_signed"] = round(
                signed_return_from_entry(entry_price, lowest_before_target), 4
            )
            out["min_before_tp1_source"] = "price_logs"
            return out
        lowest_before_target = min(lowest_before_target, price)

    return out


class PerTpBabjiRow(TypedDict, total=False):
    """Per take-profit level: worst premium from entry until first touch of that TP (from logs)."""

    tp_index: int
    tp_price: float
    """ISO timestamp of first quote ≥ this TP, or missing if never."""
    hit_at: Optional[str]
    babji_low: Optional[float]
    babji_dd_percent: Optional[float]
    """ISO timestamp of the log row that achieved babji_low in the window (before first hit)."""
    low_at: Optional[str]


def ordered_tp_levels_chronological(
    entry_price: float,
    take_profit_targets: Sequence[float],
    take_profit_targets_order: Sequence[float],
) -> List[float]:
    """
    All TP prices above entry in sheet order (TP1, TP2, …). Same ordering rule as first TP1.
    """
    order = take_profit_targets_order if take_profit_targets_order else ()
    levels: List[float] = []
    seen: set[float] = set()
    if order:
        for p in order:
            try:
                v = round(float(p), 4)
            except (TypeError, ValueError):
                continue
            if v <= entry_price or v in seen:
                continue
            seen.add(v)
            levels.append(v)
        if levels:
            return levels
    return [x for x in normalize_take_profit_targets(take_profit_targets) if x > entry_price]


def per_tp_babji_metrics(
    entry_price: float,
    ordered_tps: Sequence[float],
    price_logs: Sequence[tuple[str, float]],
    *,
    lowest_price_fallback: Optional[float] = None,
    lowest_price_at_fallback: Optional[str] = None,
) -> List[PerTpBabjiRow]:
    """
    For each TP level (in order): window = entry → first time price ≥ that TP.
    Babji low = minimum premium in that window (strictly before first hit quote).
    If that TP is never touched, window = all logs (same idea as live running window to “now”).
    When there are no logs but `lowest_price_fallback` is set (e.g. trade_stats), use it for DD/low.
    """
    if not ordered_tps:
        return []
    logs = sorted(price_logs, key=lambda x: x[0])
    rows: List[PerTpBabjiRow] = []
    for i, tp_price in enumerate(ordered_tps):
        hit_idx: Optional[int] = None
        for j, (_ts, price) in enumerate(logs):
            if price >= tp_price:
                hit_idx = j
                break
        if hit_idx is None:
            window = list(logs)
            hit_at: Optional[str] = None
        else:
            window = logs[:hit_idx]
            hit_at = logs[hit_idx][0]
        if not window:
            if not logs and lowest_price_fallback is not None and entry_price > 0:
                min_p = lowest_price_fallback
                low_at = lowest_price_at_fallback
            elif logs:
                # First stored quote already at/above this TP — no earlier quotes in window
                min_p = entry_price
                low_at = None
            else:
                rows.append(
                    {
                        "tp_index": i + 1,
                        "tp_price": tp_price,
                        "hit_at": hit_at,
                        "babji_low": None,
                        "babji_dd_percent": None,
                        "low_at": None,
                    }
                )
                continue
            dd = max_drawdown_percent(entry_price, min_p)
            rows.append(
                {
                    "tp_index": i + 1,
                    "tp_price": tp_price,
                    "hit_at": hit_at,
                    "babji_low": round(min_p, 4),
                    "babji_dd_percent": round(dd, 2),
                    "low_at": low_at,
                }
            )
            continue
        min_ts, min_price = min(window, key=lambda x: x[1])
        dd = max_drawdown_percent(entry_price, min_price)
        rows.append(
            {
                "tp_index": i + 1,
                "tp_price": tp_price,
                "hit_at": hit_at,
                "babji_low": round(min_price, 4),
                "babji_dd_percent": round(dd, 2),
                "low_at": min_ts,
            }
        )
    return rows
