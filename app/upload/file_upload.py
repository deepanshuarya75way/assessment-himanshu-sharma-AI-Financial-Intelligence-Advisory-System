"""Upload and manual-entry user interface."""

from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

from app.config import SAMPLE_DATA_PATH
from app.upload.parser import clean_transactions, load_csv, prepare_manual_entry
from database.db_manager import replace_transactions
from utils.constants import EXPENSE_CATEGORIES


def _sample_preview() -> None:
    if SAMPLE_DATA_PATH.exists():
        with st.expander("Preview sample dataset"):
            preview = pd.read_csv(SAMPLE_DATA_PATH).head(10)
            st.dataframe(preview, use_container_width=True)


def render_data_input(user_id: int) -> Optional[pd.DataFrame]:
    """Render upload and manual entry options and persist valid data."""
    st.subheader("Data Input Center")
    st.caption("Upload your bank statement CSV or add transactions manually.")

    st.download_button(
        label="Download Sample CSV",
        data=SAMPLE_DATA_PATH.read_bytes(),
        file_name="sample_data.csv",
        mime="text/csv",
        use_container_width=False,
    )
    if st.button("Load Sample Dataset", key="load_sample_data"):
        sample_df = clean_transactions(pd.read_csv(SAMPLE_DATA_PATH))
        replace_transactions(user_id=user_id, dataframe=sample_df, source="sample")
        st.session_state["cleaned_data"] = sample_df
        st.success("Sample dataset loaded successfully.")
    _sample_preview()

    upload_tab, manual_tab = st.tabs(["Upload CSV", "Manual Entry"])

    with upload_tab:
        uploaded_file = st.file_uploader("Upload transactions CSV", type=["csv"])
        if uploaded_file is not None:
            with st.spinner("Parsing and cleaning your transactions..."):
                try:
                    parsed = clean_transactions(load_csv(uploaded_file))
                except Exception as error:
                    st.error(f"File processing failed: {error}")
                else:
                    replace_transactions(user_id=user_id, dataframe=parsed, source="upload")
                    st.session_state["cleaned_data"] = parsed
                    st.success(f"{len(parsed)} transactions uploaded successfully.")
                    st.dataframe(parsed.tail(12), use_container_width=True)

    with manual_tab:
        with st.form("manual_entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            date_value = col1.date_input("Date")
            amount_value = col2.number_input("Amount", min_value=0.0, step=50.0)
            description = st.text_input("Description", placeholder="e.g. Swiggy order, Electricity bill")
            category = st.selectbox("Category", options=["Auto-detect"] + EXPENSE_CATEGORIES)
            submitted = st.form_submit_button("Add Transaction", use_container_width=True)

        if submitted:
            entry = {
                "Date": date_value,
                "Description": description,
                "Amount": amount_value,
                "Category": None if category == "Auto-detect" else category,
            }
            try:
                parsed_entry = prepare_manual_entry([entry])
            except Exception as error:
                st.error(f"Manual entry failed: {error}")
            else:
                existing = st.session_state.get("cleaned_data")
                combined = (
                    pd.concat([existing, parsed_entry], ignore_index=True)
                    if isinstance(existing, pd.DataFrame) and not existing.empty
                    else parsed_entry
                )
                combined = combined.sort_values("Date").reset_index(drop=True)
                replace_transactions(user_id=user_id, dataframe=combined, source="manual")
                st.session_state["cleaned_data"] = combined
                st.success("Transaction added successfully.")

    return st.session_state.get("cleaned_data")
