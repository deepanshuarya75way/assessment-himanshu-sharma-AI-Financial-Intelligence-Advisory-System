"""Main dashboard screen for the fintech product."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.dashboard.charts import build_category_pie_chart, build_monthly_bar_chart
from app.dashboard.insights_ui import render_fraud_alerts, render_insights
from app.insights.generate_insights import generate_financial_summary


def render_dashboard(dataframe: pd.DataFrame, monthly_income: float) -> None:
    """Render the financial dashboard for the authenticated user."""
    st.subheader("Financial Command Center")
    st.caption("Monitor spending, savings, risk signals, and advisor-grade recommendations in one place.")

    if dataframe.empty:
        st.warning("No transaction data is available yet. Upload a CSV or add transactions manually to start.")
        return

    with st.spinner("Generating AI insights and financial signals..."):
        summary = generate_financial_summary(dataframe, monthly_income)

    metric_cols = st.columns(4)
    metric_cols[0].metric("Total Expense", f"Rs. {summary['total_expense']:,.0f}")
    metric_cols[1].metric("Savings", f"Rs. {summary['monthly_savings']:,.0f}")
    metric_cols[2].metric("Predicted Expense", f"Rs. {summary['forecast']['next_month_expense']:,.0f}")
    metric_cols[3].metric(
        "Financial Health Score",
        f"{summary['health_score']} ({summary['health_label']})",
    )

    chart_col1, chart_col2 = st.columns(2, gap="large")
    with chart_col1:
        st.plotly_chart(build_monthly_bar_chart(summary["monthly_spend"]), use_container_width=True)
    with chart_col2:
        st.plotly_chart(build_category_pie_chart(summary["category_spend"]), use_container_width=True)

    lower_left, lower_right = st.columns([1.15, 0.85], gap="large")
    with lower_left:
        render_insights(summary["insights"])
        st.markdown("### Investment Recommendation")
        st.success(summary["investment_recommendation"])
    with lower_right:
        st.markdown("### Forecast Snapshot")
        st.write(
            f"Average monthly spend: Rs. {summary['forecast']['average_monthly_expense']:,.0f}"
        )
        st.write(
            f"Projected next month spend: Rs. {summary['forecast']['next_month_expense']:,.0f}"
        )
        render_fraud_alerts(summary["fraud_alerts"])

    with st.expander("View cleaned transactions"):
        st.dataframe(dataframe.sort_values("Date", ascending=False), use_container_width=True)
