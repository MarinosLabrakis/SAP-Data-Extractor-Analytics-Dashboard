"""Tests for transformer functions — pure, no DB required."""
from datetime import date, timedelta
from decimal import Decimal
from src.schemas.invoice import InvoiceDTO
from src.transformers.normalize import reclassify_overdue, to_eur
from src.transformers.enrich import vendor_scorecard, aging_buckets
import pandas as pd


def _inv(status="OPEN", days_offset=-10):
    return InvoiceDTO(
        invoice_id="X", vendor_id="V1", company_code="1000",
        invoice_date=date.today() - timedelta(days=30),
        posting_date=date.today() - timedelta(days=30),
        due_date=date.today() + timedelta(days=days_offset),
        currency="EUR", gross_amount=Decimal("100"), status=status,
    )


def test_reclassify_overdue_promotes_open_past_due():
    out = reclassify_overdue([_inv()])
    assert out[0].status == "OVERDUE"


def test_reclassify_keeps_paid_unchanged():
    out = reclassify_overdue([_inv(status="PAID")])
    assert out[0].status == "PAID"


def test_to_eur_handles_usd():
    assert to_eur(Decimal("100"), "USD") == Decimal("92.00")


def test_vendor_scorecard_aggregates():
    df = pd.DataFrame([
        {"invoice_id": "1", "vendor_id": "V1", "amount_eur": 100, "status": "OPEN"},
        {"invoice_id": "2", "vendor_id": "V1", "amount_eur": 200, "status": "OVERDUE"},
        {"invoice_id": "3", "vendor_id": "V2", "amount_eur": 50,  "status": "PAID"},
    ])
    out = vendor_scorecard(df)
    v1 = out[out["vendor_id"] == "V1"].iloc[0]
    assert v1["invoices"] == 2
    assert v1["total_eur"] == 300
    assert v1["overdue"] == 1
