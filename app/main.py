"""Primary Streamlit entry point for the AI Financial Intelligence platform."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
import sys
from typing import Any, Dict

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@dataclass(frozen=True)
class ThemePalette:
    """Visual palette used across the fintech dashboard."""

    primary: str = "#18A957"
    secondary: str = "#0F172A"
    accent: str = "#E11D48"
    background: str = "#F4F7FB"
    card: str = "#FFFFFF"
    text: str = "#0F172A"
    muted: str = "#64748B"


DEFAULT_SESSION_STATE: Dict[str, Any] = {
    "authenticated": False,
    "user_id": None,
    "username": "",
    "logged_in_user": None,
    "current_view": "welcome",
    "auth_screen": "login",
    "uploaded_data": None,
    "cleaned_data": None,
    "monthly_income": 60000.0,
    "chat_history": [],
    "insights": [],
    "predictions": {},
    "fraud_alerts": [],
    "theme_mode": "light",
}


def configure_page() -> None:
    """Apply top-level Streamlit page settings once."""
    st.set_page_config(
        page_title="AI Financial Intelligence & Advisory System",
        page_icon=":material/monitoring:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def initialize_session_state() -> None:
    """Seed Streamlit session state with safe defaults."""
    for key, value in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def inject_global_styles() -> None:
    """Inject a modern fintech visual layer into the app shell."""
    palette = ThemePalette()
    st.markdown(
        f"""
        <style>
             :root {{
                --primary: {palette.primary};
                --secondary: {palette.secondary};
                --accent: {palette.accent};
                --bg: {palette.background};
                --card: {palette.card};
                --text: {palette.text};
                --muted: {palette.muted};
            }}

            .stApp {{
                background:
                    radial-gradient(circle at top right, rgba(24, 169, 87, 0.08), transparent 22%),
                    linear-gradient(180deg, #f8fbff 0%, var(--bg) 100%);
                color: var(--text);
            }}

            .block-container {{
                padding-top: 1.5rem;
                padding-bottom: 2rem;
                max-width: 1280px;
            }}

            .hero-card {{
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.97), rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 22px;
                padding: 2rem;
                color: white;
                box-shadow: 0 24px 60px rgba(15, 23, 42, 0.18);
                margin-bottom: 1.25rem;
            }}

            .hero-title {{
                font-size: 2.2rem;
                font-weight: 700;
                line-height: 1.15;
                margin-bottom: 0.6rem;
            }}

            .hero-subtitle {{
                font-size: 1rem;
                color: rgba(255, 255, 255, 0.8);
                margin-bottom: 0;
            }}

            .badge-row {{
                display: flex;
                gap: 0.6rem;
                flex-wrap: wrap;
                margin-top: 1rem;
            }}

            .badge {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 999px;
                padding: 0.35rem 0.8rem;
                font-size: 0.85rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_shell_header() -> None:
    """Render the welcome shell used before route-level screens."""
    st.markdown(
        """
        <section class="hero-card">
            <div class="hero-title">AI Financial Intelligence & Advisory System</div>
            <p class="hero-subtitle">
                Track spending, detect anomalies, predict future expenses, and surface
                advisor-grade money insights from a single fintech workspace.
            </p>
            <div class="badge-row">
                <span class="badge">Expense Intelligence</span>
                <span class="badge">Fraud Detection</span>
                <span class="badge">Forecasting</span>
                <span class="badge">Investment Guidance</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_bootstrap_notice() -> None:
    """Fallback content shown until route modules are implemented."""
    col1, col2, col3 = st.columns(3)
    col1.metric("Auth", "Ready", "Session enabled")
    col2.metric("Upload", "Pending", "Next step")
    col3.metric("Dashboard", "Pending", "Next step")

    st.info(
        "Project scaffold is ready. The next step will connect authentication, upload, "
        "dashboard, and AI modules into this main entry point."
    )


def handoff_to_routes() -> None:
    """
    Attempt to delegate screen rendering to the route layer.

    The import is intentionally dynamic so Step 1 remains runnable even before
    the downstream modules are fully implemented.
    """
    try:
        routes_module = import_module("app.routes")
    except ModuleNotFoundError:
        render_bootstrap_notice()
        return

    route_handler = getattr(routes_module, "render_app", None)
    if callable(route_handler):
        route_handler()
        return

    render_bootstrap_notice()


def main() -> None:
    """Application bootstrap sequence."""
    configure_page()
    initialize_session_state()
    inject_global_styles()
    render_shell_header()
    handoff_to_routes()


if __name__ == "__main__":
    main()
