from fastapi import (
    APIRouter,
    Depends,
)
from pydantic import BaseModel

import requests

from app.api.auth import get_current_user

from app.engines.intelligence.intelligence_pipeline import (
    IntelligencePipeline,
)

from app.engines.security.security_engine import (
    SecurityEngine,
)

router = APIRouter(
    prefix="/api/security",
    tags=["DATAFENCE Security"],
)

intelligence = IntelligencePipeline()
security_engine = SecurityEngine()


class SecurityAnalysisRequest(BaseModel):
    email: str = ""
    phone: str = ""


# ============================================================
# XPOSEDORNOT BREACH ANALYSIS
# ============================================================

def check_xposedornot(email: str):
    if not email:
        return {
            "available": False,
            "risk_score": 0,
            "risk_level": "Unknown",
            "breaches": 0,
        }

    url = f"https://api.xposedornot.com/v1/check-email/{email}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return {
                "available": True,
                "risk_score": 0,
                "risk_level": "Low",
                "breaches": 0,
                "breach_sites": []
            }

        data = response.json()
        
        breach_sites = []
        breaches_array = data.get("breaches", [])
        if breaches_array and isinstance(breaches_array, list):
            if len(breaches_array) > 0 and isinstance(breaches_array[0], list):
                breach_sites = breaches_array[0]
            else:
                breach_sites = breaches_array

        return {
            "available": True,
            "risk_score": min(len(breach_sites) * 15, 100),
            "risk_level": "High" if len(breach_sites) > 3 else "Medium" if len(breach_sites) > 0 else "Low",
            "breaches": len(breach_sites),
            "breach_sites": breach_sites
        }

        return {
            "available": True,
            "risk_score": 0,
            "risk_level": "Low",
            "breaches": len(breach_sites),
            "breach_sites": breach_sites
        }

    except Exception:

        return {
            "available": False,
            "risk_score": 0,
            "risk_level": "Unknown",
            "breaches": 0,
            "breach_sites": []
        }

import phonenumbers
from phonenumbers import geocoder, carrier

# ============================================================
# FULL SECURITY ANALYSIS
# ============================================================

@router.post("/full-analysis")
def full_analysis(
    request: SecurityAnalysisRequest,
    current_user=Depends(
        get_current_user
    ),
):
    target_email = request.email.strip() if request.email else current_user["email"]
    target_phone = request.phone.strip()

    # ========================================================
    # USER-SPECIFIC DATA MODEL
    # ========================================================
    
    data_points = []
    connections = []
    phone_info = {}

    if target_email:
        data_points.append({"type": "email", "value": target_email})
        connections.append({"type": "email"})
        connections.append({"type": "documents"})
        
    if target_phone:
        data_points.append({"type": "phone", "value": target_phone})
        connections.append({"type": "contacts"})
        
        # Live Phone Number Analysis
        try:
            parsed_phone = phonenumbers.parse(target_phone, None)
            if phonenumbers.is_valid_number(parsed_phone):
                region = geocoder.description_for_number(parsed_phone, "en")
                provider = carrier.name_for_number(parsed_phone, "en")
                if region:
                    data_points.append({"type": "location", "value": region})
                    phone_info["region"] = region
                if provider:
                    phone_info["carrier"] = provider
        except Exception:
            pass
        
    # Always add some base inferences based on standard exposure
    if not phone_info.get("region"):
        data_points.extend([{"type": "location"}])
    data_points.extend([{"type": "activity"}])

    sample_data = {
        "identity": {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
        },
        "data_points": data_points,
        "connections": connections,
    }

    # ========================================================
    # INTELLIGENCE PIPELINE
    # ========================================================

    intelligence_result = intelligence.analyze(
        sample_data
    )
    
    # Inject live phone intelligence findings
    if phone_info:
        desc = []
        if "region" in phone_info: desc.append(f"Located in {phone_info['region']}")
        if "carrier" in phone_info: desc.append(f"using {phone_info['carrier']}")
        
        if desc:
            intelligence_result["inference"]["findings"].insert(0, {
                "inference": "Probable Location & Carrier identified: " + " ".join(desc),
                "severity": "HIGH",
                "source_categories": ["Phone Number"]
            })
            intelligence_result["inference"]["score"] = min(100, intelligence_result["inference"]["score"] + 25)

    # ========================================================
    # XPOSEDORNOT BREACH ANALYSIS
    # ========================================================

    breach_result = check_xposedornot(target_email)

    # ========================================================
    # SECURITY ASSESSMENT
    # ========================================================

    assessment = security_engine.assess(

        exposure_score=max(
            intelligence_result[
                "exposure"
            ]["score"],
            breach_result[
                "risk_score"
            ],
        ),

        inference_score=(
            intelligence_result[
                "inference"
            ]["score"]
        ),

        threat_score=(
            intelligence_result[
                "threat"
            ]["score"]
        ),

        blast_radius=(
            intelligence_result[
                "blast_radius"
            ]["score"]
        ),
    )

    # ========================================================
    # REMEDIATION PLAN
    # ========================================================
    
    remediation_plan = []
    if breach_result.get("available") and breach_result.get("breaches", 0) > 0:
        sites_str = ", ".join(breach_result.get("breach_sites", []))
        site_mention = f" ({sites_str})" if sites_str else ""
        remediation_plan.append({
            "title": "Rotate Compromised Passwords",
            "description": f"Your email was found in {breach_result['breaches']} breaches{site_mention}. Immediately change your passwords for these accounts and enable 2FA.",
            "critical": True
        })
    if phone_info.get("region"):
        remediation_plan.append({
            "title": "Limit Phone Number Exposure",
            "description": f"Your phone number reveals your carrier ({phone_info.get('carrier', 'Unknown')}) and region ({phone_info['region']}). Consider using a VoIP number for public registrations.",
            "critical": False
        })
    
    if assessment["risk_level"] in ["HIGH", "CRITICAL"]:
        remediation_plan.append({
            "title": "Secure Connected Services",
            "description": "Your digital blast radius is wide. Revoke OAuth permissions for unused applications and audit your privacy settings.",
            "critical": True
        })

    # Add default if empty
    if not remediation_plan:
        remediation_plan.append({
            "title": "Maintain Good Security Hygiene",
            "description": "Keep your software updated and continue using strong, unique passwords for all accounts.",
            "critical": False
        })

    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "status": "FULL_ANALYSIS_COMPLETE",

        "identity": {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
        },

        "intelligence": intelligence_result,

        "security": assessment,

        "breach_analysis": breach_result,
        
        "remediation_plan": remediation_plan

    }
        
