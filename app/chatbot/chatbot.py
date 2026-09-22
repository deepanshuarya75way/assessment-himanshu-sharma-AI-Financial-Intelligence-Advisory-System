"""Optional personal finance chatbot."""

from __future__ import annotations

import streamlit as st

from app.chatbot.nlp_utils import detect_intent
from app.insights.generate_insights import generate_financial_summary


def build_chatbot_response(question: str, summary: dict[str, object]) -> str:
    """Generate a concise response from computed financial signals."""
    intent = detect_intent(question)
    if intent == "overspending":
        return str(summary["insights"][0]) if summary.get("insights") else "I need more data to identify overspending."
    if intent == "fraud":
        alerts = summary.get("fraud_alerts") or []
        return alerts[0] if alerts else "I do not see any major anomaly in your latest transactions."
    if intent == "investment":
        return str(summary.get("investment_recommendation", "No investment recommendation available yet."))
    if intent == "health":
        return f"Your Financial Health Score is {summary['health_score']} which is rated as {summary['health_label']}."
    if intent == "forecast":
        return f"Your next month expense is projected around Rs. {summary['forecast']['next_month_expense']:,.0f}."
    return "Ask me about overspending, savings, fraud alerts, financial health score, or investment ideas."


def render_chatbot(dataframe, monthly_income: float) -> None:
    """Render the in-app finance advisor chatbot."""
    st.subheader("AI Advisor Chatbot")
    st.caption("Ask quick questions about your spending, savings, fraud alerts, or investment options.")
    summary = generate_financial_summary(dataframe, monthly_income)

    question = st.text_input(
        "Ask the advisor",
        placeholder="Where am I overspending?",
        key="chatbot_question",
    )
    if st.button("Ask Advisor", use_container_width=False):
        if not question.strip():
            st.warning("Please enter a question for the advisor.")
        else:
            response = build_chatbot_response(question, summary)
            st.session_state["chat_history"] = st.session_state.get("chat_history", []) + [
                {"question": question, "response": response}
            ]

    for item in reversed(st.session_state.get("chat_history", [])):
        st.markdown(f"**You:** {item['question']}")
        st.markdown(f"**Advisor:** {item['response']}")
