"""Prediction and parser tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.prediction.predict import detect_anomalies, predict_next_month_expense
from app.upload.parser import clean_transactions


def test_clean_transactions_predicts_missing_category() -> None:
    dataframe = pd.DataFrame(
        [
            {"Date": "2026-01-01", "Description": "Swiggy order", "Amount": 350},
            {"Date": "2026-01-02", "Description": "Uber ride", "Amount": 250},
        ]
    )
    cleaned = clean_transactions(dataframe)
    assert "Category" in cleaned.columns
    assert cleaned["Category"].isna().sum() == 0


def test_prediction_and_anomaly_pipeline_returns_expected_fields() -> None:
    dataframe = clean_transactions(
        pd.DataFrame(
            [
                {"Date": "2025-10-01", "Description": "Rent", "Amount": 18000, "Category": "Bills"},
                {"Date": "2025-11-01", "Description": "Rent", "Amount": 18500, "Category": "Bills"},
                {"Date": "2025-12-01", "Description": "Rent", "Amount": 19000, "Category": "Bills"},
                {"Date": "2025-12-05", "Description": "Flight ticket", "Amount": 32000, "Category": "Travel"},
            ]
        )
    )
    forecast = predict_next_month_expense(dataframe)
    anomalies = detect_anomalies(dataframe)

    assert forecast["next_month_expense"] >= 0
    assert "is_anomaly" in anomalies.columns
