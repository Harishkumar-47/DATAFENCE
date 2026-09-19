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
    assert result["scan_id"] > 0
    assert result["scanned_at"]
    assert any(source["name"] == "DATAFENCE risk engine" for source in result["sources"])

    history = security.scan_history(limit=10, current_user=user)
    assert history["count"] == 1
    assert history["items"][0]["id"] == result["scan_id"]
    assert history["items"][0]["breach_status"] == "not_found"

    action_id = result["remediation_plan"][0]["id"]
    updated = security.update_remediation(
        action_id, security.RemediationUpdate(resolved=True), user,
    )
    assert updated["resolved"] is True
    with auth.get_db() as db:
        saved = db.execute(
            "SELECT resolved FROM remediation_status WHERE user_id = ? AND action_id = ?",
            (user["id"], action_id),
        ).fetchone()
    assert saved["resolved"] == 1

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


@pytest.mark.parametrize("domain", [
    "example.com", "accounts.example.co.uk", "sub-domain.example.org",
])
def test_safe_domain_accepts_hostnames(domain):
    assert security.safe_domain(domain) == domain


@pytest.mark.parametrize("domain", [
    "javascript:alert(1)", "example.com/path", "user@example.com", "localhost",
])
def test_safe_domain_rejects_unsafe_values(domain):
    assert security.safe_domain(domain) == ""
