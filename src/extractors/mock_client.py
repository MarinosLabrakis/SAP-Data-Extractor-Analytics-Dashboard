"""Deterministic mock SAP client — used for local dev, CI, and recruiter demos.

Generates a realistic, repeatable P2P dataset that exercises every code path:
overdue invoices, blocked POs, multi-currency vendors, and a few outliers
that the IsolationForest job will flag as anomalous.
"""
from __future__ import annotations
import random
from datetime import date, timedelta
from decimal import Decimal
from typing import Iterable

from ..schemas.purchase_order import PurchaseOrderDTO, POItemDTO
from ..schemas.invoice import InvoiceDTO
from ..schemas.payment import PaymentDTO

VENDORS = [
    ("1000001", "EUR"), ("1000002", "EUR"),
    ("1000003", "CHF"), ("1000004", "EUR"), ("1000005", "USD"),
]


class MockSAPClient:
    def __init__(self, seed: int = 42, n: int = 120) -> None:
        self.rng = random.Random(seed)
        self.n = n

    def fetch_purchase_orders(self, *, modified_since: str | None = None) -> Iterable[PurchaseOrderDTO]:
        today = date.today()
        for i in range(self.n):
            vendor, ccy = self.rng.choice(VENDORS)
            qty = self.rng.randint(1, 50)
            price = Decimal(str(round(self.rng.uniform(50, 5_000), 2)))
            po_date = today - timedelta(days=self.rng.randint(0, 120))
            yield PurchaseOrderDTO(
                po_number=f"45000{i:05d}",
                vendor_id=vendor,
                company_code="1000",
                purch_org="1000",
                po_date=po_date,
                currency=ccy,
                total_net=price * qty,
                status=self.rng.choices(["OPEN", "CLOSED", "BLOCKED"], weights=[6, 3, 1])[0],
                delivery_date=po_date + timedelta(days=self.rng.randint(7, 60)),
                items=(
                    POItemDTO(item_no=10, material=f"MAT-{self.rng.randint(1000,9999)}",
                              description="Industrial component", quantity=Decimal(qty),
                              unit="PC", net_price=price),
                ),
            )

    def fetch_invoices(self, *, modified_since: str | None = None) -> Iterable[InvoiceDTO]:
        today = date.today()
        for i in range(self.n):
            vendor, ccy = self.rng.choice(VENDORS)
            gross = Decimal(str(round(self.rng.uniform(200, 25_000), 2)))
            # Inject 3% obvious anomalies (10x normal)
            if self.rng.random() < 0.03:
                gross *= 10
            inv_date = today - timedelta(days=self.rng.randint(0, 90))
            due = inv_date + timedelta(days=self.rng.choice([30, 45, 60]))
            status = "PAID" if self.rng.random() < 0.6 else ("OVERDUE" if due < today else "OPEN")
            yield InvoiceDTO(
                invoice_id=f"51000{i:06d}",
                po_number=f"45000{self.rng.randint(0, self.n - 1):05d}",
                vendor_id=vendor,
                company_code="1000",
                invoice_date=inv_date,
                posting_date=inv_date,
                due_date=due,
                currency=ccy,
                gross_amount=gross,
                tax_amount=gross * Decimal("0.19"),
                status=status,
            )

    def fetch_payments(self, *, modified_since: str | None = None) -> Iterable[PaymentDTO]:
        return iter(())   # populated by the reconciliation job
