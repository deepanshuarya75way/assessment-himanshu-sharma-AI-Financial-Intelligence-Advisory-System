"""Reusable UI blocks for insights and alerts."""

from __future__ import annotations

from typing import Iterable

import streamlit as st


def render_insights(insights: Iterable[str]) -> None:
    """Render AI insights in a compact visual block."""
    st.markdown("### AI Insights")
    for insight in insights:
        st.info(insight)


def render_fraud_alerts(alerts: Iterable[str]) -> None:
    """Render fraud or anomaly alerts."""
    st.markdown("### Fraud Alerts")
    alerts = list(alerts)
    if not alerts:
        st.success("No critical anomalies were detected in your current transaction history.")
        return
    for alert in alerts:
        st.warning(alert)
