import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.security import router as security_router


app = FastAPI(
    title="DATAFENCE",
    description=(
        "Personal Data Exposure, Inference "
        "& Adaptive Security Engine"
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,

    allow_origins=allowed_origins,

    allow_credentials=False,

    allow_methods=["GET", "POST", "OPTIONS"],

    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(
    auth_router
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
        "version": "1.0.0",
        "message": (
            "Personal Data Security "
            "Intelligence Platform"
        ),
    }


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "healthy"}
