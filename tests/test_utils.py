"""
Unit tests for drawdown and (optional) market hours.
"""
import pytest

# Import from app package (run from version_b: python -m pytest tests/)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.utils import (
    compute_take_profit_metrics,
    max_drawdown_percent,
    ordered_tp_levels_chronological,
    per_tp_babji_metrics,
)


def test_max_drawdown_percent_basic():
    assert max_drawdown_percent(100.0, 70.0) == 30.0
    assert max_drawdown_percent(10.0, 7.0) == 30.0


def test_max_drawdown_percent_no_drawdown():
    assert max_drawdown_percent(100.0, 100.0) == 0.0
    assert max_drawdown_percent(100.0, 110.0) == 0.0


def test_max_drawdown_percent_zero_entry():
    assert max_drawdown_percent(0.0, 0.0) == 0.0


def test_max_drawdown_percent_simulated_stop():
    # Entry 2.50, lowest 1.75 -> 30% drawdown (stop would have hit at 30%)
    assert max_drawdown_percent(2.50, 1.75) == 30.0


def test_compute_take_profit_drawdown_uses_lowest_before_first_tp_not_current():
    """
    Drawdown for stop analysis: adverse excursion from entry (lowest price) until first TP is
    touched, not (entry - current) / entry.
    """
    entry = 500.0
    # TPs at 600, 800 — first target is 600
    logs = [
        ("t1", 400.0),  # dip to 400 -> 20% DD from entry
        ("t2", 550.0),
        ("t3", 600.0),  # first hit at TP1
    ]
    m = compute_take_profit_metrics(entry, [600.0, 800.0], logs)
    assert m["take_profit_target_price"] == 600.0
    assert m["drawdown_before_take_profit_percent"] == 20.0
    assert m["drawdown_before_take_profit_price"] == 400.0
    assert m["drawdown_before_tp1_percent_signed"] == -20.0
    assert m["tp1_upside_percent"] == 20.0
    assert m["min_before_tp1_source"] == "price_logs"


def test_manual_min_before_tp1_skips_logs():
    entry = 2.6
    m = compute_take_profit_metrics(
        entry,
        [3.2],
        [],
        lowest_price_before_tp1_manual=2.0,
        take_profit_targets_order=(3.2,),
    )
    assert m["take_profit_target_price"] == 3.2
    assert m["drawdown_before_take_profit_price"] == 2.0
    assert round(m["drawdown_before_tp1_percent_signed"] or 0, 2) == -23.08  # (2-2.6)/2.6*100
    assert m["min_before_tp1_source"] == "manual_sheet"


def test_per_tp_babji_never_hit_same_running_low():
    entry = 3.5
    tps = [4.2, 4.7, 5.0]
    logs = [("t1", 0.09), ("t2", 0.14)]
    rows = per_tp_babji_metrics(entry, tps, logs)
    assert len(rows) == 3
    for r in rows:
        assert r["babji_low"] == 0.09
        assert r["hit_at"] is None
        assert r["babji_dd_percent"] == pytest.approx(97.43, rel=1e-2)


def test_per_tp_babji_tp1_hit_then_tp2_live():
    entry = 3.5
    tps = [4.2, 4.7]
    logs = [("t1", 0.09), ("t2", 4.2)]
    rows = per_tp_babji_metrics(entry, tps, logs)
    assert rows[0]["hit_at"] == "t2"
    assert rows[0]["babji_low"] == 0.09
    assert rows[1]["hit_at"] is None
    assert rows[1]["babji_low"] == 0.09


def test_ordered_tp_levels_respects_sheet_order():
    entry = 3.5
    order = (5.0, 4.2, 4.7)
    levels = ordered_tp_levels_chronological(entry, [4.2, 4.7, 5.0], order)
    assert levels == [5.0, 4.2, 4.7]
