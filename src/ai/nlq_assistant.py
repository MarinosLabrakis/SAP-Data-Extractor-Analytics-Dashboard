"""Optional natural-language Q&A over procurement data.

Translates plain-English finance questions into safe parameterised SQL via
an LLM, executes via the read-only analytics session, returns a DataFrame.

Disabled unless OPENAI_API_KEY is set. The LLM is instructed to:
  - emit ONLY a SELECT statement
  - target the `sap` schema
  - never reference auth/system tables
A regex guard rejects anything that is not a single SELECT.
"""
from __future__ import annotations
import re
import pandas as pd
from sqlalchemy import text

from ..core.config import get_settings
from ..core.container import build_session_factory


SAFE_SELECT = re.compile(r"^\s*SELECT\b[\s\S]+?;?\s*$", re.IGNORECASE)

SYSTEM_PROMPT = """You translate finance questions into PostgreSQL SELECT queries
against schema `sap` with tables: vendors, purchase_orders, po_items, invoices, payments.
Return ONLY the SQL — no prose, no markdown, single SELECT statement, no DML, no DDL."""


class NLQAssistant:
    def __init__(self) -> None:
        self.api_key = get_settings().openai_api_key
        self.session_factory = build_session_factory()

    def _llm_to_sql(self, question: str) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": question}],
            temperature=0,
        )
        sql = resp.choices[0].message.content.strip().strip("`")
        if not SAFE_SELECT.match(sql):
            raise ValueError("Refusing unsafe SQL from LLM")
        return sql

    async def ask(self, question: str) -> pd.DataFrame:
        sql = self._llm_to_sql(question)
        async with self.session_factory() as session:
            rows = await session.execute(text(sql))
            return pd.DataFrame([dict(r._mapping) for r in rows])
