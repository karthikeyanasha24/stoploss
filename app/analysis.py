"""
After N days: simulate stop levels [15,20,25,30,35,40], compute hit rates, suggest best stop %.
"""
from __future__ import annotations

import datetime as dt
import logging
from typing import List

from . import config
from .database import get_trade_stats, get_trades_for_analysis

logger = logging.getLogger(__name__)


def would_stop_have_triggered(max_drawdown_percent: float, stop_percent: float) -> bool:
    """If max_drawdown >= stop%, that stop would have been hit."""
    return max_drawdown_percent >= stop_percent


def run_analysis() -> dict:
    """
    Get trades tracked >= ANALYSIS_DAYS, for each get max_drawdown_percent,
    simulate each stop %, aggregate hit rates, suggest best.
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
    for t in trades:
        stats = get_trade_stats(t.id)
        if stats is None:
            continue
        total += 1
        for s in stops:
            if would_stop_have_triggered(stats.max_drawdown_percent, s):
                hit_counts[s] += 1

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
        "stop_results": stop_results,
        "recommended_stop": recommended,
        "summary": f"Recommended Stop: {recommended}%. Balanced stop-out rate and capital preservation.",
    }
