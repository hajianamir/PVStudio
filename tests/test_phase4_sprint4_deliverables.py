"""Unit and Integration Tests for Phase 4 Sprint 4 Deliverables.

Verifies:
1. Expanded 20-Case Seeded Solar Design Error Benchmark for AI Copilot.
2. Webhook Event Delivery against mock CRM/ERP/BIM listener endpoints.
3. Android Mobile Field Sync End-to-End Round-Trip Integration.
"""

import pytest
from app.schemas.mobile import SyncBatchRequest, FieldInspectionRecord
from app.services.mobile_sync.service import MobileSyncService
from app.schemas.webhook import WebhookSubscriptionRequest
from app.services.webhook_service import WebhookService
from calc.ai_copilot.service import AICopilotInputSchema, audit_solar_design_copilot

# 20 Seeded Error Cases for AI Copilot Benchmark
AI_BENCHMARK_20_CASES = [
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
    # Case 11: Transformer Tap Changer Mismatch
    ("US-NEC-2020-v1", {"grid_nominal_kv": 110.0, "actual_grid_kv": 115.0, "transformer_tap_percent": 0.0}, "WARN_TRANSFORMER_TAP_MISMATCH", "IEEE C57.131 / IEEE C57.12.00"),
    # Case 12: Rapid Shutdown Missing
    ("US-NEC-2020-v1", {"system_class": "RESIDENTIAL", "has_rapid_shutdown": False}, "ERR_RAPID_SHUTDOWN_MISSING", "NEC Article 690.12"),
    # Case 13: Equipment Grounding Conductor Undersize
    ("US-NEC-2020-v1", {"ocpd_rating_a": 60, "egc_awg": 12}, "ERR_EGC_CONDUCTOR_UNDERSIZED", "NEC Article 250.122"),
    # Case 14: Relay Protection Coordination Delay Margin Low
    ("US-NEC-2020-v1", {"relay_primary_time_sec": 0.10, "relay_backup_time_sec": 0.20}, "WARN_RELAY_COORDINATION_MARGIN_LOW", "IEEE C37.113"),
    # Case 15: C&I Substation Busbar Differential Trip Time Margin High
    ("EU-DE-v1", {"busbar_fault_current_ka": 35.0, "breaker_interrupting_ka": 25.0}, "ERR_BREAKER_INTERRUPT_RATING_LOW", "IEEE 1547-2018 / IEC 60909"),
    # Case 16: MENA-GCC Transformer MVA Undersize
    ("MENA-GCC-v1", {"plant_capacity_kw": 100000.0, "transformer_mva": 80.0}, "ERR_TRANSFORMER_UNDERSIZED", "IEEE C57.12.00 / IEC 60076"),
    # Case 17: Residential Voltage Drop Overlimit
    ("US-NEC-2020-v1", {"ac_voltage_drop_percent": 4.8, "system_class": "RESIDENTIAL"}, "ERR_AC_VOLTAGE_DROP_HIGH", "NEC Article 210.19(A) Informational Note No. 2"),
    # Case 18: Commercial High Temperature Voc Derating
    ("MENA-GCC-v1", {"string_voc_max_v": 1580.0, "system_class": "COMMERCIAL"}, "ERR_DC_VOC_OVERLIMIT", "IEC 62548 §6.2"),
    # Case 19: High Fault Current Protection Mismatch
    ("EU-DE-v1", {"fault_current_ka": 42.0, "breaker_interrupting_ka": 31.5}, "ERR_BREAKER_INTERRUPT_RATING_LOW", "IEEE 1547-2018 / IEC 60909"),
    # Case 20: Multi-Error DSCR + Voc Overlimit
    ("US-NEC-2020-v1", {"string_voc_max_v": 650.0, "dscr_min_twenty_year": 1.05, "system_class": "RESIDENTIAL"}, "ERR_DC_VOC_OVERLIMIT", "NEC Article 690.7"),
]

@pytest.mark.parametrize("jurisdiction,params,expected_flag_id,expected_citation", AI_BENCHMARK_20_CASES)
def test_ai_copilot_expanded_20_case_seeded_error_benchmark(jurisdiction, params, expected_flag_id, expected_citation):
    inputs = AICopilotInputSchema(
        project_id="proj_ai_sprint4",
        jurisdiction=jurisdiction,
        design_params=params
    )
    res = audit_solar_design_copilot(inputs)
    flags = res.outputs["flags"]

    flag_map = {f["flag_id"]: f["standard_citation"] for f in flags}
    assert expected_flag_id in flag_map
    assert flag_map[expected_flag_id] == expected_citation

def test_webhook_end_to_end_crm_dispatch():
    svc = WebhookService()
    sub_crm = WebhookSubscriptionRequest(
        subscription_id="sub_crm_01",
        client_name="Salesforce CRM",
        target_url="https://crm.solar.com/webhook",
        subscribed_events=["PROJECT_APPROVED"],
        secret_key="crm_secret_123"
    )
    svc.register_subscription(sub_crm)
    events = svc.dispatch_event("PROJECT_APPROVED", "proj_1001", {"status": "APPROVED"})
    assert len(events) == 1
    assert len(events[0].hmac_signature) == 64

def test_webhook_end_to_end_erp_dispatch():
    svc = WebhookService()
    sub_erp = WebhookSubscriptionRequest(
        subscription_id="sub_erp_01",
        client_name="SAP ERP",
        target_url="https://erp.solar.com/webhook",
        subscribed_events=["INSPECTION_COMPLETED"],
        secret_key="erp_secret_456"
    )
    svc.register_subscription(sub_erp)
    events = svc.dispatch_event("INSPECTION_COMPLETED", "proj_1001", {"inspector": "tech_john"})
    assert len(events) == 1
    assert len(events[0].hmac_signature) == 64

def test_webhook_end_to_end_bim_dispatch():
    svc = WebhookService()
    sub_bim = WebhookSubscriptionRequest(
        subscription_id="sub_bim_01",
        client_name="Autodesk BIM",
        target_url="https://bim.solar.com/webhook",
        subscribed_events=["BANKABILITY_REPORT_GENERATED"],
        secret_key="bim_secret_789"
    )
    svc.register_subscription(sub_bim)
    events = svc.dispatch_event("BANKABILITY_REPORT_GENERATED", "proj_1001", {"dscr_min": 1.22})
    assert len(events) == 1
    assert len(events[0].hmac_signature) == 64

def test_android_mobile_field_sync_end_to_end_round_trip():
    svc = MobileSyncService()

    # Capture Record on Android device
    rec = FieldInspectionRecord(
        record_id="rec_round_trip_01",
        project_id="proj_round_trip",
        inspector_id="tech_round_trip",
        timestamp_utc="2026-10-24T14:00:00Z",
        checklist_answers={"visual_inspection_ok": True},
        insulation_resistance_mohm=550.0,
        scanned_barcodes=["SN_PANEL_001"]
    )
    batch_req = SyncBatchRequest(device_id="android_tab_01", sync_sequence_id="batch_s4_01", records=[rec])

    # Process Sync
    res = svc.process_sync_batch(batch_req)
    assert res.status == "SUCCESS"
    assert res.processed_count == 1

    # Verify Cloud DB Store Update
    stored_rec = svc._db_store["rec_round_trip_01"]
    assert stored_rec.checklist_answers["visual_inspection_ok"] == True
    assert stored_rec.insulation_resistance_mohm == 550.0
    assert "SN_PANEL_001" in stored_rec.scanned_barcodes
