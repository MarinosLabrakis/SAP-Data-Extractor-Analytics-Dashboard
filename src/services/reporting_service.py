"""Reporting orchestrator — Excel + PDF + email."""
from __future__ import annotations
from pathlib import Path
from .analytics_service import AnalyticsService
from ..reports.excel_report import build_excel
from ..reports.pdf_report import build_pdf
from ..reports.emailer import send_report


class ReportingService:
    def __init__(self, out_dir: Path = Path("data/reports")) -> None:
        self.analytics = AnalyticsService()
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

    async def generate_weekly(self, *, email: bool = False) -> dict[str, Path]:
        kpis = await self.analytics.kpis()
        scorecard = await self.analytics.vendor_scorecard()
        aging = await self.analytics.aging()

        xlsx = self.out_dir / "weekly_report.xlsx"
        pdf  = self.out_dir / "weekly_report.pdf"
        build_excel(xlsx, kpis=kpis, scorecard=scorecard, aging=aging)
        build_pdf(pdf,   kpis=kpis, scorecard=scorecard)

        if email:
            send_report(subject="Weekly SAP P2P report", attachments=[xlsx, pdf])
        return {"xlsx": xlsx, "pdf": pdf}
