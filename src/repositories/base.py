"""Generic async repository base — Unit-of-Work style."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
