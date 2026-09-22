"""High-level insight generation for the dashboard."""

from __future__ import annotations

from typing import Dict

import pandas as pd

from app.insights.rules_engine import ESSENTIAL_CATEGORIES, build_investment_recommendation, build_spending_rules, category_breakdown
from app.prediction.predict import detect_anomalies, predict_next_month_expense, summarize_fraud_alerts
from utils.helpers import compute_financial_health_score


def generate_financial_summary(dataframe: pd.DataFrame, monthly_income: float) -> Dict[str, object]:
    """Generate metrics, predictions, insights, and anomaly summaries."""
    if dataframe.empty:
        return {
            "total_expense": 0.0,
            "monthly_spend": pd.Series(dtype=float),
            "category_spend": {},
            "forecast": {"next_month_expense": 0.0, "average_monthly_expense": 0.0},
            "health_score": 0,
            "health_label": "Needs Attention",
            "monthly_savings": monthly_income,
            "insights": ["Upload data to unlock AI insights."],
            "investment_recommendation": "No recommendation available yet.",
            "anomaly_df": dataframe,
            "fraud_alerts": [],
        }

    prepared = dataframe.copy()
    prepared["Month"] = prepared["Date"].dt.to_period("M").astype(str)
    expense_df = prepared[prepared["Category"] != "Transfer"].copy()
    if expense_df.empty:
        expense_df = prepared.copy()

    total_expense = float(expense_df["Amount"].sum())
    monthly_spend = expense_df.groupby("Month")["Amount"].sum()
    category_spend = category_breakdown(expense_df)
    forecast = predict_next_month_expense(expense_df)
    anomaly_df = detect_anomalies(expense_df)
    fraud_alerts = summarize_fraud_alerts(anomaly_df)

    essential_spend = expense_df[expense_df["Category"].isin(ESSENTIAL_CATEGORIES)]["Amount"].sum()
    essentials_ratio = float(essential_spend / total_expense) if total_expense else 0.0
    average_monthly_spend = float(monthly_spend.mean()) if not monthly_spend.empty else 0.0
    monthly_savings = max(monthly_income - average_monthly_spend, 0.0)
    health_score, health_label = compute_financial_health_score(
        total_expense=average_monthly_spend,
        monthly_income=monthly_income,
        monthly_spend_series=monthly_spend,
        essentials_ratio=essentials_ratio,
    )
    insights = build_spending_rules(expense_df, monthly_income, forecast["next_month_expense"])
    investment_recommendation = build_investment_recommendation(monthly_savings)

    return {
        "total_expense": total_expense,
        "monthly_spend": monthly_spend,
        "category_spend": category_spend,
        "forecast": forecast,
        "health_score": health_score,
        "health_label": health_label,
        "monthly_savings": monthly_savings,
        "insights": insights,
        "investment_recommendation": investment_recommendation,
        "anomaly_df": anomaly_df,
        "fraud_alerts": fraud_alerts,
    }
