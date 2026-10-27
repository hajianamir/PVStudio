"""Central API Router for PVStudio Platform."""

from fastapi import APIRouter
from app.api.endpoints import calc, mobile

api_router = APIRouter()
api_router.include_router(calc.router)
api_router.include_router(mobile.router)
