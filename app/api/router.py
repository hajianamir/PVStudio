"""
PVStudio API Router Definitions
"""

from fastapi import APIRouter
from app.api.endpoints import calc

api_router = APIRouter()
api_router.include_router(calc.router, prefix="/calc", tags=["Calculations"])
