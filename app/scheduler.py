"""
APScheduler: run tracker every POLLING_INTERVAL seconds during market hours;
run analysis once per day (trades with 7+ days data).
"""
from __future__ import annotations

import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from . import config
from .analysis import run_analysis
from .tracker import run_tracking
from .api_client import MarketDataAPI

logger = logging.getLogger(__name__)


def create_scheduler(api: MarketDataAPI) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()

    def job_tracker():
        try:
            run_tracking(api)
        except Exception as e:
            logger.exception("Tracker job failed: %s", e)

    def job_analysis():
        try:
            run_analysis()
        except Exception as e:
            logger.exception("Analysis job failed: %s", e)

    def job_sheet_sync():
        """Periodically sync new trades from Google Sheet into the DB."""
        try:
            # Lazy import to avoid circular import at module load time
            from .main import sync_sheet_to_db

            added = sync_sheet_to_db()
            logger.info("Auto sheet sync completed: %d new trades added", added)
        except Exception as e:
            logger.exception("Auto sheet sync job failed: %s", e)

    scheduler.add_job(
        job_tracker,
        IntervalTrigger(seconds=config.POLLING_INTERVAL),
        id="tracker",
        name="Track prices",
        max_instances=1,
        misfire_grace_time=None,
        coalesce=True,
    )
    scheduler.add_job(
        job_analysis,
        IntervalTrigger(hours=24),
        id="analysis",
        name="Stop % analysis",
    )
    scheduler.add_job(
        job_sheet_sync,
        IntervalTrigger(seconds=300),  # 5 minutes - auto-update latest trades from sheet
        id="sheet_sync",
        name="Sync sheet to DB",
        max_instances=1,
        coalesce=True,
    )
    return scheduler
