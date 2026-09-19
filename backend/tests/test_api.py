import sqlite3
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api import auth, security


request = SimpleNamespace(client=SimpleNamespace(host="test-client"))


def create_account(email="owner@example.com"):
    return auth.signup(auth.SignupRequest(
        name="Account Owner", email=email, password="correct horse battery staple",
    ), request)


def test_account_lifecycle_and_hashed_session_storage():
    body = create_account()
    token = body["token"]
    assert auth.get_current_user(f"Bearer {token}")["email"] == "owner@example.com"

    with sqlite3.connect(auth.DB_PATH) as db:
        stored = db.execute("SELECT token_hash FROM sessions").fetchone()[0]
    assert token not in stored
    assert len(stored) == 64

    auth.logout(f"Bearer {token}")
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(f"Bearer {token}")
    assert exc.value.status_code == 401


def test_login_does_not_create_unknown_accounts():
    with pytest.raises(HTTPException) as exc:
        auth.login(auth.LoginRequest(
            email="missing@example.com", password="correct horse battery staple",
        ), request)
    assert exc.value.status_code == 401
    with auth.get_db() as db:
        assert db.execute("SELECT id FROM users WHERE email = ?", ("missing@example.com",)).fetchone() is None


def test_scan_is_scoped_to_authenticated_email(monkeypatch):
    user = create_account("scan-owner@example.com")["user"]
    seen = {}

    def fake_breach(email):
        seen["email"] = email
        return {
            "status": "not_found", "available": True, "verified": True, "message": "none",
            "risk_score": 0, "risk_level": "Low", "breaches": 0,
            "breach_sites": [], "org_analysis": [],
        }

    monkeypatch.setattr(security, "check_xposedornot", fake_breach)
    result = security.full_analysis(security.SecurityAnalysisRequest(), request, user)
    assert seen["email"] == "scan-owner@example.com"
    assert result["identity"]["email"] == "scan-owner@example.com"

    with pytest.raises(ValidationError):
        security.SecurityAnalysisRequest(email="victim@example.com")


def test_provider_failure_is_not_reported_as_safe(monkeypatch):
    def fail(*args, **kwargs):
        raise security.requests.ConnectionError("offline")

    monkeypatch.setattr(security.requests, "get", fail)
    result = security.check_xposedornot("owner@example.com")
    assert result["status"] == "unavailable"
    assert result["verified"] is False
    assert result["risk_level"] == "Unknown"
