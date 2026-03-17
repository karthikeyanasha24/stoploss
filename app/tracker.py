"""
Tracking logic: every cycle fetch live price, insert price_logs, update trade_stats.
"""
from __future__ import annotations

import datetime as dt
import logging

from . import config
from .api_client import MarketDataAPI
from .database import (
    get_active_trades,
    get_or_create_trade_stats,
    insert_price_log,
    update_trade_stats,
)
from .models import Trade
from .utils import is_market_open, max_drawdown_percent

logger = logging.getLogger(__name__)


def run_tracking(api: MarketDataAPI) -> None:
    """For each ACTIVE trade: fetch price (last available, even when market closed), log it, update lowest/highest/drawdown."""
    market_open = is_market_open()
    if not market_open:
        logger.info("Market closed — fetching last available prices (previous close)")

    today = dt.date.today()
    trades = get_active_trades()
    for t in trades:
        if t.expiry_date < today:
            logger.info("Trade %s expired; skipping", t.id)
            continue
        try:
            contract = api.find_contract(
                ticker=t.ticker,
                strike=t.strike_price,
                expiry=t.expiry_date.isoformat(),
                option_type=t.option_type,
            )
            if not contract:
                logger.debug("Trade %s %s: no contract found", t.id, t.ticker)
                continue
            price = api.get_option_quote(contract.symbol)
            if price is None:
                logger.warning("Trade %s %s %s: no price returned", t.id, t.ticker, contract.symbol)
                continue
            insert_price_log(t.id, price)
            stats = get_or_create_trade_stats(t.id, t.entry_price)
            low = min(stats.lowest_price, price)
            high = max(stats.highest_price, price)
            dd = max_drawdown_percent(t.entry_price, low)
            price_source = "live" if market_open else "last"
            update_trade_stats(t.id, low, high, dd, last_price=price, price_source=price_source)
            logger.info(
                "Trade %s [%s %s %s exp=%s] | contract=%s | "
                "PARAMS: entry_price=%.2f fetched_price=%.2f prev_lowest=%.2f prev_highest=%.2f | "
                "CALC: new_lowest=min(%.2f,%.2f)=%.2f new_highest=max(%.2f,%.2f)=%.2f | "
                "DRAWDOWN: (entry-lowest)/entry*100 = (%.2f-%.2f)/%.2f*100 = %.1f%%",
                t.id, t.ticker, t.strike_price, t.option_type, t.expiry_date.isoformat(),
                contract.symbol,
                t.entry_price, price, stats.lowest_price, stats.highest_price,
                stats.lowest_price, price, low, stats.highest_price, price, high,
                t.entry_price, low, t.entry_price, dd,
            )
        except Exception as e:
            logger.warning("Error tracking trade %s: %s", t.id, e)
