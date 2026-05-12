"""Append-only audit log — mirrors SAP CDHDR/CDPOS pattern."""
from __future__ import annotations
import json
from sqlalchemy import text
from .base import BaseRepository


class AuditRepository(BaseRepository):
    INSERT = text("""
        INSERT INTO sap.audit_log (entity, entity_id, action, changed_by, payload)
        VALUES (:entity, :entity_id, :action, :changed_by, CAST(:payload AS JSONB))
    """)

    async def log(self, *, entity: str, entity_id: str, action: str,
                  changed_by: str = "pipeline", payload: dict | None = None) -> None:
        await self.session.execute(self.INSERT, {
            "entity": entity, "entity_id": entity_id, "action": action,
            "changed_by": changed_by, "payload": json.dumps(payload or {}, default=str),
        })
