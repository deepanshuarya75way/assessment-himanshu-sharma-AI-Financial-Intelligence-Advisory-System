"""Reusable authentication helpers for user creation and login."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Any, Dict, Optional, Tuple

from app.config import MIN_PASSWORD_LENGTH, PASSWORD_SALT_BYTES, PBKDF2_ITERATIONS
from database.db_manager import get_connection


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a random salt."""
    if not password:
        raise ValueError("Password is required.")

    salt = secrets.token_hex(PASSWORD_SALT_BYTES)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return f"{salt}${derived_key.hex()}"


def verify_password(password: str, stored_password_hash: str) -> bool:
    """Verify a password against the stored salted PBKDF2 hash."""
    try:
        salt, expected_hash = stored_password_hash.split("$", maxsplit=1)
    except ValueError:
        return False

    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return hmac.compare_digest(derived_key.hex(), expected_hash)


def validate_credentials(username: str, password: str) -> Tuple[bool, str]:
    """Validate signup/login inputs before hitting persistence."""
    cleaned_username = username.strip()

    if not cleaned_username:
        return False, "Username is required."

    if len(cleaned_username) < 3:
        return False, "Username must be at least 3 characters long."

    if not password:
        return False, "Password is required."

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."

    return True, ""


def create_user(username: str, password: str) -> Tuple[bool, str]:
    """Create a new user in SQLite with a securely hashed password."""
    is_valid, message = validate_credentials(username, password)
    if not is_valid:
        return False, message

    cleaned_username = username.strip().lower()
    password_hash = hash_password(password)

    with get_connection() as connection:
        existing_user = connection.execute(
            "SELECT id FROM users WHERE username = ?",
            (cleaned_username,),
        ).fetchone()

        if existing_user:
            return False, "Username already exists. Please choose another one."

        connection.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (cleaned_username, password_hash),
        )

    return True, "Account created successfully. You can now log in."


def login_user(username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Authenticate a user and return a safe user payload for the session."""
    cleaned_username = username.strip().lower()

    if not cleaned_username or not password:
        return False, "Please enter both username and password.", None

    with get_connection() as connection:
        user = connection.execute(
            "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
            (cleaned_username,),
        ).fetchone()

    if user is None or not verify_password(password, user["password_hash"]):
        return False, "Invalid username or password.", None

    return (
        True,
        "Login successful.",
        {
            "id": user["id"],
            "username": user["username"],
            "created_at": user["created_at"],
        },
    )
