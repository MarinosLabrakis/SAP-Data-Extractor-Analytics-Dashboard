"""Pure-function transformers — DTOs in, DTOs out.

Kept side-effect-free so they can be unit-tested without a database.
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal
import pandas as pd

from ..schemas.invoice import InvoiceDTO


_FX = {  # static FX rates for demo; real impl would call SAP TCURR or a market API
    "EUR": Decimal("1.00"),
    "USD": Decimal("0.92"),
    "CHF": Decimal("1.05"),
}


def to_eur(amount: Decimal, currency: str) -> Decimal:
    return (amount * _FX.get(currency, Decimal("1"))).quantize(Decimal("0.01"))


def reclassify_overdue(invoices: list[InvoiceDTO], today: date | None = None) -> list[InvoiceDTO]:
    """Promote OPEN invoices past due date to OVERDUE."""
    today = today or date.today()
    out: list[InvoiceDTO] = []
    for inv in invoices:
        if inv.status == "OPEN" and inv.due_date < today:
            out.append(inv.model_copy(update={"status": "OVERDUE"}))
        else:
            out.append(inv)
    return out


def invoices_to_dataframe(invoices: list[InvoiceDTO]) -> pd.DataFrame:
    """Cleaned, normalized DataFrame for analytics + ML."""
    df = pd.DataFrame([i.model_dump() for i in invoices])
    if df.empty:
        return df
    df["gross_amount"] = df["gross_amount"].astype(float)
    df["amount_eur"] = df.apply(lambda r: float(to_eur(Decimal(str(r["gross_amount"])), r["currency"])), axis=1)
    df["days_to_due"] = (pd.to_datetime(df["due_date"]) - pd.to_datetime(df["invoice_date"])).dt.days
    return df
