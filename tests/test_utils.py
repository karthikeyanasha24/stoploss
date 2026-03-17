"""
Unit tests for drawdown and (optional) market hours.
"""
import pytest

# Import from app package (run from version_b: python -m pytest tests/)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.utils import max_drawdown_percent


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
