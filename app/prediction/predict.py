"""Prediction and anomaly detection helpers."""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from app.prediction.model_loader import get_anomaly_model, get_prediction_model


def predict_next_month_expense(dataframe: pd.DataFrame) -> Dict[str, float]:
    """Forecast next month's expense from historical monthly spend."""
    if dataframe.empty:
        return {"next_month_expense": 0.0, "average_monthly_expense": 0.0}

    monthly = dataframe.copy()
    monthly["MonthPeriod"] = monthly["Date"].dt.to_period("M")
    grouped = monthly.groupby("MonthPeriod")["Amount"].sum().reset_index()
    grouped["month_index"] = np.arange(len(grouped))
    grouped["lag_1"] = grouped["Amount"].shift(1).fillna(grouped["Amount"].mean())
    grouped["lag_2"] = grouped["Amount"].shift(2).fillna(grouped["Amount"].mean())

    if len(grouped) < 2:
        baseline = float(grouped["Amount"].iloc[-1])
        return {"next_month_expense": round(baseline, 2), "average_monthly_expense": round(baseline, 2)}

    model = get_prediction_model()
    next_features = pd.DataFrame(
        [
            {
                "month_index": int(grouped["month_index"].iloc[-1] + 1),
                "lag_1": float(grouped["Amount"].iloc[-1]),
                "lag_2": float(grouped["Amount"].iloc[-2]),
            }
        ]
    )
    prediction = float(model.predict(next_features)[0])
    average = float(grouped["Amount"].mean())
    return {
        "next_month_expense": round(max(prediction, 0.0), 2),
        "average_monthly_expense": round(average, 2),
    }


def detect_anomalies(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return unusual transactions using an Isolation Forest model."""
    if dataframe.empty:
        return dataframe.assign(anomaly_score=[], is_anomaly=[])

    prepared = dataframe.copy()
    prepared["category_code"] = prepared["Category"].astype("category").cat.codes
    features = np.column_stack(
        [
            prepared["Amount"].astype(float),
            prepared["Date"].dt.day.astype(int),
            prepared["Date"].dt.weekday.astype(int),
            prepared["category_code"].astype(int),
        ]
    )

    model = get_anomaly_model()
    prepared["anomaly_score"] = model.decision_function(features)
    prepared["is_anomaly"] = model.predict(features) == -1

    amount_threshold = prepared["Amount"].quantile(0.95) if len(prepared) > 5 else prepared["Amount"].max()
    prepared.loc[prepared["Amount"] >= amount_threshold, "is_anomaly"] = True
    return prepared.sort_values(["is_anomaly", "Amount"], ascending=[False, False])


def summarize_fraud_alerts(anomaly_df: pd.DataFrame) -> List[str]:
    """Create user-facing fraud or unusual activity alerts."""
    alerts: List[str] = []
    flagged = anomaly_df[anomaly_df["is_anomaly"]].head(5)
    for row in flagged.itertuples(index=False):
        alerts.append(
            f"Unusual transaction detected: {row.Description} for Rs. {row.Amount:,.0f} on {row.Date.strftime('%d %b %Y')}."
        )
    return alerts
