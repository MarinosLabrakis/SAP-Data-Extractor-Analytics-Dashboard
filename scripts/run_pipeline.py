"""CLI entrypoint — run the full pipeline once.

Usage:
    python scripts/run_pipeline.py --source mock --period 2025-Q1
"""
from __future__ import annotations
import argparse
import asyncio

from src.core.logging import configure_logging, get_logger
from src.services.extraction_service import ExtractionService
from src.services.reporting_service import ReportingService

configure_logging()
log = get_logger(__name__)


async def main(source: str, period: str, do_report: bool) -> None:
    log.info("Starting pipeline (source=%s, period=%s)", source, period)
    stats = await ExtractionService().run()
    log.info("Extraction complete: %s", stats)
    if do_report:
        out = await ReportingService().generate_weekly(email=False)
        log.info("Reports written: %s", {k: str(v) for k, v in out.items()})


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", default="mock")
    p.add_argument("--period", default="2025-Q1")
    p.add_argument("--no-report", action="store_true")
    args = p.parse_args()
    asyncio.run(main(args.source, args.period, not args.no_report))
