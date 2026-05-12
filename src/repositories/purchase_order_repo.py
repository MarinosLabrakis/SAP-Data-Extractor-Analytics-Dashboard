"""Repository for purchase_orders + po_items — owns all SQL for the aggregate."""
from __future__ import annotations
from sqlalchemy import text
from .base import BaseRepository
from ..schemas.purchase_order import PurchaseOrderDTO


class PurchaseOrderRepository(BaseRepository):
    UPSERT = text("""
        INSERT INTO sap.purchase_orders
              (po_number, vendor_id, company_code, purch_org, po_date,
               currency, total_net, status, delivery_date)
        VALUES (:po_number, :vendor_id, :company_code, :purch_org, :po_date,
                :currency, :total_net, :status, :delivery_date)
        ON CONFLICT (po_number) DO UPDATE SET
            status        = EXCLUDED.status,
            total_net     = EXCLUDED.total_net,
            delivery_date = EXCLUDED.delivery_date,
            updated_at    = now()
    """)

    UPSERT_ITEM = text("""
        INSERT INTO sap.po_items (po_number, item_no, material, description, quantity, unit, net_price)
        VALUES (:po_number, :item_no, :material, :description, :quantity, :unit, :net_price)
        ON CONFLICT (po_number, item_no) DO UPDATE SET
            quantity  = EXCLUDED.quantity,
            net_price = EXCLUDED.net_price
    """)

    async def upsert_many(self, pos: list[PurchaseOrderDTO]) -> int:
        for po in pos:
            await self.session.execute(self.UPSERT, po.model_dump(exclude={"items"}))
            for it in po.items:
                await self.session.execute(self.UPSERT_ITEM, {"po_number": po.po_number, **it.model_dump()})
        return len(pos)
