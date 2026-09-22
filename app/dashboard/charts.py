"""Interactive charts for the financial dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.constants import CATEGORY_COLORS


def build_monthly_bar_chart(monthly_spend: pd.Series) -> go.Figure:
    """Create a bar chart of monthly expenses."""
    chart_df = monthly_spend.reset_index()
    chart_df.columns = ["Month", "Amount"]
    figure = px.bar(
        chart_df,
        x="Month",
        y="Amount",
        text_auto=".2s",
        color_discrete_sequence=["#18A957"],
    )
    figure.update_layout(
        title="Monthly Expense Trend",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.9)",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return figure


def build_category_pie_chart(category_spend: dict[str, float]) -> go.Figure:
    """Create a category composition pie chart."""
    chart_df = pd.DataFrame({"Category": list(category_spend.keys()), "Amount": list(category_spend.values())})
    colors = [CATEGORY_COLORS.get(category, "#94A3B8") for category in chart_df["Category"]]
    figure = px.pie(chart_df, names="Category", values="Amount", color="Category", color_discrete_sequence=colors)
    figure.update_layout(
        title="Expense Mix by Category",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return figure
