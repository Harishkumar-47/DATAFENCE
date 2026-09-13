from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.analysis import router as analysis_router
from app.api.security import router as security_router


app = FastAPI(
    title="DATAFENCE",
    description=(
        "Personal Data Exposure, Inference "
        "& Adaptive Security Engine"
    ),
    version="0.4.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(
    auth_router
)

app.include_router(
    analysis_router
)

app.include_router(
    security_router
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": "DATAFENCE",
        "status": "online",
        "version": "0.4.0",
        "message": (
            "Personal Data Security "
            "Intelligence Platform"
        ),
    }