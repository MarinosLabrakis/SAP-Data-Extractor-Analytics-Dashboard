"""Analytical enrichment: vendor scorecards, aging buckets, KPI rollups."""
from __future__ import annotations
import pandas as pd


def aging_buckets(df: pd.DataFrame, today: pd.Timestamp | None = None) -> pd.DataFrame:
    today = today or pd.Timestamp.today().normalize()
    df = df.copy()
    df["days_overdue"] = (today - pd.to_datetime(df["due_date"])).dt.days.clip(lower=0)
    df["bucket"] = pd.cut(
        df["days_overdue"],
        bins=[-1, 0, 30, 60, 90, 10_000],
        labels=["Current", "1-30", "31-60", "61-90", "90+"],
    )
    return df


def vendor_scorecard(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate KPIs per vendor — used in dashboard + executive PDF."""
    if df.empty:
        return df
    return (df.groupby("vendor_id")
              .agg(invoices=("invoice_id", "count"),
                   total_eur=("amount_eur", "sum"),
                   avg_eur=("amount_eur", "mean"),
                   overdue=("status", lambda s: (s == "OVERDUE").sum()))
              .round(2)
              .reset_index()
              .sort_values("total_eur", ascending=False))
