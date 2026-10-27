"""Schemas for Android Offline-First Mobile Field Operations, Conflict Resolution UI & Dual-Measurement Preservation."""

import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ConflictLogEntry(BaseModel):
    conflict_id: str = Field(..., description="Unique conflict log UUID")
    record_id: str = Field(..., description="Target record ID where conflict occurred")
    field_name: str = Field(..., description="Specific field name in conflict")
    existing_value: Any = Field(..., description="Existing server value")
    incoming_value: Any = Field(..., description="Incoming client value")
    existing_updated_by: str
    existing_updated_at: str
    incoming_updated_by: str
    incoming_updated_at: str
    resolution_status: str = "PENDING_HUMAN_RESOLUTION"  # PENDING_HUMAN_RESOLUTION, RESOLVED_EXISTING, RESOLVED_INCOMING
    requires_engineer_review: bool = False

class DualMeasurementRecord(BaseModel):
    measurement_id: str
    record_id: str
    parameter_type: str  # IV_CURVE, INSULATION_RESISTANCE
    reading_a: Dict[str, Any]
    reading_b: Dict[str, Any]
    timestamp_a: str
    timestamp_b: str
    technician_a: str
    technician_b: str
    requires_engineer_review: bool = True

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
    dual_measurements: List[DualMeasurementRecord] = Field(default_factory=list, description="Preserved dual measurements awaiting O&M engineer review")

class SyncBatchRequest(BaseModel):
    device_id: str = Field(..., description="Android device ID")
    sync_sequence_id: str = Field(..., description="Idempotent client transaction batch ID")
    records: List[FieldInspectionRecord] = Field(default_factory=list, description="Batch of records captured offline")

class SyncBatchResponse(BaseModel):
    sync_sequence_id: str
    status: str = "SUCCESS"  # SUCCESS, CONFLICT_PENDING_RESOLUTION, ERROR
    processed_count: int
    conflict_log_entries: List[ConflictLogEntry] = Field(default_factory=list)
    dual_measurement_records: List[DualMeasurementRecord] = Field(default_factory=list)
    server_timestamp_utc: str

class ConflictResolutionRequest(BaseModel):
    conflict_id: str
    chosen_value: Any
    resolved_by: str
    resolution_notes: str
