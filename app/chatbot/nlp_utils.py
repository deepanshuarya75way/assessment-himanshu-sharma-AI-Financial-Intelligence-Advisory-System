"""Simple intent detection utilities for the in-app chatbot."""

from __future__ import annotations


def detect_intent(question: str) -> str:
    """Classify the user question into a supported chatbot intent."""
    lowered = (question or "").strip().lower()
    if any(term in lowered for term in ["overspend", "spending too much", "save money"]):
        return "overspending"
    if any(term in lowered for term in ["fraud", "unusual", "anomaly"]):
        return "fraud"
    if any(term in lowered for term in ["invest", "sip", "fd", "mutual fund"]):
        return "investment"
    if any(term in lowered for term in ["health score", "financial health"]):
        return "health"
    if any(term in lowered for term in ["predict", "forecast", "next month"]):
        return "forecast"
    return "general"
