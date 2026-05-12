"""Read-side analytics — feeds reports + dashboard."""
from __future__ import annotations
import pandas as pd
from sqlalchemy import text

from ..core.container import build_session_factory
from ..transformers.enrich import aging_buckets, vendor_scorecard


class AnalyticsService:
    def __init__(self) -> None:
        self.session_factory = build_session_factory()

    async def load_invoices_df(self) -> pd.DataFrame:
        async with self.session_factory() as session:
            rows = await session.execute(text("SELECT * FROM sap.invoices"))
            df = pd.DataFrame([dict(r._mapping) for r in rows])
        if not df.empty:
            df["gross_amount"] = df["gross_amount"].astype(float)
            df["amount_eur"] = df["gross_amount"]   # FX already normalized in production
        return df

    async def kpis(self) -> dict:
        df = await self.load_invoices_df()
        if df.empty:
            return {"open_invoices": 0, "overdue_invoices": 0, "total_open_eur": 0.0}
        return {
            "open_invoices":     int((df["status"] == "OPEN").sum()),
            "overdue_invoices":  int((df["status"] == "OVERDUE").sum()),
            "total_open_eur":    float(df.loc[df["status"] != "PAID", "amount_eur"].sum()),
            "vendor_count":      int(df["vendor_id"].nunique()),
        }

    async def vendor_scorecard(self) -> pd.DataFrame:
        df = await self.load_invoices_df()
        return vendor_scorecard(df)

    async def aging(self) -> pd.DataFrame:
        df = await self.load_invoices_df()
        return aging_buckets(df) if not df.empty else df
