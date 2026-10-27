"""Unit and Integration Tests for Phase 4 Sprint 1 Deliverables.

Verifies:
1. Android Offline-First Mobile Field Sync with Auditable Per-Field Conflict Logging & Idempotency.
2. AI Copilot Design Error Detection Benchmark (10 parametrized seeded error cases).
3. Profile-Lock & Catalog-Lock Guardrails via direct validator function testing (Approach B).
"""

import pytest
from app.schemas.mobile import SyncBatchRequest, FieldInspectionRecord
from app.services.mobile_sync.service import MobileSyncService
from calc.ai_copilot.service import AICopilotInputSchema, audit_solar_design_copilot, validate_citation

def test_android_offline_mobile_sync_idempotency_and_conflict_logging():
    svc = MobileSyncService()

    # Batch 1: Initial offline sync
    rec1 = FieldInspectionRecord(
        record_id="rec_001",
        project_id="proj_solar_1",
        inspector_id="tech_john",
        timestamp_utc="2026-10-24T10:00:00Z",
        checklist_answers={"grounding_ok": True},
        insulation_resistance_mohm=600.0,
        scanned_barcodes=["SN1001", "SN1002"]
    )
    req1 = SyncBatchRequest(device_id="android_dev_1", sync_sequence_id="seq_001", records=[rec1])
    res1 = svc.process_sync_batch(req1)

    assert res1.status == "SUCCESS"
    assert res1.processed_count == 1

    # Batch 1 Re-transmission (Sequence Idempotency check)
    res1_retry = svc.process_sync_batch(req1)
    assert res1_retry.status == "SUCCESS"
    assert res1_retry.processed_count == 1

    # Batch 2: Conflict update (Technician B modifies checklist & insulation resistance)
    rec1_updated = FieldInspectionRecord(
        record_id="rec_001",
        project_id="proj_solar_1",
        inspector_id="tech_dave",
        timestamp_utc="2026-10-24T12:00:00Z",
        checklist_answers={"grounding_ok": False},  # Conflict: True vs False
        insulation_resistance_mohm=450.0,            # Conflict: 600M vs 450M
        scanned_barcodes=["SN1002", "SN1003"]        # Additive Merge
    )
    req2 = SyncBatchRequest(device_id="android_dev_1", sync_sequence_id="seq_002", records=[rec1_updated])
    res2 = svc.process_sync_batch(req2)

    assert res2.status == "CONFLICT_AUDITED"
    assert res2.processed_count == 1
    assert len(res2.conflict_log_entries) >= 2

    # Verifies Additive Barcode Merge (SN1001, SN1002, SN1003 all present)
    assert sorted(svc._db_store["rec_001"].scanned_barcodes) == ["SN1001", "SN1002", "SN1003"]

# 10 Seeded Solar Design Error Test Cases for AI Copilot Benchmark
AI_BENCHMARK_CASES = [
    # Case 1: Residential Voc Overlimit (680V > 600V)
    ("US-NEC-2020-v1", {"string_voc_max_v": 680.0, "system_class": "RESIDENTIAL"}, "ERR_DC_VOC_OVERLIMIT", "NEC Article 690.7"),
    # Case 2: C&I Voc Overlimit (1600V > 1500V)
    ("EU-DE-v1", {"string_voc_max_v": 1600.0, "system_class": "COMMERCIAL"}, "ERR_DC_VOC_OVERLIMIT", "IEC 62548 §6.2"),
    # Case 3: AC Voltage Drop > 3.0%
    ("US-NEC-2020-v1", {"ac_voltage_drop_percent": 3.8}, "ERR_AC_VOLTAGE_DROP_HIGH", "NEC Article 210.19(A) Informational Note No. 2"),
    # Case 4: Protection Short-Circuit Interrupting Rating Low
    ("US-NEC-2020-v1", {"fault_current_ka": 28.0, "breaker_interrupting_ka": 16.0}, "ERR_BREAKER_INTERRUPT_RATING_LOW", "IEEE 1547-2018 / IEC 60909"),
    # Case 5: Utility Substation Transformer Undersized
    ("EU-DE-v1", {"plant_capacity_kw": 50000.0, "transformer_mva": 40.0}, "ERR_TRANSFORMER_UNDERSIZED", "IEEE C57.12.00 / IEC 60076"),
    # Case 6: Financial DSCR Shortfall (< 1.20x)
    ("US-NEC-2020-v1", {"dscr_min_twenty_year": 1.12}, "ERR_FINANCIAL_DSCR_SHORTFALL", "calc/compliance/profiles/US-NEC-2020-v1.yaml §min_required_dscr"),
    # Case 7: MENA-GCC DSCR Shortfall (< 1.15x)
    ("MENA-GCC-v1", {"dscr_min_twenty_year": 1.08}, "ERR_FINANCIAL_DSCR_SHORTFALL", "calc/compliance/profiles/MENA-GCC-v1.yaml §min_required_dscr"),
    # Case 8: MENA-GCC High Temperature Grid Derating (> 45C)
    ("MENA-GCC-v1", {"max_ambient_temperature_c": 48.0}, "WARN_GCC_HIGH_TEMP_DERATING", "SEC Grid Code §4.2 / IEC 62548"),
    # Case 9: DC Voc Knife-Edge Thermal Risk (597V / 600V)
    ("US-NEC-2020-v1", {"string_voc_max_v": 597.0, "system_class": "RESIDENTIAL"}, "WARN_DC_VOC_KNIFE_EDGE", "NEC Article 690.7"),
    # Case 10: Multi-Error Case (720V Voc + 4.5% Vdrop)
    ("US-NEC-2020-v1", {"string_voc_max_v": 720.0, "ac_voltage_drop_percent": 4.5, "system_class": "RESIDENTIAL"}, "ERR_DC_VOC_OVERLIMIT", "NEC Article 690.7"),
]

@pytest.mark.parametrize("jurisdiction,params,expected_flag_id,expected_citation", AI_BENCHMARK_CASES)
def test_ai_copilot_seeded_error_case_benchmark(jurisdiction, params, expected_flag_id, expected_citation):
    inputs = AICopilotInputSchema(
        project_id="proj_ai_benchmark",
        jurisdiction=jurisdiction,
        design_params=params
    )
    res = audit_solar_design_copilot(inputs)
    flags = res.outputs["flags"]

    flag_map = {f["flag_id"]: f["standard_citation"] for f in flags}
    assert expected_flag_id in flag_map
    assert flag_map[expected_flag_id] == expected_citation

def test_citation_validator_deep_rejection_guardrail():
    # Direct Approach B Unit Test: Verifies validate_citation logic
    assert validate_citation("IEEE 99999-2050") == False
    assert validate_citation("NREL Project Finance Standard") == False
    assert validate_citation("Regional Project Finance Covenant") == False

    # Deep YAML file lookup verification
    assert validate_citation("calc/compliance/profiles/US-NEC-2020-v1.yaml §min_required_dscr") == True
    assert validate_citation("calc/compliance/profiles/MENA-GCC-v1.yaml §min_required_dscr") == True
    assert validate_citation("calc/compliance/profiles/US-NEC-2020-v1.yaml §nonexistent_key") == False
    assert validate_citation("calc/compliance/profiles/NON_EXISTENT_FILE.yaml §min_required_dscr") == False

def test_ai_copilot_transformer_tap_mismatch_warning():
    inputs = AICopilotInputSchema(
        project_id="proj_tap_test",
        jurisdiction="US-NEC-2020-v1",
        design_params={"grid_nominal_kv": 110.0, "actual_grid_kv": 115.0, "transformer_tap_percent": 0.0}
    )
    res = audit_solar_design_copilot(inputs)
    flags = res.outputs["flags"]
    flag_ids = [f["flag_id"] for f in flags]

    assert "WARN_TRANSFORMER_TAP_MISMATCH" in flag_ids
