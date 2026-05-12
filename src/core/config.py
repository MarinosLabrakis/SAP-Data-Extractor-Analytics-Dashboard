"""Centralized application settings (12-factor)."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://sap:sap@localhost:5432/sap_analytics"

    sap_client: str = "mock"            # mock | odata | rfc
    sap_base_url: str = ""
    sap_user: str = ""
    sap_password: str = ""
    sap_ashost: str = ""
    sap_sysnr: str = "00"
    sap_rfc_client: str = "100"

    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_to: str = ""

    openai_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
