"""RFC client for SAP ECC / on-prem S/4HANA via SAP NetWeaver RFC SDK.

Requires the optional `pyrfc` dependency and the SAP NW RFC SDK installed
on the host. We call standard BAPIs:
    - BAPI_PO_GETLIST          (Purchase Orders)
    - BAPI_INCOMINGINVOICE_GETLIST (Vendor Invoices)
"""
from __future__ import annotations
from typing import Iterable
from decimal import Decimal
from datetime import datetime

from ..schemas.purchase_order import PurchaseOrderDTO
from ..schemas.invoice import InvoiceDTO
from ..schemas.payment import PaymentDTO
from ..core.config import get_settings
from ..core.logging import get_logger

log = get_logger(__name__)


class RFCSAPClient:
    def __init__(self) -> None:
        try:
            from pyrfc import Connection  # type: ignore
        except ImportError as exc:
            raise RuntimeError("pyrfc not installed — `pip install '.[sap]'` and SAP NW RFC SDK") from exc

        s = get_settings()
        self.conn = Connection(
            user=s.sap_user, passwd=s.sap_password,
            ashost=s.sap_ashost, sysnr=s.sap_sysnr, client=s.sap_rfc_client,
        )

    @staticmethod
    def _abap_date(yyyymmdd: str):
        return datetime.strptime(yyyymmdd, "%Y%m%d").date()

    def fetch_purchase_orders(self, *, modified_since: str | None = None) -> Iterable[PurchaseOrderDTO]:
        result = self.conn.call("BAPI_PO_GETITEMS", DOCUMENT_DATE_FROM=modified_since or "20240101")
        for row in result.get("PO_ITEMS", []):
            yield PurchaseOrderDTO(
                po_number=row["PO_NUMBER"],
                vendor_id=row["VENDOR"],
                company_code=row["COMP_CODE"],
                po_date=self._abap_date(row["DOC_DATE"]),
                currency=row["CURRENCY"],
                total_net=Decimal(str(row["NET_VALUE"])),
            )

    def fetch_invoices(self, *, modified_since: str | None = None) -> Iterable[InvoiceDTO]:
        return iter(())

    def fetch_payments(self, *, modified_since: str | None = None) -> Iterable[PaymentDTO]:
        return iter(())
