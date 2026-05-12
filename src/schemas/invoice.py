"""DTOs for Vendor Invoice objects (RBKP/RSEG)."""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

InvoiceStatus = Literal["OPEN", "PAID", "OVERDUE", "BLOCKED"]


class InvoiceDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    invoice_id: str = Field(min_length=1, max_length=20)
    po_number: str | None = None
    vendor_id: str
    company_code: str
    invoice_date: date
    posting_date: date
    due_date: date
    currency: str
    gross_amount: Decimal
    tax_amount: Decimal = Decimal("0")
    status: InvoiceStatus = "OPEN"
    anomaly_score: float | None = None
