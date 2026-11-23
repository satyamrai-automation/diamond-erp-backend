from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api_router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise REST API for Diamond Manufacturing, Cutting, Polishing, Tracking, 4Cs QC, and Sales ERP.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration: allow credentials with origin matching
cors_origins = [o for o in settings.ALLOWED_ORIGINS if o != "*"]
has_wildcard = "*" in settings.ALLOWED_ORIGINS

if has_wildcard:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^https?://.*$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["System Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "api_version": "v1"
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Diamond Manufacturing & ERP API",
        "docs": "/docs",
        "health": "/health"
    }
