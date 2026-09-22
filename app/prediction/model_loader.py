"""Model loading and bootstrap helpers."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from app.config import ML_MODELS_DIR, SAMPLE_DATA_PATH, ensure_directories
from utils.constants import EXPENSE_CATEGORIES
from utils.helpers import infer_category_from_description


CLASSIFIER_PATH = ML_MODELS_DIR / "expense_classifier.pkl"
PREDICTION_PATH = ML_MODELS_DIR / "prediction_model.pkl"
ANOMALY_PATH = ML_MODELS_DIR / "anomaly_model.pkl"


def _safe_load(path: Path):
    try:
        if path.exists() and path.stat().st_size > 0:
            return joblib.load(path)
    except Exception:
        return None
    return None


def _training_dataframe() -> pd.DataFrame:
    if SAMPLE_DATA_PATH.exists():
        sample = pd.read_csv(SAMPLE_DATA_PATH)
    else:
        sample = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])

    synthetic_records = [
        ("2026-01-01", "Swiggy lunch", 350, "Food"),
        ("2026-01-02", "Uber office ride", 280, "Travel"),
        ("2026-01-03", "Electricity payment", 1900, "Utilities"),
        ("2026-01-04", "Amazon electronics", 4500, "Shopping"),
        ("2026-01-05", "Netflix family plan", 649, "Entertainment"),
        ("2026-01-06", "Doctor appointment", 1200, "Health"),
        ("2026-01-07", "Udemy ML course", 1099, "Education"),
        ("2026-01-08", "Mutual fund SIP", 5000, "Investment"),
        ("2026-01-09", "Rent payment", 18000, "Bills"),
        ("2026-01-10", "Dmart groceries", 3800, "Groceries"),
    ]
    synthetic = pd.DataFrame(synthetic_records, columns=["Date", "Description", "Amount", "Category"])
    return pd.concat([sample, synthetic], ignore_index=True)


def build_expense_classifier() -> Pipeline:
    """Train a lightweight text classifier for expense categorization."""
    training_df = _training_dataframe()
    training_df = training_df.dropna(subset=["Description", "Category"])
    classifier = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english")),
            ("model", LogisticRegression(max_iter=400, class_weight="balanced")),
        ]
    )
    classifier.fit(training_df["Description"].astype(str), training_df["Category"].astype(str))
    joblib.dump(classifier, CLASSIFIER_PATH)
    return classifier


def build_prediction_model() -> RandomForestRegressor:
    """Train a baseline regressor on monthly expense trends."""
    training_df = _training_dataframe()
    monthly = (
        pd.to_datetime(training_df["Date"], errors="coerce")
        .to_frame(name="Date")
        .assign(Amount=pd.to_numeric(training_df["Amount"], errors="coerce").fillna(0.0).abs())
    )
    monthly["MonthPeriod"] = monthly["Date"].dt.to_period("M")
    grouped = monthly.groupby("MonthPeriod")["Amount"].sum().reset_index()
    grouped["month_index"] = np.arange(len(grouped))
    grouped["lag_1"] = grouped["Amount"].shift(1).fillna(grouped["Amount"].mean())
    grouped["lag_2"] = grouped["Amount"].shift(2).fillna(grouped["Amount"].mean())

    model = RandomForestRegressor(n_estimators=150, random_state=42)
    model.fit(grouped[["month_index", "lag_1", "lag_2"]], grouped["Amount"])
    joblib.dump(model, PREDICTION_PATH)
    return model


def build_anomaly_model() -> IsolationForest:
    """Train a simple anomaly detector on transaction behavior."""
    training_df = _training_dataframe()
    dates = pd.to_datetime(training_df["Date"], errors="coerce")
    amounts = pd.to_numeric(training_df["Amount"], errors="coerce").fillna(0.0).abs()
    categories = training_df["Category"].fillna("").astype(str)
    category_codes = categories.astype("category").cat.codes
    features = np.column_stack(
        [
            amounts,
            dates.dt.day.fillna(1).astype(int),
            dates.dt.weekday.fillna(0).astype(int),
            category_codes,
        ]
    )
    model = IsolationForest(contamination=0.08, random_state=42)
    model.fit(features)
    joblib.dump(model, ANOMALY_PATH)
    return model


@st.cache_resource(show_spinner=False)
def get_expense_classifier():
    """Load or rebuild the expense classifier."""
    ensure_directories()
    return _safe_load(CLASSIFIER_PATH) or build_expense_classifier()


@st.cache_resource(show_spinner=False)
def get_prediction_model():
    """Load or rebuild the forecasting model."""
    ensure_directories()
    return _safe_load(PREDICTION_PATH) or build_prediction_model()


@st.cache_resource(show_spinner=False)
def get_anomaly_model():
    """Load or rebuild the anomaly detector."""
    ensure_directories()
    return _safe_load(ANOMALY_PATH) or build_anomaly_model()


def predict_missing_category(description: str) -> str:
    """Fast path for simple category prediction."""
    inferred = infer_category_from_description(description)
    if inferred:
        return inferred
    classifier = get_expense_classifier()
    prediction = classifier.predict([description or "unknown purchase"])[0]
    if prediction in EXPENSE_CATEGORIES:
        return str(prediction)
    return "Other"
