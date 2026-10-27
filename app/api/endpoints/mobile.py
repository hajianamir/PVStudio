"""API Router Endpoints for Android Mobile Field Sync & Conflict Resolution UI."""

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.mobile import SyncBatchRequest, SyncBatchResponse, ConflictResolutionRequest, ConflictLogEntry
from app.services.mobile_sync.service import MobileSyncService

router = APIRouter(prefix="/mobile", tags=["mobile_field"])
sync_service = MobileSyncService()

@router.post("/sync", response_model=SyncBatchResponse)
def sync_offline_batch(batch: SyncBatchRequest):
    """Idempotent sync endpoint for Android offline-first field inspections."""
    return sync_service.process_sync_batch(batch)

@router.post("/resolve-conflict", response_model=ConflictLogEntry)
def resolve_field_conflict(req: ConflictResolutionRequest):
    """User-facing resolution endpoint for resolving checklist field conflicts."""
    try:
        return sync_service.resolve_user_conflict(req)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
