"""Column detection and TP extraction helpers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.sheet_loader import (  # noqa: E402
    _column_index,
    _collect_exit_prices_multi_row,
    _extract_exit_prices_from_cell,
    _find_exit_column_index,
    _merge_duplicate_trades,
    _normalize_sheet_rows,
    _trade_dicts_from_sheet_rows,
)


def test_column_index_prefers_real_entry_over_re_entry():
    headers = ["Date", "Ticker", "Re-entry", "Entry", "Exit"]
    assert _column_index(headers, ["entry"]) == 3


def test_column_index_exact_match():
    headers = ["", "Date", "Ticker / Strike", "Entry", "Exit"]
    assert _column_index(headers, ["entry"]) == 3


def test_extract_exit_prices_dollar_and_percent():
    assert _extract_exit_prices_from_cell("$2.75 (30%)") == [2.75]
    assert _extract_exit_prices_from_cell("30%") == []


def test_collect_exit_fallback_when_exit_column_empty():
    """Exit index points at empty cell but TP is one column to the right of Entry."""
    header_idx = 0
    rows = [
        ["Date", "Ticker", "Entry", "Exit", "Numbers"],
        ["1/1/26", "Bought TEST 100C Exp:12/31/26", "1.50", "", "$3.25", "50%"],
    ]
    col_date, col_ticker, col_entry, col_exit = 0, 1, 2, 3
    col_date_opt = col_date
    t_sorted, t_order = _collect_exit_prices_multi_row(
        rows,
        1,
        col_ticker,
        col_entry,
        col_exit,
        header_idx,
        col_date_opt,
        entry_price=1.5,
    )
    assert t_sorted == [3.25]
    assert t_order == [3.25]


def test_infer_exit_column_when_no_exit_header_uses_sample_rows():
    """No 'Exit' header: infer column with most premium-like values (fallback Entry+1 would be wrong)."""
    header_idx = 0
    rows = [
        ["Date", "Ticker", "Entry", "Notes", "X", "Y"],
        ["3/2/2026", "Bought TEST 100C Exp:12/31/26", "1.50", "Calls", "", ""],
        ["", "", "", "", "", "$4.20"],
        ["", "", "", "", "", "$4.70"],
    ]
    headers = rows[header_idx]
    col_entry = 2
    col_exit = _find_exit_column_index(
        headers,
        col_entry,
        sample_rows=rows,
        header_idx=header_idx,
        col_ticker=1,
        col_date=0,
    )
    assert col_exit == 5


def test_continuation_row_bare_decimal_two_cells_sparse():
    """Sparse row '4.70' | '20%' left-pads; relaxed extraction picks 4.70 without $."""
    header_idx = 0
    rows = [
        ["Date", "Ticker/Strike", "Direction", "Entry", "Exit", "Numbers"],
        ["3/2/2026", "Bought TEST 100C Exp:12/31/26", "Calls", "$1.50", "$2.50", "50%"],
        ["4.70", "20%"],
    ]
    headers = rows[header_idx]
    col_date, col_ticker, col_entry, col_exit = 0, 1, 3, 4
    norm = _normalize_sheet_rows(rows, headers, col_date, col_ticker, col_entry, col_exit, None)
    trades = _trade_dicts_from_sheet_rows(norm, header_idx, col_date, col_ticker, col_entry, col_exit)
    assert len(trades) == 1
    assert 2.5 in trades[0]["take_profit_targets"]
    assert 4.7 in trades[0]["take_profit_targets"]


def test_entry_numbers_exit_column_order_finds_exit_after_numbers():
    """Entry → Numbers → Exit: Exit must not resolve to the Numbers column."""
    headers = ["Date", "Ticker", "Direction", "Entry", "Numbers", "Exit", "P/L"]
    from app.sheet_loader import _find_exit_column_index

    assert _find_exit_column_index(headers, col_entry=3) == 5


def test_extract_exit_rejects_large_bare_integer_without_dollar():
    """Max Profit style cells like 380 should not become a fake TP."""
    assert _extract_exit_prices_from_cell("380") == []
    assert _extract_exit_prices_from_cell("380%") == []
    assert _extract_exit_prices_from_cell("$380.00") == [380.0]


def test_small_trade_channel_layout_collects_multi_row_tps():
    """Weekly log: Number column between Entry and Exit; multiple exit rows."""
    header_idx = 0
    rows = [
        ["Date", "Ticker/Strike", "Direction", "Number of Call/put", "Entry", "Exit", "Numbers"],
        ["12/1/2025", "Bought SPX 6810P", "Calls", "5", "$1.80", "$2.50", "4"],
        ["", "", "", "", "", "$2.80", "1"],
    ]
    col_date, col_ticker, col_entry, col_exit = 0, 1, 4, 5
    t_sorted, t_order = _collect_exit_prices_multi_row(
        rows,
        1,
        col_ticker,
        col_entry,
        col_exit,
        header_idx,
        col_date,
        entry_price=1.8,
    )
    assert t_sorted == [2.5, 2.8]
    assert t_order == [2.5, 2.8]


def test_split_row_ticker_then_entry_row_collects_exit_tps():
    """Matches DEC Week 1 style: Bought line, Exp line, then Date+Entry+Exit with empty Ticker cell."""
    header_idx = 0
    rows = [
        ["Date", "Ticker/Strike", "Direction", "Entry", "Exit", "Numbers"],
        ["", "Bought QQQ 630C", "", "", "", ""],
        ["", "Exp; 12/31/2025", "", "", "", ""],
        ["12/12/2025", "", "Calls ", "$4.00", "$5.50", "30%"],
    ]
    trades = _trade_dicts_from_sheet_rows(rows, header_idx, 0, 1, 3, 4)
    assert len(trades) == 1
    assert trades[0]["ticker"] == "QQQ"
    assert trades[0]["strike_price"] == 630.0
    assert trades[0]["entry_price"] == 4.0
    assert trades[0]["take_profit_targets"] == [5.5]


def test_march_log_nvda_single_row_exit_is_tp1():
    """March-style log: TP1 on same row as entry (NVDA 190C example)."""
    header_idx = 0
    rows = [
        ["Date", "Ticker/Strike", "Direction(Call/Put)", "Entry", "Exit", "Numbers", "Profit/Loss", "Max Profit (Loss)", "Remarks"],
        ["3/16/2026", "Bought NVDA 190C (Exp: 03/20/2026)", "Calls", "$1.70", "$3.50", "70%", "Profit", "160%", "Open"],
    ]
    trades = _trade_dicts_from_sheet_rows(rows, header_idx, 0, 1, 3, 4)
    assert len(trades) == 1
    assert trades[0]["entry_price"] == 1.7
    assert trades[0]["take_profit_targets"] == [3.5]
    assert trades[0]["take_profit_targets_order"] == [3.5]


def test_march_wk1_qqq_612c_multirow_exits_match_trade_log():
    """March WK 1 style: anchor + Exit-only continuation rows (user QQQ 612C example)."""
    header_idx = 0
    rows = [
        ["Date", "Ticker/Strike", "Direction(Call/Put)", "Entry", "Exit", "Numbers", "Profit/Loss", "Max Profit (Loss)", "Remarks"],
        ["3/2/2026", "Bought QQQ 612C (Exp:03/06/2026)", "Calls", "$3.50", "$4.20", "30%", "Profit", "34.00%", "Open"],
        ["", "", "", "", "$4.70", "20%", "", "", ""],
        ["", "", "", "", "$5.00", "20%", "", "", ""],
        ["", "", "", "", "$4.70", "10%", "", "", ""],
    ]
    trades = _trade_dicts_from_sheet_rows(rows, header_idx, 0, 1, 3, 4)
    assert len(trades) == 1
    assert trades[0]["entry_price"] == 3.5
    assert trades[0]["take_profit_targets"] == [4.2, 4.7, 5.0]
    assert trades[0]["take_profit_targets_order"] == [4.2, 4.7, 5.0]


def test_merge_duplicate_trades_unions_when_later_row_has_no_exits():
    """Same UNIQUE key as DB: a second sheet row must not wipe TPs from the first."""
    import datetime as dt

    d = dt.date(2026, 3, 6)
    first = {
        "ticker": "QQQ",
        "strike_price": 612.0,
        "option_type": "CALL",
        "expiry_date": d,
        "analyst_name": "March WK 1",
        "entry_price": 3.5,
        "take_profit_targets": [4.2, 4.7, 5.0],
        "take_profit_targets_order": [4.2, 4.7, 5.0],
        "trade_date": dt.date(2026, 3, 2),
        "lowest_price_before_tp1_manual": None,
    }
    second = {**first, "take_profit_targets": [], "take_profit_targets_order": []}
    merged = _merge_duplicate_trades([first, second])
    assert len(merged) == 1
    assert merged[0]["take_profit_targets"] == [4.2, 4.7, 5.0]


def test_march_log_nvda_exit_on_continuation_row():
    """Exit stacked below anchor row still maps to same trade (fixes 'No TPs' when parser skipped continuation)."""
    header_idx = 0
    rows = [
        ["Date", "Ticker/Strike", "Direction(Call/Put)", "Entry", "Exit", "Numbers"],
        ["3/16/2026", "Bought NVDA 190C (Exp: 03/20/2026)", "Calls", "$1.70", "", ""],
        ["", "", "", "", "$3.50", "70%"],
    ]
    trades = _trade_dicts_from_sheet_rows(rows, header_idx, 0, 1, 3, 4)
    assert len(trades) == 1
    assert trades[0]["take_profit_targets"] == [3.5]
    assert trades[0]["take_profit_targets_order"] == [3.5]


def test_block_pattern_skips_tp_when_profit_loss_column_is_loss():
    """Per spec: do not attach TPs when the row is explicitly marked Loss in Profit/Loss."""
    header_idx = 0
    rows = [
        ["Date", "Ticker/Strike", "Direction", "Entry", "Exit", "Profit/Loss"],
        ["3/2/2026", "Bought TEST 100C Exp:12/31/2026", "Calls", "$1.50", "$3.00", "Loss"],
    ]
    trades = _trade_dicts_from_sheet_rows(rows, header_idx, 0, 1, 3, 4)
    assert len(trades) == 1
    assert trades[0]["take_profit_targets"] == []


def test_block_pattern_finds_tps_when_exit_col_index_wrong():
    """Mis-labeled Exit column: premiums still found by scanning the row (pattern-based)."""
    header_idx = 0
    rows = [
        ["Date", "Ticker", "Entry", "Notes", "X"],
        ["3/2/2026", "Bought TEST 100C Exp:12/31/2026", "$1.50", "Calls", "$4.20"],
    ]
    # col_exit=3 points at Notes/Calls — real TP is in col 4; block scan still finds $4.20.
    trades = _trade_dicts_from_sheet_rows(rows, header_idx, 0, 1, 2, 3)
    assert len(trades) == 1
    assert trades[0]["take_profit_targets"] == [4.2]
