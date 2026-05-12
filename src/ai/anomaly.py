"""Invoice anomaly detection — IsolationForest over (amount_eur, days_to_due).

Returns each invoice's anomaly_score in [-1, 1] (lower = more anomalous).
The pipeline persists this back into sap.invoices.anomaly_score.
"""
from __future__ import annotations
import pandas as pd
from sklearn.ensemble import IsolationForest


FEATURES = ["amount_eur", "days_to_due"]


def score(df: pd.DataFrame, *, contamination: float = 0.05) -> pd.DataFrame:
    """Return a copy of df with an `anomaly_score` column.

    `contamination` ≈ expected anomaly rate (3-5% is typical for invoices).
    """
    if df.empty or not all(c in df.columns for c in FEATURES):
        return df.assign(anomaly_score=None)

    model = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    X = df[FEATURES].fillna(0).to_numpy()
    model.fit(X)
    out = df.copy()
    out["anomaly_score"] = model.score_samples(X)
    out["is_anomaly"]    = model.predict(X) == -1
    return out
