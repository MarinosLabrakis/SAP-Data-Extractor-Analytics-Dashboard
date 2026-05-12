"""Repository for vendor invoices."""
from __future__ import annotations
from sqlalchemy import text
from .base import BaseRepository
from ..schemas.invoice import InvoiceDTO


class InvoiceRepository(BaseRepository):
    UPSERT = text("""
        INSERT INTO sap.invoices
              (invoice_id, po_number, vendor_id, company_code, invoice_date, posting_date,
               due_date, currency, gross_amount, tax_amount, status, anomaly_score)
        VALUES (:invoice_id, :po_number, :vendor_id, :company_code, :invoice_date, :posting_date,
                :due_date, :currency, :gross_amount, :tax_amount, :status, :anomaly_score)
        ON CONFLICT (invoice_id) DO UPDATE SET
            status        = EXCLUDED.status,
            anomaly_score = EXCLUDED.anomaly_score
    """)

    async def upsert_many(self, invoices: list[InvoiceDTO]) -> int:
        for inv in invoices:
            await self.session.execute(self.UPSERT, inv.model_dump())
        return len(invoices)

    async def fetch_all(self) -> list[dict]:
        rows = await self.session.execute(text("SELECT * FROM sap.invoices"))
        return [dict(r._mapping) for r in rows]
