from fastapi import APIRouter
from app.api.v1.endpoints import auth, diamonds, manufacturing, dashboard

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Profile"])
api_router.include_router(diamonds.router, prefix="/diamonds", tags=["Diamond Inventory & Split Genealogy"])
api_router.include_router(manufacturing.router, prefix="/manufacturing", tags=["Manufacturing & Production Tracking"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["CTO & Admin Dashboard Analytics"])
