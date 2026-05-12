"""Orchestrates: extract → transform → load → audit."""
from __future__ import annotations
from ..core.container import build_sap_client, build_session_factory
from ..core.logging import get_logger
from ..repositories.purchase_order_repo import PurchaseOrderRepository
from ..repositories.invoice_repo import InvoiceRepository
from ..repositories.audit_repo import AuditRepository
from ..transformers.normalize import reclassify_overdue

log = get_logger(__name__)


class ExtractionService:
    def __init__(self) -> None:
        self.sap = build_sap_client()
        self.session_factory = build_session_factory()

    async def run(self) -> dict[str, int]:
        pos = list(self.sap.fetch_purchase_orders())
        invoices = reclassify_overdue(list(self.sap.fetch_invoices()))

        async with self.session_factory() as session:
            async with session.begin():
                po_repo    = PurchaseOrderRepository(session)
                inv_repo   = InvoiceRepository(session)
                audit_repo = AuditRepository(session)

                n_po  = await po_repo.upsert_many(pos)
                n_inv = await inv_repo.upsert_many(invoices)

                await audit_repo.log(entity="pipeline", entity_id="extract",
                                     action="RUN", payload={"po": n_po, "invoices": n_inv})

        log.info("Extracted %s POs and %s invoices", n_po, n_inv)
        return {"purchase_orders": n_po, "invoices": n_inv}
