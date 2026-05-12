"""SAP client protocol — implementations live in this package."""
from __future__ import annotations
from typing import Protocol, Iterable

from ..schemas.purchase_order import PurchaseOrderDTO
from ..schemas.invoice import InvoiceDTO
from ..schemas.payment import PaymentDTO


class SAPClient(Protocol):
    """Abstract adapter over SAP S/4HANA — OData, RFC, or mock.

    Methods return iterables of DTOs so implementations can stream large
    extracts without materializing them in memory.
    """

    def fetch_purchase_orders(self, *, modified_since: str | None = None) -> Iterable[PurchaseOrderDTO]: ...
    def fetch_invoices(self, *, modified_since: str | None = None) -> Iterable[InvoiceDTO]: ...
    def fetch_payments(self, *, modified_since: str | None = None) -> Iterable[PaymentDTO]: ...
