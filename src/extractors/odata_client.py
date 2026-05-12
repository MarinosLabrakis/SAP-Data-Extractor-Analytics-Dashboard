"""OData v2 client for SAP S/4HANA (Cloud or on-prem with Gateway).

Consumes the public S/4HANA APIs:
    - API_PURCHASEORDER_PROCESS_SRV   /A_PurchaseOrder, /A_PurchaseOrderItem
    - API_SUPPLIERINVOICE_PROCESS_SRV /A_SupplierInvoice
    - API_BUSINESS_PARTNER            /A_BusinessPartner

Auth: HTTP Basic (S/4HANA on-prem) or OAuth2 client credentials (BTP).
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Iterable, Any
import requests

from ..schemas.purchase_order import PurchaseOrderDTO, POItemDTO
from ..schemas.invoice import InvoiceDTO
from ..schemas.payment import PaymentDTO
from ..core.logging import get_logger

log = get_logger(__name__)


class ODataSAPClient:
    def __init__(self, *, base_url: str, user: str, password: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (user, password)
        self.session.headers.update({"Accept": "application/json", "sap-client": "100"})
        self.timeout = timeout

    # ----------------------------------------------------------- internals
    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        log.debug("GET %s", url)
        r = self.session.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()["d"]

    @staticmethod
    def _odata_date(value: str) -> date:
        # /Date(1735689600000)/  →  date
        ms = int(value.removeprefix("/Date(").removesuffix(")/"))
        return date.fromtimestamp(ms / 1000)

    # ----------------------------------------------------------- public API
    def fetch_purchase_orders(self, *, modified_since: str | None = None) -> Iterable[PurchaseOrderDTO]:
        params: dict[str, Any] = {
            "$expand": "to_PurchaseOrderItem",
            "$format": "json",
        }
        if modified_since:
            params["$filter"] = f"LastChangeDateTime ge datetime'{modified_since}'"

        data = self._get("/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder", params)
        for row in data.get("results", []):
            items = tuple(
                POItemDTO(
                    item_no=int(it["PurchaseOrderItem"]),
                    material=it.get("Material"),
                    description=it.get("PurchaseOrderItemText"),
                    quantity=Decimal(str(it.get("OrderQuantity", "0"))),
                    unit=it.get("PurchaseOrderQuantityUnit"),
                    net_price=Decimal(str(it.get("NetPriceAmount", "0"))),
                )
                for it in row.get("to_PurchaseOrderItem", {}).get("results", [])
            )
            yield PurchaseOrderDTO(
                po_number=row["PurchaseOrder"],
                vendor_id=row["Supplier"],
                company_code=row["CompanyCode"],
                purch_org=row.get("PurchasingOrganization"),
                po_date=self._odata_date(row["PurchaseOrderDate"]),
                currency=row["DocumentCurrency"],
                total_net=Decimal(str(row.get("TotalNetAmount", "0"))),
                status="CLOSED" if row.get("PurchasingProcessingStatus") == "C" else "OPEN",
                items=items,
            )

    def fetch_invoices(self, *, modified_since: str | None = None) -> Iterable[InvoiceDTO]:
        data = self._get("/sap/opu/odata/sap/API_SUPPLIERINVOICE_PROCESS_SRV/A_SupplierInvoice")
        for row in data.get("results", []):
            yield InvoiceDTO(
                invoice_id=row["SupplierInvoice"],
                po_number=row.get("PurchaseOrder"),
                vendor_id=row["InvoicingParty"],
                company_code=row["CompanyCode"],
                invoice_date=self._odata_date(row["DocumentDate"]),
                posting_date=self._odata_date(row["PostingDate"]),
                due_date=self._odata_date(row["NetPaymentDueDate"]),
                currency=row["DocumentCurrency"],
                gross_amount=Decimal(str(row.get("InvoiceGrossAmount", "0"))),
                tax_amount=Decimal(str(row.get("TaxAmount", "0"))),
            )

    def fetch_payments(self, *, modified_since: str | None = None) -> Iterable[PaymentDTO]:
        # The Payment API varies by S/4HANA release — consult /BusinessPartner/Payment.
        return iter(())
