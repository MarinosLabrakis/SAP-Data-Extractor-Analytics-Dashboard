"""Tests for IsolationForest anomaly scoring."""
import pandas as pd
from src.ai.anomaly import score


def test_anomaly_flags_outlier():
    base = [{"amount_eur": 100 + i, "days_to_due": 30} for i in range(50)]
    base.append({"amount_eur": 100_000, "days_to_due": 30})   # extreme outlier
    df = pd.DataFrame(base)
    out = score(df, contamination=0.05)
    assert "anomaly_score" in out.columns
    # The outlier must be in the bottom-3 of anomaly_score (lower = more anomalous)
    bottom = out.nsmallest(3, "anomaly_score")
    assert (bottom["amount_eur"] == 100_000).any()
