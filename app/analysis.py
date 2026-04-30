"""
After N days: simulate stop levels [15,20,25,30,35,40], compute hit rates, suggest best stop %.
"""
from __future__ import annotations

import logging
from typing import Optional

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
            "trades_detail": [],
            "drawdown_signed_summary": None,
        }

    stops = config.STOP_PERCENTAGES
    hit_counts = {s: 0 for s in stops}
    total = 0
    total_for_stop_sim = 0
    skipped_without_take_profit = 0
    skipped_without_take_profit_hit = 0
    excluded_lotto_outliers = 0
    trade_rows: list[dict] = []
    signed_pcts: list[float] = []
    signed_pcts_core: list[float] = []
    threshold = config.ANALYSIS_EXCLUDE_SIGNED_DRAWDOWN_BELOW
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
        min_p = tp_metrics["drawdown_before_take_profit_price"]
        signed = tp_metrics["drawdown_before_tp1_percent_signed"]
        if signed is not None:
            signed_pcts.append(float(signed))
        excluded_from_stop = (
            signed is not None and float(signed) <= threshold
        )
        if excluded_from_stop:
            excluded_lotto_outliers += 1
        else:
            total_for_stop_sim += 1
            for s in stops:
                if would_stop_have_triggered(drawdown_to_tp, s):
                    hit_counts[s] += 1
        if signed is not None and not excluded_from_stop:
            signed_pcts_core.append(float(signed))
        trade_rows.append({
            "ticker": t.ticker,
            "entry_price": round(t.entry_price, 4),
            "tp1_price": tp_target,
            "tp1_upside_percent": tp_metrics["tp1_upside_percent"],
            "min_price_before_tp1": round(min_p, 4) if min_p is not None else None,
            "drawdown_percent_signed": round(signed, 2) if signed is not None else None,
            "drawdown_percent_magnitude": round(drawdown_to_tp, 2) if drawdown_to_tp is not None else None,
            "min_before_tp1_source": tp_metrics["min_before_tp1_source"],
            "excluded_from_stop_analysis": excluded_from_stop,
        })

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
            "trades_detail": [],
            "drawdown_signed_summary": None,
        }

    stop_results = []
    denom = total_for_stop_sim
    for s in stops:
        rate = (hit_counts[s] / denom * 100) if denom else 0
        stop_results.append({"stop_percent": s, "trades_stopped_out_pct": round(rate, 1), "trades_stopped": hit_counts[s], "total_trades": denom})

    # Recommend a balanced stop: closest to a target stop-out rate (default 35%).
    # This avoids "first level under 50%" selecting 15% too aggressively.
    target_hit_rate = config.ANALYSIS_TARGET_STOP_OUT_PCT
    recommended = 30
    if denom and stop_results:
        recommended_row = min(
            stop_results,
            key=lambda r: (
                abs(r["trades_stopped_out_pct"] - target_hit_rate),
                r["stop_percent"],  # tie-break toward tighter risk
            ),
        )
        recommended = int(recommended_row["stop_percent"])

    def _percentile(vals: list[float], pct: float) -> Optional[float]:
        if not vals:
            return None
        s = sorted(vals)
        k = (len(s) - 1) * pct / 100
        lo, hi = int(k), min(int(k) + 1, len(s) - 1)
        return round(s[lo] + (s[hi] - s[lo]) * (k - lo), 2)

    # Magnitude (positive = how far below entry) — used for stop-% suggestion
    mag_pcts = [abs(v) for v in signed_pcts]
    mag_pcts_core = [abs(v) for v in signed_pcts_core]

    avg_signed = round(sum(signed_pcts) / len(signed_pcts), 2) if signed_pcts else None
    min_signed = round(min(signed_pcts), 2) if signed_pcts else None
    max_signed = round(max(signed_pcts), 2) if signed_pcts else None
    pct90_magnitude = _percentile(mag_pcts, 90)
    avg_signed_core = round(sum(signed_pcts_core) / len(signed_pcts_core), 2) if signed_pcts_core else None
    min_signed_core = round(min(signed_pcts_core), 2) if signed_pcts_core else None
    max_signed_core = round(max(signed_pcts_core), 2) if signed_pcts_core else None
    pct90_magnitude_core = _percentile(mag_pcts_core, 90)

    avg_magnitude = round(sum(mag_pcts) / len(mag_pcts), 2) if mag_pcts else None
    max_magnitude = round(max(mag_pcts), 2) if mag_pcts else None
    avg_magnitude_core = round(sum(mag_pcts_core) / len(mag_pcts_core), 2) if mag_pcts_core else None
    max_magnitude_core = round(max(mag_pcts_core), 2) if mag_pcts_core else None

    return {
        "analysis_days": config.ANALYSIS_DAYS,
        "total_trades_analyzed": total,
        "trades_with_take_profit_hits": total,
        "skipped_without_take_profit": skipped_without_take_profit,
        "skipped_without_take_profit_hit": skipped_without_take_profit_hit,
        "excluded_lotto_outliers": excluded_lotto_outliers,
        "excluded_signed_drawdown_threshold_percent": threshold,
        "total_trades_for_stop_simulation": denom,
        "stop_results": stop_results,
        "recommended_stop": recommended,
        "trades_detail": trade_rows,
        "drawdown_summary": {
            "avg_drawdown_percent": avg_magnitude_core if avg_magnitude_core is not None else avg_magnitude,
            "max_drawdown_percent": max_magnitude_core if max_magnitude_core is not None else max_magnitude,
            "percentile_90_drawdown_percent": pct90_magnitude_core if pct90_magnitude_core is not None else pct90_magnitude,
            "note": (
                "Drawdown % = how far below entry the option fell before hitting TP1. "
                "Avg/max/p90 exclude outliers (trades with signed drawdown <= threshold)."
            ),
        },
        "drawdown_signed_summary": {
            "average_percent": avg_signed,
            "min_percent": min_signed,
            "max_percent": max_signed,
            "percentile_90_magnitude": pct90_magnitude,
            "average_percent_excluding_outliers": avg_signed_core,
            "min_percent_excluding_outliers": min_signed_core,
            "max_percent_excluding_outliers": max_signed_core,
            "percentile_90_magnitude_excluding_outliers": pct90_magnitude_core,
            "avg_magnitude_excluding_outliers": avg_magnitude_core,
            "max_magnitude_excluding_outliers": max_magnitude_core,
            "note": "drawdown_percent_signed = (min_price_before_tp1 - entry) / entry * 100 (negative when underwater)",
            "outlier_note": f"Trades with signed drawdown <= {threshold}% are excluded from stop-% rates and from the excluding-outliers stats",
        },
        "recommendation_method": (
            f"closest_stop_to_target_hit_rate_{target_hit_rate:.1f}pct"
        ),
        "recommendation_target_stop_out_pct": round(target_hit_rate, 1),
        "summary": (
            f"Recommended Stop: {recommended}% (closest to target stop-out {target_hit_rate:.1f}%, "
            f"based on {denom} trade(s) after excluding signed drawdown <= {threshold}%). "
            "Uses lowest premium on the path to TP1 (manual sheet column or price logs), not current price. "
            "Stop simulation uses the positive drawdown magnitude vs your stop %."
        ),
    }
