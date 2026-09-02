from fastapi import (
    APIRouter,
    Depends,
)

from app.api.auth import get_current_user

from app.engines.data.data_discovery import (
    DataDiscoveryEngine,
)

from app.engines.data.data_exposure import (
    DataExposureEngine,
)

from app.engines.inference.inference_engine import (
    InferenceEngine,
)

from app.engines.inference.profile_reconstructor import (
    ProfileReconstructor,
)

from app.engines.threat.threat_engine import (
    ThreatEngine,
)


router = APIRouter(
    prefix="/api/analysis",
    tags=["DATAFENCE Analysis"],
)


# ============================================================
# RUN ANALYSIS
# ============================================================

@router.post("/run")
def run_analysis(
    current_user=Depends(
        get_current_user
    ),
):

    email = current_user["email"]

    # ========================================================
    # DEMO DATA RECONSTRUCTION
    # ========================================================

    demo_data = [

        {
            "category": "identity",
            "value": "User Identity",
            "source": "Account",
        },

        {
            "category": "email",
            "value": email,
            "source": "Gmail",
        },

        {
            "category": "location",
            "value": "Chennai",
            "source": "Location History",
        },

        {
            "category": "search",
            "value": "Technology products",
            "source": "Search Activity",
        },

        {
            "category": "purchase",
            "value": "Online purchases",
            "source": "Shopping Activity",
        },

        {
            "category": "contacts",
            "value": "Contact network",
            "source": "Contacts",
        },
    ]

    # ========================================================
    # INITIALIZE ENGINES
    # ========================================================

    discovery = DataDiscoveryEngine()

    exposure = DataExposureEngine()

    inference = InferenceEngine()

    reconstructor = ProfileReconstructor()

    threat = ThreatEngine()

    # ========================================================
    # DATA DISCOVERY
    # ========================================================

    discovered = discovery.analyze(
        demo_data
    )

    # ========================================================
    # EXPOSURE
    # ========================================================

    exposure_score = exposure.calculate(
        discovered
    )

    # ========================================================
    # INFERENCE
    # ========================================================

    inferences = inference.analyze(
        discovered
    )

    # ========================================================
    # PROFILE
    # ========================================================

    profile = reconstructor.reconstruct(
        inferences
    )

    # ========================================================
    # THREATS
    # ========================================================

    threats = threat.analyze(
        exposure_score,
        inferences,
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "status": "ANALYSIS_COMPLETE",

        "identity": {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
        },

        "data": discovered,

        "exposure_score": exposure_score,

        "inferences": inferences,

        "reconstructed_profile": profile,

        "threats": threats,
    }