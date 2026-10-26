"""Unit and Integration Tests for Phase 4 Sprint 1 Deliverables.

Verifies:
1. Android Offline-First Mobile Field Sync with LWW conflict resolution and sequence idempotency.
2. AI Copilot Design Error Detection Benchmark (100% citation compliance & 100% seeded error detection).
"""

import pytest
from app.schemas.mobile import SyncBatchRequest, FieldInspectionRecord
from app.services.mobile_sync.service import MobileSyncService
from calc.ai_copilot.service import AICopilotInputSchema, audit_solar_design_copilot

def test_android_offline_mobile_sync_idempotency_and_lww():
    svc = MobileSyncService()

    # Batch 1: Initial offline sync
    rec1 = FieldInspectionRecord(
        record_id="rec_001",
        project_id="proj_solar_1",
        inspector_id="tech_john",
        timestamp_utc="2026-10-24T10:00:00Z",
        checklist_answers={"grounding_ok": True},
        insulation_resistance_mohm=600.0
    )
    req1 = SyncBatchRequest(device_id="android_dev_1", sync_sequence_id="seq_001", records=[rec1])
    res1 = svc.process_sync_batch(req1)

    assert res1.status == "SUCCESS"
    assert res1.processed_count == 1

    # Batch 1 Re-transmission (Idempotency check)
    res1_retry = svc.process_sync_batch(req1)
    assert res1_retry.status == "SUCCESS"
    assert res1_retry.processed_count == 1

    # Batch 2: LWW Update (newer timestamp)
    rec1_updated = FieldInspectionRecord(
        record_id="rec_001",
        project_id="proj_solar_1",
        inspector_id="tech_john",
        timestamp_utc="2026-10-24T12:00:00Z",
        checklist_answers={"grounding_ok": True, "labels_ok": True},
        insulation_resistance_mohm=650.0
    )
    req2 = SyncBatchRequest(device_id="android_dev_1", sync_sequence_id="seq_002", records=[rec1_updated])
    res2 = svc.process_sync_batch(req2)

    assert res2.status == "SUCCESS"
    assert res2.processed_count == 1
    assert svc._db_store["rec_001"].insulation_resistance_mohm == 650.0

def test_ai_copilot_seeded_error_detection_and_100pct_citations():
    # Seeded Solar Design Errors Case
    params_with_errors = {
        "string_voc_max_v": 720.0,            # Error 1: Exceeds 600V residential max
        "system_class": "RESIDENTIAL",
        "ac_voltage_drop_percent": 4.2,       # Error 2: Exceeds 3.0% threshold
        "fault_current_ka": 32.0,             # Error 3: Exceeds 16kA breaker rating
        "breaker_interrupting_ka": 16.0
    }

    inputs = AICopilotInputSchema(
        project_id="proj_ai_test",
        jurisdiction="US-NEC-2020",
        design_params=params_with_errors
    )

    res = audit_solar_design_copilot(inputs)
    outputs = res.outputs

    # Verifies >= 80% error detection accuracy (3 of 3 seeded errors detected = 100%)
    assert outputs["total_flags"] == 3
    assert outputs["error_count"] == 3

    # Verifies 100% standard citation compliance (every flag has non-empty citation)
    assert outputs["citation_compliance_percent"] == 100.0

    flag_citations = [f["standard_citation"] for f in outputs["flags"]]
    assert "NEC Article 690.7" in flag_citations
    assert "NEC Article 210.19(A) Informational Note No. 2" in flag_citations
    assert "IEEE 1547-2018 / IEC 60909" in flag_citations
