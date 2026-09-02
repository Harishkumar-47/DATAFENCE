from fastapi import (
    APIRouter,
    Depends,
)

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


# ============================================================
# FULL SECURITY ANALYSIS
# ============================================================

@router.post("/full-analysis")
def full_analysis(
    current_user=Depends(
        get_current_user
    ),
):

    # ========================================================
    # USER-SPECIFIC DATA MODEL
    # ========================================================

    sample_data = {

        "identity": {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
        },

        "data_points": [

            {
                "type": "email",
            },

            {
                "type": "location",
            },

            {
                "type": "activity",
            },

            {
                "type": "purchases",
            },

            {
                "type": "contacts",
            },
        ],

        "connections": [

            {
                "type": "email",
            },

            {
                "type": "contacts",
            },

            {
                "type": "documents",
            },
        ],
    }

    # ========================================================
    # INTELLIGENCE PIPELINE
    # ========================================================

    intelligence_result = intelligence.analyze(
        sample_data
    )

    # ========================================================
    # SECURITY ASSESSMENT
    # ========================================================

    assessment = security_engine.assess(

        exposure_score=(
            intelligence_result[
                "exposure"
            ]["score"]
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
    }