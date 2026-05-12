"""APScheduler entrypoint — nightly extract, weekly report, daily alerts."""
from __future__ import annotations
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..core.logging import configure_logging, get_logger
from ..services.extraction_service import ExtractionService
from ..services.reporting_service import ReportingService

configure_logging()
log = get_logger(__name__)


async def nightly_extract() -> None:
    log.info("→ nightly_extract")
    await ExtractionService().run()


async def weekly_report() -> None:
    log.info("→ weekly_report")
    await ReportingService().generate_weekly(email=True)


def main() -> None:
    sched = AsyncIOScheduler(timezone="UTC")
    sched.add_job(nightly_extract, CronTrigger(hour=2, minute=0),  id="nightly_extract")
    sched.add_job(weekly_report,   CronTrigger(day_of_week="mon", hour=6), id="weekly_report")
    sched.start()
    log.info("Scheduler running. Ctrl-C to stop.")
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()


if __name__ == "__main__":
    main()
