"""
After N days: simulate stop levels [15,20,25,30,35,40], compute hit rates, suggest best stop %.
"""
from __future__ import annotations

import logging

from . import config
from .database import get_take_profit_metrics, get_trades_for_analysis

logger = logging.getLogger(__name__)


def would_stop_have_triggered(max_drawdown_percent: float, stop_percent: float) -> bool:
    """If max_drawdown >= stop%, that stop would have been hit."""
    return max_drawdown_percent >= stop_percent


def run_analysis() -> dict:
    """
    Get trades tracked >= ANALYSIS_DAYS, and for trades that reached their first
    take-profit target, simulate which stop % would have been hit before that TP.
    """
    trades = get_trades_for_analysis(config.ANALYSIS_DAYS)
    if not trades:
        return {
            "message": f"No trades with at least {config.ANALYSIS_DAYS} days of tracking",
            "stop_results": [],
            "recommended_stop": None,
        }

    stops = config.STOP_PERCENTAGES
    hit_counts = {s: 0 for s in stops}
    total = 0
    skipped_without_take_profit = 0
    skipped_without_take_profit_hit = 0
    for t in trades:
        tp_metrics = get_take_profit_metrics(t)
        tp_target = tp_metrics["take_profit_target_price"]
        drawdown_to_tp = tp_metrics["drawdown_before_take_profit_percent"]
        if tp_target is None:
            skipped_without_take_profit += 1
            continue
        if drawdown_to_tp is None:
            skipped_without_take_profit_hit += 1
            continue
        total += 1
        for s in stops:
            if would_stop_have_triggered(drawdown_to_tp, s):
                hit_counts[s] += 1

    if total == 0:
        return {
            "message": "No tracked trades have reached a take-profit target yet.",
            "analysis_days": config.ANALYSIS_DAYS,
            "total_trades_analyzed": 0,
            "trades_with_take_profit_hits": 0,
            "skipped_without_take_profit": skipped_without_take_profit,
            "skipped_without_take_profit_hit": skipped_without_take_profit_hit,
            "stop_results": [],
            "recommended_stop": None,
        }

    stop_results = []
    for s in stops:
        rate = (hit_counts[s] / total * 100) if total else 0
        stop_results.append({"stop_percent": s, "trades_stopped_out_pct": round(rate, 1), "trades_stopped": hit_counts[s], "total_trades": total})

    # Recommend: e.g. 30% as balanced (middle of range); or lowest stop with < 50% hit rate
    recommended = 30
    for s in stops:
        if total and (hit_counts[s] / total) < 0.5:
            recommended = s
            break

    return {
        "analysis_days": config.ANALYSIS_DAYS,
        "total_trades_analyzed": total,
        "trades_with_take_profit_hits": total,
        "skipped_without_take_profit": skipped_without_take_profit,
        "skipped_without_take_profit_hit": skipped_without_take_profit_hit,
        "stop_results": stop_results,
        "recommended_stop": recommended,
        "summary": f"Recommended Stop: {recommended}%. Based on drawdown from alert until the first take-profit hit.",
    }
