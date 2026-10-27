"""Unit and Integration Tests for Phase 4 Sprint 2 Deliverables.

Verifies:
1. User-Facing Conflict Resolution UI Handler (`resolve_user_conflict`).
2. Dual-Measurement Preservation Model for IV Curve and Insulation Resistance (Zero Data Overwrite).
3. Deep YAML Profile Key Validation in `validate_citation`.
"""

import pytest
from app.schemas.mobile import SyncBatchRequest, FieldInspectionRecord, ConflictResolutionRequest
from app.services.mobile_sync.service import MobileSyncService
from calc.ai_copilot.service import validate_citation

def test_user_facing_conflict_resolution_and_dual_measurement_preservation():
    svc = MobileSyncService()

    # Technician A syncs Record
    rec_a = FieldInspectionRecord(
        record_id="rec_field_100",
        project_id="proj_utility_solar",
        inspector_id="tech_alice",
        timestamp_utc="2026-10-24T08:00:00Z",
        checklist_answers={"grounding_bonding_ok": True},
        insulation_resistance_mohm=600.0,
        iv_curve_measurements=[{"v": 100.0, "i": 8.5}]
    )
    res_a = svc.process_sync_batch(SyncBatchRequest(device_id="dev_a", sync_sequence_id="seq_a1", records=[rec_a]))
    assert res_a.status == "SUCCESS"

    # Technician B syncs conflicting checklist answer & differing measurements
    rec_b = FieldInspectionRecord(
        record_id="rec_field_100",
        project_id="proj_utility_solar",
        inspector_id="tech_bob",
        timestamp_utc="2026-10-24T08:30:00Z",
        checklist_answers={"grounding_bonding_ok": False},  # Conflict
        insulation_resistance_mohm=420.0,                   # Measurement difference
        iv_curve_measurements=[{"v": 100.0, "i": 6.2}]       # Measurement difference
    )
    res_b = svc.process_sync_batch(SyncBatchRequest(device_id="dev_b", sync_sequence_id="seq_b1", records=[rec_b]))

    assert res_b.status == "CONFLICT_PENDING_RESOLUTION"
    assert len(res_b.conflict_log_entries) == 1
    assert len(res_b.dual_measurement_records) == 2

    # Verifies Dual-Measurement Preservation (BOTH readings preserved with technician provenance & review flags)
    dual_recs = svc._db_store["rec_field_100"].dual_measurements
    assert len(dual_recs) == 2
    types = [d.parameter_type for d in dual_recs]
    assert "INSULATION_RESISTANCE" in types
    assert "IV_CURVE" in types
    assert all(d.requires_engineer_review for d in dual_recs)

    # Technician B resolves checklist conflict via User-Facing Resolution Dialog
    conflict_id = res_b.conflict_log_entries[0].conflict_id
    res_req = ConflictResolutionRequest(
        conflict_id=conflict_id,
        chosen_value=True,
        resolved_by="lead_eng_dave",
        resolution_notes="Grounding verified via digital micro-ohmmeter secondary check."
    )
    resolved_entry = svc.resolve_user_conflict(res_req)
    assert resolved_entry.resolution_status == "RESOLVED"
    assert svc._db_store["rec_field_100"].checklist_answers["grounding_bonding_ok"] == True

def test_validate_citation_deep_yaml_key_lookup():
    # Direct Approach B Unit Assertions
    assert validate_citation("IEEE 99999-2050") == False
    assert validate_citation("NREL Project Finance Standard") == False
    assert validate_citation("calc/compliance/profiles/FAKE.yaml §min_required_dscr") == False

    # Deep YAML file lookup verification
    assert validate_citation("calc/compliance/profiles/US-NEC-2020-v1.yaml §min_required_dscr") == True
    assert validate_citation("calc/compliance/profiles/MENA-GCC-v1.yaml §min_required_dscr") == True
    assert validate_citation("calc/compliance/profiles/US-NEC-2020-v1.yaml §nonexistent_key") == False
