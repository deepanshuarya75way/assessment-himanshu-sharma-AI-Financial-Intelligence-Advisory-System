"""Rule engine for financial intelligence insights."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from utils.constants import INVESTMENT_GUIDANCE


ESSENTIAL_CATEGORIES = {"Bills", "Utilities", "Groceries", "Health", "Education"}


def build_spending_rules(dataframe: pd.DataFrame, monthly_income: float, forecast: float) -> List[str]:
    """Generate rule-based financial insights."""
    insights: List[str] = []
    if dataframe.empty:
        return ["Upload transaction data to unlock AI insights."]

    total_spend = float(dataframe["Amount"].sum())
    category_spend = dataframe.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    top_category = category_spend.index[0]
    top_amount = float(category_spend.iloc[0])
    monthly_average = total_spend / max(dataframe["Date"].dt.to_period("M").nunique(), 1)
    savings = max(monthly_income - monthly_average, 0.0)

    if top_amount / max(total_spend, 1.0) > 0.30:
        insights.append(f"You are overspending on {top_category.lower()}. It contributes Rs. {top_amount:,.0f} of total spending.")

    subscription_spend = category_spend.get("Entertainment", 0.0)
    if subscription_spend > monthly_income * 0.08:
        insights.append(f"Reduce subscriptions and leisure spend to save around Rs. {subscription_spend * 0.20:,.0f} per month.")

    if forecast > monthly_average * 1.10:
        insights.append(f"Your next month's spend is projected to rise to Rs. {forecast:,.0f}. Plan a tighter budget now.")

    if savings < monthly_income * 0.15:
        insights.append("Your savings buffer is below the ideal 15% mark. Tightening discretionary spending would improve resilience.")

    if not insights:
        insights.append("Your spending looks balanced. Keep monitoring categories with the highest month-on-month growth.")

    return insights


def build_investment_recommendation(monthly_savings: float) -> str:
    """Recommend an investment action based on free monthly cash flow."""
    for threshold, message in INVESTMENT_GUIDANCE:
        if monthly_savings >= threshold:
            return message
    return "Focus on stabilizing savings and building an emergency fund before taking investment risk."


def category_breakdown(dataframe: pd.DataFrame) -> Dict[str, float]:
    """Return category share data as a dictionary."""
    if dataframe.empty:
        return {}
    grouped = dataframe.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    return {str(category): float(amount) for category, amount in grouped.items()}
