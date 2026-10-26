"""Schemas for Android Offline-First Mobile Field Operations & Sync Service."""

import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class FieldInspectionRecord(BaseModel):
    record_id: str = Field(..., description="Unique client UUID generated on Android")
    project_id: str = Field(..., description="Target solar project ID")
    inspector_id: str = Field(..., description="User ID of field technician")
    timestamp_utc: str = Field(..., description="ISO 8601 timestamp recorded offline")
    checklist_answers: Dict[str, bool] = Field(default_factory=dict, description="Checklist item responses")
    iv_curve_measurements: List[Dict[str, float]] = Field(default_factory=list, description="Array of V, I measurement points")
    insulation_resistance_mohm: float = Field(default=500.0, description="Measured insulation resistance in M-ohms")
    scanned_barcodes: List[str] = Field(default_factory=list, description="Scanned panel/inverter serial numbers")
    annotated_photo_urls: List[str] = Field(default_factory=list, description="URLs or local paths of annotated site photos")

class SyncBatchRequest(BaseModel):
    device_id: str = Field(..., description="Android device ID")
    sync_sequence_id: str = Field(..., description="Idempotent client transaction batch ID")
    records: List[FieldInspectionRecord] = Field(default_factory=list, description="Batch of records captured offline")

class SyncBatchResponse(BaseModel):
    sync_sequence_id: str
    status: str = "SUCCESS"  # SUCCESS, CONFLICT_RESOLVED, ERROR
    processed_count: int
    rejected_records: List[str] = Field(default_factory=list)
    server_timestamp_utc: str
