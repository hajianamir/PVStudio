"""
PVStudio FastAPI Core Application Entrypoint
"""

from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="PVStudio API",
    description="Integrated Solar Design, EPC, Grid & Bankability Platform API",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health/liveness")
def liveness():
    return {"status": "ok"}


@app.get("/health/readiness")
def readiness():
    return {"status": "ready"}
