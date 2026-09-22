"""SQLite database management utilities."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Generator

import pandas as pd

from app.config import DATABASE_PATH, ensure_directories


def initialize_database() -> None:
    """Create required database tables for the application."""
    ensure_directories()
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        connection.commit()


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Yield a SQLite connection with Row-based results."""
    initialize_database()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def save_transactions(user_id: int, dataframe: pd.DataFrame, source: str = "upload") -> None:
    """Persist a set of transactions for a user."""
    if dataframe.empty:
        return

    records = [
        (
            int(user_id),
            row.Date.strftime("%Y-%m-%d"),
            str(row.Description),
            float(row.Amount),
            str(row.Category),
            source,
        )
        for row in dataframe.itertuples(index=False)
    ]

    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO transactions (user_id, date, description, amount, category, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            records,
        )


def load_transactions(user_id: int) -> pd.DataFrame:
    """Fetch persisted transactions for a user."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT date, description, amount, category, source
            FROM transactions
            WHERE user_id = ?
            ORDER BY date ASC, id ASC
            """,
            (int(user_id),),
        ).fetchall()

    if not rows:
        return pd.DataFrame(columns=["Date", "Description", "Amount", "Category", "Source"])

    dataframe = pd.DataFrame(rows, columns=["Date", "Description", "Amount", "Category", "Source"])
    dataframe["Date"] = pd.to_datetime(dataframe["Date"], errors="coerce")
    dataframe["Amount"] = pd.to_numeric(dataframe["Amount"], errors="coerce").fillna(0.0)
    return dataframe


def replace_transactions(user_id: int, dataframe: pd.DataFrame, source: str = "upload") -> None:
    """Replace all transactions for a user with a new curated set."""
    with get_connection() as connection:
        connection.execute("DELETE FROM transactions WHERE user_id = ?", (int(user_id),))
    save_transactions(user_id=user_id, dataframe=dataframe, source=source)
