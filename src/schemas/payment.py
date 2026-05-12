"""DTOs for Vendor Payment objects (BSAK/BSIK)."""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class PaymentDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    payment_id: str
    invoice_id: str
    paid_at: date
    amount: Decimal
    currency: str
    method: str = "BANK"
