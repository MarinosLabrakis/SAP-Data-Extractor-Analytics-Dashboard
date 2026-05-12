"""DTOs for SAP Purchase Order objects (EKKO/EKPO).

Pydantic v2 models — used at every layer boundary so we never pass raw dicts.
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

POStatus = Literal["OPEN", "CLOSED", "BLOCKED"]


class POItemDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    item_no: int = Field(ge=1)
    material: str | None = None
    description: str | None = None
    quantity: Decimal
    unit: str | None = None
    net_price: Decimal


class PurchaseOrderDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    po_number: str = Field(min_length=1, max_length=10)     # EBELN
    vendor_id: str                                          # LIFNR
    company_code: str                                       # BUKRS
    purch_org: str | None = None                            # EKORG
    po_date: date                                           # BEDAT
    currency: str
    total_net: Decimal
    status: POStatus = "OPEN"
    delivery_date: date | None = None
    items: tuple[POItemDTO, ...] = ()
