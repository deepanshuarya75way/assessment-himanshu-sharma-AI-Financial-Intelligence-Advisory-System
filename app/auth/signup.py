"""Signup UI for new users."""

from __future__ import annotations

import streamlit as st

from app.auth.auth_utils import create_user


def render_signup() -> None:
    """Render the signup experience inside the auth screen."""
    with st.container(border=True):
        st.subheader("Create your account")
        st.caption("Set up secure access to your AI-powered financial workspace.")

        with st.form("signup_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="Choose a username",
                max_chars=50,
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a strong password",
                max_chars=128,
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                max_chars=128,
            )
            submitted = st.form_submit_button("Sign Up", use_container_width=True)

        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match. Please try again.")
                return

            success, message = create_user(username=username, password=password)
            if success:
                st.success(message)
                st.session_state["auth_screen"] = "login"
            else:
                st.error(message)

        st.markdown("Already registered?")
        if st.button("Back to Login", key="go_to_login", use_container_width=True):
            st.session_state["auth_screen"] = "login"
            st.rerun()
