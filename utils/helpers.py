"""Common helper functions for data preparation and scoring."""

from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np
import pandas as pd

from app.config import DEFAULT_MONTHLY_INCOME
from utils.constants import KEYWORD_TO_CATEGORY


def safe_float(value: object, default: float = 0.0) -> float:
    """Convert a value to float safely."""
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def infer_category_from_description(description: str) -> str | None:
    """Infer a category from known transaction keywords."""
    lowered = (description or "").strip().lower()
    for keyword, category in KEYWORD_TO_CATEGORY.items():
        if keyword in lowered:
            return category
    return None


def ensure_datetime_column(dataframe: pd.DataFrame, column: str = "Date") -> pd.DataFrame:
    """Return a dataframe with a parsed datetime column."""
    prepared = dataframe.copy()
    prepared[column] = pd.to_datetime(prepared[column], errors="coerce")
    return prepared


def normalize_amounts(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Normalize amounts so expenses are positive outgoing values."""
    prepared = dataframe.copy()
    prepared["Amount"] = pd.to_numeric(prepared["Amount"], errors="coerce").fillna(0.0)
    prepared["Amount"] = prepared["Amount"].abs()
    return prepared


def compute_monthly_income(dataframe: pd.DataFrame, manual_income: float | None = None) -> float:
    """Derive a baseline monthly income from data or fallback to a default."""
    if manual_income and manual_income > 0:
        return manual_income

    if dataframe.empty:
        return DEFAULT_MONTHLY_INCOME

    monthly_expense = dataframe["Amount"].sum() / max(dataframe["Date"].dt.to_period("M").nunique(), 1)
    return max(DEFAULT_MONTHLY_INCOME, monthly_expense * 1.6)


def rolling_stability_score(values: Iterable[float]) -> float:
    """Return a stability score between 0 and 100 from monthly volatility."""
    numeric = np.array(list(values), dtype=float)
    if numeric.size <= 1:
        return 80.0
    mean_value = float(np.mean(numeric))
    if mean_value <= 0:
        return 50.0
    coefficient = float(np.std(numeric) / mean_value)
    return max(0.0, min(100.0, 100.0 - (coefficient * 100.0)))


def health_label(score: float) -> str:
    """Map numeric health score to a human-friendly label."""
    if score >= 80:
        return "Excellent"
    if score >= 65:
        return "Good"
    if score >= 45:
        return "Average"
    return "Needs Attention"


def compute_financial_health_score(
    total_expense: float,
    monthly_income: float,
    monthly_spend_series: pd.Series,
    essentials_ratio: float,
) -> Tuple[int, str]:
    """Compute the financial health score from savings, consistency, and spending mix."""
    if monthly_income <= 0:
        return 35, health_label(35)

    savings_ratio = max(0.0, (monthly_income - total_expense) / monthly_income)
    stability = rolling_stability_score(monthly_spend_series.tolist())
    spending_discipline = max(0.0, min(100.0, 100.0 - (essentials_ratio * 55.0)))
    score = int(round((savings_ratio * 45.0) + (stability * 0.30) + (spending_discipline * 0.25)))
    bounded_score = max(0, min(100, score))
    return bounded_score, health_label(bounded_score)
