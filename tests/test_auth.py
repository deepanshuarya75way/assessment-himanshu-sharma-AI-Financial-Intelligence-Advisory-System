"""Authentication tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth.auth_utils import create_user, hash_password, login_user, verify_password


def test_hash_and_verify_password() -> None:
    password_hash = hash_password("SecurePass123")
    assert verify_password("SecurePass123", password_hash) is True
    assert verify_password("WrongPass", password_hash) is False


def test_create_and_login_user_with_unique_name() -> None:
    username = "test_user_auth_case"
    create_user(username, "SecurePass123")
    success, _, user = login_user(username, "SecurePass123")
    assert success is True
    assert user is not None
    assert user["username"] == username
