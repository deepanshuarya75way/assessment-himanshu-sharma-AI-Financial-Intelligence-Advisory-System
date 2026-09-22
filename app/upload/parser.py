"""Parsing and cleaning utilities for uploaded transaction data."""

from __future__ import annotations

from io import BytesIO
from typing import Iterable

import pandas as pd

from app.prediction.model_loader import predict_missing_category
from utils.helpers import ensure_datetime_column, infer_category_from_description, normalize_amounts


REQUIRED_COLUMNS = ["Date", "Description", "Amount"]
OPTIONAL_COLUMNS = ["Category"]


def load_csv(uploaded_file: BytesIO) -> pd.DataFrame:
    """Read a CSV upload safely."""
    return pd.read_csv(uploaded_file)


def clean_transactions(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Validate, standardize, and enrich transaction data."""
    if dataframe is None or dataframe.empty:
        raise ValueError("The uploaded data is empty.")

    normalized_columns = {column: column.strip().title() for column in dataframe.columns}
    prepared = dataframe.rename(columns=normalized_columns).copy()

    missing = [column for column in REQUIRED_COLUMNS if column not in prepared.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    if "Category" not in prepared.columns:
        prepared["Category"] = None

    prepared = prepared[["Date", "Description", "Amount", "Category"]]
    prepared["Description"] = prepared["Description"].astype(str).str.strip()
    prepared["Category"] = prepared["Category"].where(prepared["Category"].notna(), None)

    prepared = ensure_datetime_column(prepared, "Date")
    prepared = normalize_amounts(prepared)
    prepared = prepared.dropna(subset=["Date"])
    prepared = prepared[prepared["Description"].str.len() > 0]
    prepared = prepared[prepared["Amount"] > 0]

    def _resolve_category(row: pd.Series) -> str:
        if isinstance(row["Category"], str) and row["Category"].strip():
            return row["Category"].strip().title()
        rule_category = infer_category_from_description(row["Description"])
        if rule_category:
            return rule_category
        return predict_missing_category(row["Description"])

    prepared["Category"] = prepared.apply(_resolve_category, axis=1)
    prepared = prepared.sort_values("Date").reset_index(drop=True)
    return prepared


def prepare_manual_entry(entries: Iterable[dict]) -> pd.DataFrame:
    """Convert manual UI transaction entries into the shared dataframe schema."""
    return clean_transactions(pd.DataFrame(list(entries)))
