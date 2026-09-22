"""Application-wide constants used by the fintech workflows."""

from __future__ import annotations


EXPENSE_CATEGORIES = [
    "Food",
    "Travel",
    "Bills",
    "Shopping",
    "Entertainment",
    "Health",
    "Education",
    "Investment",
    "Transfer",
    "Groceries",
    "Utilities",
    "Other",
]

MONTH_ORDER = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

CATEGORY_COLORS = {
    "Food": "#F97316",
    "Travel": "#06B6D4",
    "Bills": "#EF4444",
    "Shopping": "#A855F7",
    "Entertainment": "#EC4899",
    "Health": "#10B981",
    "Education": "#3B82F6",
    "Investment": "#16A34A",
    "Transfer": "#64748B",
    "Groceries": "#84CC16",
    "Utilities": "#F59E0B",
    "Other": "#94A3B8",
}

KEYWORD_TO_CATEGORY = {
    "swiggy": "Food",
    "zomato": "Food",
    "restaurant": "Food",
    "cafe": "Food",
    "uber": "Travel",
    "ola": "Travel",
    "metro": "Travel",
    "flight": "Travel",
    "electricity": "Utilities",
    "water": "Utilities",
    "internet": "Bills",
    "rent": "Bills",
    "emi": "Bills",
    "amazon": "Shopping",
    "flipkart": "Shopping",
    "mall": "Shopping",
    "netflix": "Entertainment",
    "spotify": "Entertainment",
    "movie": "Entertainment",
    "hospital": "Health",
    "pharmacy": "Health",
    "doctor": "Health",
    "course": "Education",
    "udemy": "Education",
    "mutual fund": "Investment",
    "sip": "Investment",
    "salary": "Transfer",
    "bonus": "Transfer",
    "grocery": "Groceries",
    "dmart": "Groceries",
}

INVESTMENT_GUIDANCE = [
    (15000, "You can allocate Rs. 10,000 to diversified SIPs and keep Rs. 5,000 in a liquid fund."),
    (7000, "Consider starting a SIP of Rs. 5,000 per month and keep the rest in an emergency buffer."),
    (3000, "A starter SIP of Rs. 3,000 per month in index funds would be a sensible next move."),
    (1000, "Build a recurring deposit or short-term emergency fund before taking market risk."),
]
