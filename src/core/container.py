"""Lightweight DI container — wires extractors, repositories, services."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import get_settings
from ..extractors.base import SAPClient
from ..extractors.mock_client import MockSAPClient
from ..extractors.odata_client import ODataSAPClient


def build_sap_client() -> SAPClient:
    s = get_settings()
    if s.sap_client == "odata":
        return ODataSAPClient(base_url=s.sap_base_url, user=s.sap_user, password=s.sap_password)
    if s.sap_client == "rfc":
        from ..extractors.rfc_client import RFCSAPClient   # imported lazily — pyrfc optional
        return RFCSAPClient()
    return MockSAPClient()


def build_session_factory() -> async_sessionmaker:
    engine = create_async_engine(get_settings().database_url, pool_pre_ping=True, future=True)
    return async_sessionmaker(engine, expire_on_commit=False)
