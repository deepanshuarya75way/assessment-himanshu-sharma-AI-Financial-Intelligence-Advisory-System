"""Application routing and view orchestration."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.auth.login import render_login
from app.auth.signup import render_signup
from app.chatbot.chatbot import render_chatbot
from app.config import DEFAULT_MONTHLY_INCOME
from app.dashboard.dashboard import render_dashboard
from app.upload.file_upload import render_data_input
from database.db_manager import initialize_database, load_transactions


@st.cache_data(show_spinner=False)
def get_user_transactions(user_id: int) -> pd.DataFrame:
    """Cached user transaction loader."""
    return load_transactions(user_id)


def logout_user() -> None:
    """Clear the authenticated session and return to the welcome view."""
    st.session_state["authenticated"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = ""
    st.session_state["logged_in_user"] = None
    st.session_state["current_view"] = "welcome"
    st.session_state["cleaned_data"] = None
    st.session_state["chat_history"] = []
    st.rerun()


def render_authenticated_app() -> None:
    """Render the full authenticated fintech workflow."""
    user_id = int(st.session_state["user_id"])
    if not isinstance(st.session_state.get("cleaned_data"), pd.DataFrame):
        st.session_state["cleaned_data"] = get_user_transactions(user_id)

    with st.sidebar:
        st.markdown(f"### Hello, {st.session_state.get('username', 'User').title()}")
        st.caption("Personal finance intelligence dashboard")
        selected_page = st.radio(
            "Workspace",
            options=["Dashboard", "Data Upload", "Chatbot"],
            index=0,
        )
        monthly_income = st.number_input(
            "Monthly Income (Rs.)",
            min_value=0.0,
            value=float(st.session_state.get("monthly_income", DEFAULT_MONTHLY_INCOME)),
            step=1000.0,
        )
        st.session_state["monthly_income"] = monthly_income
        if st.button("Refresh Data", use_container_width=True):
            get_user_transactions.clear()
            st.session_state["cleaned_data"] = get_user_transactions(user_id)
            st.rerun()
        if st.button("Logout", use_container_width=True):
            logout_user()

    current_data = st.session_state.get("cleaned_data")
    if not isinstance(current_data, pd.DataFrame):
        current_data = pd.DataFrame(columns=["Date", "Description", "Amount", "Category", "Source"])
        st.session_state["cleaned_data"] = current_data

    if selected_page == "Data Upload":
        updated = render_data_input(user_id)
        if isinstance(updated, pd.DataFrame):
            get_user_transactions.clear()
    elif selected_page == "Chatbot":
        render_chatbot(current_data, monthly_income)
    else:
        render_dashboard(current_data, monthly_income)


def render_auth_screen() -> None:
    """Render login and signup tabs for unauthenticated users."""
    st.session_state.setdefault("auth_screen", "login")

    left_col, right_col = st.columns([1.05, 1], gap="large")

    with left_col:
        st.markdown("### Secure Access")
        st.write(
            "Create an account or log in to access forecasting, fraud alerts, "
            "health scores, and personalized savings guidance."
        )
        st.info("Dashboard routes stay locked until the session is authenticated.")

    with right_col:
        auth_choice = st.radio(
            "Access",
            options=["login", "signup"],
            format_func=lambda option: "Login" if option == "login" else "Create Account",
            horizontal=True,
            key="auth_screen",
            label_visibility="collapsed",
        )

        if auth_choice == "login":
            render_login()
        else:
            render_signup()


def render_app() -> None:
    """Top-level route controller called by the main Streamlit entry point."""
    initialize_database()

    if st.session_state.get("authenticated"):
        render_authenticated_app()
        return

    render_auth_screen()
