"""Login UI for existing users."""

from __future__ import annotations

import streamlit as st

from app.auth.auth_utils import login_user


def render_login() -> None:
    """Render the login form and persist the authenticated session."""
    with st.container(border=True):
        st.subheader("Welcome back")
        st.caption("Log in to access your dashboards, insights, and financial alerts.")

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                max_chars=50,
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                max_chars=128,
            )
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            success, message, user = login_user(username=username, password=password)
            if not success or user is None:
                st.error(message)
                return

            st.session_state["authenticated"] = True
            st.session_state["user_id"] = user["id"]
            st.session_state["username"] = user["username"]
            st.session_state["logged_in_user"] = user
            st.session_state["current_view"] = "dashboard"
            st.success(message)
            st.rerun()

        st.markdown("Don't have an account yet?")
        if st.button("Create Account", key="go_to_signup", use_container_width=True):
            st.session_state["auth_screen"] = "signup"
            st.rerun()
