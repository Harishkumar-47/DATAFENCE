"""Security analysis for the authenticated account owner."""

import os
import re
import subprocess
from datetime import datetime, timezone
from urllib.parse import quote

import phonenumbers
import requests
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, ConfigDict, Field
from phonenumbers import carrier, geocoder

from app.api.auth import get_current_user, get_db
from app.core.rate_limit import RateLimiter
from app.engines.intelligence.intelligence_pipeline import IntelligencePipeline
from app.engines.security.security_engine import SecurityEngine

router = APIRouter(prefix="/api/security", tags=["Security"])
intelligence = IntelligencePipeline()
security_engine = SecurityEngine()
scan_limiter = RateLimiter(limit=5, window_seconds=300)
ACCOUNT_DISCOVERY_ENABLED = os.getenv("ENABLE_ACCOUNT_DISCOVERY", "false").lower() == "true"


class SecurityAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Phone metadata is local-only and optional. It never claims account or SIM linkage.
    phone: str = Field(default="", max_length=32)


class RemediationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resolved: bool


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_domain(value: str) -> str:
    domain = value.lower().strip().strip(".")
    return domain if re.fullmatch(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", domain) else ""


def unavailable_breach(reason: str) -> dict:
    return {
        "status": "unavailable", "available": False, "verified": False,
        "message": reason, "risk_score": 0, "risk_level": "Unknown",
        "breaches": 0, "breach_sites": [], "org_analysis": [],
    }


def check_xposedornot(email: str) -> dict:
    """Query breach data while preserving unknown/error states."""
    try:
        response = requests.get(
            f"https://api.xposedornot.com/v1/check-email/{quote(email, safe='')}",
            timeout=(3.05, 10),
            headers={"User-Agent": "DATAFENCE/1.0"},
        )
    except requests.RequestException:
        return unavailable_breach("The breach provider could not be reached.")

    if response.status_code == 404:
        return {
            "status": "not_found", "available": True, "verified": True,
            "message": "No matching breach was reported by this provider.",
            "risk_score": 0, "risk_level": "Low", "breaches": 0,
            "breach_sites": [], "org_analysis": [],
        }
    if response.status_code == 429:
        return unavailable_breach("The breach provider rate limit was reached.")
    if response.status_code != 200:
        return unavailable_breach(f"The breach provider returned HTTP {response.status_code}.")

    try:
        data = response.json()
    except requests.JSONDecodeError:
        return unavailable_breach("The breach provider returned an invalid response.")

    raw_breaches = data.get("breaches", [])
    breach_sites = raw_breaches[0] if raw_breaches and isinstance(raw_breaches[0], list) else raw_breaches
    breach_sites = [str(site) for site in breach_sites] if isinstance(breach_sites, list) else []
    organizations = []

    if breach_sites:
        try:
            analytics = requests.get(
                "https://api.xposedornot.com/v1/breach-analytics",
                params={"email": email}, timeout=(3.05, 10),
                headers={"User-Agent": "DATAFENCE/1.0"},
            )
            if analytics.status_code == 200:
                details = analytics.json().get("ExposedBreaches", {}).get("breaches_details", [])
                for item in details:
                    count = int(item.get("xposed_records") or 0)
                    organizations.append({
                        "name": str(item.get("breach") or "Unknown organization"),
                        "domain": safe_domain(str(item.get("domain") or "")),
                        "breach_count": count,
                        "high_risk": count > 10_000_000,
                        "xposed_data": str(item.get("xposed_data") or ""),
                    })
        except (requests.RequestException, ValueError, TypeError, AttributeError):
            # The primary lookup remains valid even if optional details fail.
            pass

    count = len(breach_sites)
    return {
        "status": "found" if count else "not_found", "available": True,
        "verified": True, "message": f"Provider lookup completed with {count} match(es).",
        "risk_score": min(count * 15, 100),
        "risk_level": "High" if count > 3 else "Medium" if count else "Low",
        "breaches": count, "breach_sites": breach_sites, "org_analysis": organizations,
    }


def inspect_phone(phone: str) -> dict:
    if not phone:
        return {"status": "not_provided"}
    try:
        parsed = phonenumbers.parse(phone, None)
    except phonenumbers.NumberParseException:
        return {"status": "invalid", "message": "Use international format, for example +14155552671."}
    if not phonenumbers.is_valid_number(parsed):
        return {"status": "invalid", "message": "The phone number is not valid."}
    return {
        "status": "valid", "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
        "region": geocoder.description_for_number(parsed, "en") or None,
        "carrier": carrier.name_for_number(parsed, "en") or None,
        "disclaimer": "Carrier and region are numbering-plan metadata, not a live trace.",
    }


def discover_accounts(email: str) -> dict:
    if not ACCOUNT_DISCOVERY_ENABLED:
        return {"status": "disabled", "sites": [], "message": "Account discovery is disabled by the operator."}
    try:
        process = subprocess.run(
            ["holehe", email, "--only-used", "--no-color"], capture_output=True,
            text=True, timeout=25, check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "sites": [], "message": "Account discovery timed out."}
    except OSError:
        return {"status": "unavailable", "sites": [], "message": "Account discovery is unavailable."}
    if process.returncode != 0:
        return {"status": "failed", "sites": [], "message": "Account discovery failed."}
    sites = [line[3:].strip() for line in process.stdout.splitlines() if line.startswith("[+]")]
    return {"status": "complete", "sites": sites, "message": f"Checked configured services; found {len(sites)} match(es)."}


@router.post("/full-analysis")
def full_analysis(
    payload: SecurityAnalysisRequest,
    request: Request,
    current_user=Depends(get_current_user),
):
    scan_limiter.check(request)
    target_email = current_user["email"]
    phone = inspect_phone(payload.phone.strip())

    data_points = [{"type": "email", "value": target_email}]
    connections = [{"type": "email"}]
    if phone["status"] == "valid":
        data_points.append({"type": "phone", "value": phone["e164"]})
        connections.append({"type": "contacts"})
        if phone.get("region"):
            data_points.append({"type": "location", "value": phone["region"]})

    result = intelligence.analyze({
        "identity": {"id": current_user["id"], "name": current_user["name"], "email": target_email},
        "data_points": data_points, "connections": connections,
    })
    breach = check_xposedornot(target_email)
    discovery = discover_accounts(target_email)
    assessment = security_engine.assess(
        exposure_score=max(result["exposure"]["score"], breach["risk_score"]),
        inference_score=result["inference"]["score"],
        threat_score=result["threat"]["score"],
        blast_radius=result["blast_radius"]["score"],
    )

    plan = []
    for org in breach["org_analysis"]:
        if org["high_risk"]:
            plan.append({
                "id": f"org-{len(plan)}", "title": f"Review your {org['name']} account",
                "description": "Change reused passwords, enable MFA, and close the account if it is no longer needed.",
                "critical": True, "priority": "critical", "domain": org["domain"],
            })
    if breach["breaches"]:
        plan.append({
            "id": "rotate-passwords", "title": "Rotate affected passwords",
            "description": "Use unique generated passwords and enable multi-factor authentication on affected accounts.",
            "critical": True, "priority": "critical",
        })
        exposed_types = " ".join(
            organization.get("xposed_data", "") for organization in breach["org_analysis"]
        ).lower()
        if any(term in exposed_types for term in ("password", "credential")):
            plan.append({
                "id": "enable-mfa", "title": "Enable phishing-resistant MFA",
                "description": "Prefer passkeys or security keys; avoid SMS where stronger factors are available.",
                "critical": True, "priority": "critical",
            })
        if any(term in exposed_types for term in ("financial", "credit", "bank", "payment")):
            plan.append({
                "id": "monitor-finances", "title": "Monitor financial accounts",
                "description": "Review statements, enable transaction alerts, and consider a credit freeze if identity data was exposed.",
                "critical": True, "priority": "critical",
            })
        if any(term in exposed_types for term in ("phone", "address", "name", "email")):
            plan.append({
                "id": "phishing-watch", "title": "Prepare for targeted phishing",
                "description": "Treat unexpected recovery messages and calls as suspicious; navigate to services directly instead of using links.",
                "critical": False, "priority": "high",
            })
    elif breach["status"] == "unavailable":
        plan.append({
            "id": "retry-provider", "title": "Breach source unavailable",
            "description": "Run another scan later. No conclusion can be drawn while the breach provider is unavailable.",
            "critical": False, "priority": "informational",
        })
    if not plan:
        plan.append({
            "id": "security-hygiene", "title": "Maintain good security hygiene",
            "description": "Keep unique passwords, multi-factor authentication, and recovery details up to date.",
            "critical": False, "priority": "routine",
        })

    scanned_at = now_iso()
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO scan_history (
                user_id, scanned_at, security_score, risk_score, risk_level,
                breach_status, breach_count, discovery_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            current_user["id"], scanned_at, assessment["security_score"],
            assessment["risk_score"], assessment["risk_level"], breach["status"],
            breach["breaches"], discovery["status"],
        ))
        scan_id = cursor.lastrowid
        resolved = {
            row["action_id"]: bool(row["resolved"])
            for row in db.execute(
                "SELECT action_id, resolved FROM remediation_status WHERE user_id = ?",
                (current_user["id"],),
            ).fetchall()
        }

    for action in plan:
        action["resolved"] = resolved.get(action["id"], False)

    return {
        "status": "FULL_ANALYSIS_COMPLETE",
        "scan_id": scan_id,
        "scanned_at": scanned_at,
        "sources": [
            {"name": "XposedOrNot", "type": "external", "status": breach["status"]},
            {"name": "Holehe", "type": "external", "status": discovery["status"]},
            {"name": "DATAFENCE risk engine", "type": "local", "status": "complete"},
        ],
        "identity": {"id": current_user["id"], "name": current_user["name"], "email": target_email},
        "intelligence": result, "security": assessment, "breach_analysis": breach,
        "account_discovery": discovery, "active_registered_sites": discovery["sites"],
        "phone_metadata": phone, "remediation_plan": plan,
    }


@router.get("/history")
def scan_history(
    limit: int = Query(default=10, ge=1, le=50),
    current_user=Depends(get_current_user),
):
    with get_db() as db:
        rows = db.execute("""
            SELECT id, scanned_at, security_score, risk_score, risk_level,
                   breach_status, breach_count, discovery_status
            FROM scan_history WHERE user_id = ?
            ORDER BY scanned_at DESC LIMIT ?
        """, (current_user["id"], limit)).fetchall()
    return {"items": [dict(row) for row in rows], "count": len(rows)}


@router.put("/remediations/{action_id}")
def update_remediation(
    action_id: str,
    payload: RemediationUpdate,
    current_user=Depends(get_current_user),
):
    if not re.fullmatch(r"[a-z0-9-]{1,100}", action_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid remediation action")
    updated_at = now_iso()
    with get_db() as db:
        db.execute("""
            INSERT INTO remediation_status (user_id, action_id, resolved, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, action_id) DO UPDATE SET
                resolved = excluded.resolved, updated_at = excluded.updated_at
        """, (current_user["id"], action_id, int(payload.resolved), updated_at))
    return {"action_id": action_id, "resolved": payload.resolved, "updated_at": updated_at}
