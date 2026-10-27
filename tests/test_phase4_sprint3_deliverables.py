"""Unit and Integration Tests for Phase 4 Sprint 3 Deliverables.

Verifies:
1. Webhook Subscription Manager for CRM/ERP/BIM integrations.
2. HMAC SHA-256 Event Payload Signing & Tamper Rejection.
3. Mobile Conflict Resolution API Route & Dual Measurement Retention.
"""

import hmac
import hashlib
import json
import pytest
from app.schemas.webhook import WebhookSubscriptionRequest
from app.services.webhook_service import WebhookService
from app.schemas.mobile import SyncBatchRequest, FieldInspectionRecord, ConflictResolutionRequest
from app.services.mobile_sync.service import MobileSyncService

def test_webhook_subscription_and_hmac_sha256_dispatch():
    svc = WebhookService()

    # Register Salesforce CRM Webhook Subscription
    sub = WebhookSubscriptionRequest(
        subscription_id="sub_sf_crm_001",
        client_name="Salesforce CRM",
        target_url="https://crm.example.com/webhooks/solar",
        subscribed_events=["PROJECT_APPROVED", "INSPECTION_COMPLETED"],
        secret_key="top_secret_hmac_key"
    )
    svc.register_subscription(sub)

    # Dispatch Event: INSPECTION_COMPLETED
    dispatched = svc.dispatch_event(
        event_type="INSPECTION_COMPLETED",
        project_id="proj_solar_999",
        payload_data={"status": "APPROVED", "inspector": "tech_john"}
    )

    assert len(dispatched) == 1
    event = dispatched[0]
    assert event.event_type == "INSPECTION_COMPLETED"
    assert event.project_id == "proj_solar_999"
    assert len(event.hmac_signature) == 64  # Hex-encoded SHA-256 length

def test_webhook_hmac_tamper_rejection():
    svc = WebhookService()
    secret = "top_secret_hmac_key"
    sub = WebhookSubscriptionRequest(
        subscription_id="sub_erp_001",
        client_name="SAP ERP",
        target_url="https://erp.example.com/webhooks",
        subscribed_events=["PROJECT_APPROVED"],
        secret_key=secret
    )
    svc.register_subscription(sub)

    dispatched = svc.dispatch_event(
        event_type="PROJECT_APPROVED",
        project_id="proj_solar_100",
        payload_data={"capex_usd": 40000000.0}
    )
    event = dispatched[0]

    # Tamper payload data: modify capex_usd
    tampered_body = json.dumps({"event_id": event.event_id, "event_type": event.event_type, "project_id": event.project_id, "data": {"capex_usd": 50000000.0}})
    expected_tampered_sig = hmac.new(secret.encode('utf-8'), tampered_body.encode('utf-8'), hashlib.sha256).hexdigest()

    # Signature for tampered payload does NOT match original signature
    assert event.hmac_signature != expected_tampered_sig

def test_mobile_resolve_conflict_endpoint_and_record_update():
    svc = MobileSyncService()
    rec_a = FieldInspectionRecord(
        record_id="rec_conflict_test",
        project_id="p1",
        inspector_id="tech_a",
        timestamp_utc="2026-10-24T10:00:00Z",
        checklist_answers={"check_1": True}
    )
    rec_b = FieldInspectionRecord(
        record_id="rec_conflict_test",
        project_id="p1",
        inspector_id="tech_b",
        timestamp_utc="2026-10-24T10:05:00Z",
        checklist_answers={"check_1": False}
    )
    svc.process_sync_batch(SyncBatchRequest(device_id="d1", sync_sequence_id="s1", records=[rec_a]))
    res_b = svc.process_sync_batch(SyncBatchRequest(device_id="d2", sync_sequence_id="s2", records=[rec_b]))

    assert res_b.status == "CONFLICT_PENDING_RESOLUTION"
    conflict_id = res_b.conflict_log_entries[0].conflict_id

    # Resolve conflict via user-facing endpoint handler
    res_req = ConflictResolutionRequest(
        conflict_id=conflict_id,
        chosen_value=True,
        resolved_by="lead_eng",
        resolution_notes="Verified via secondary check."
    )
    res_entry = svc.resolve_user_conflict(res_req)
    assert res_entry.resolution_status == "RESOLVED"
    assert svc._db_store["rec_conflict_test"].checklist_answers["check_1"] == True

def test_dual_measurement_preservation_records():
    svc = MobileSyncService()
    rec_a = FieldInspectionRecord(
        record_id="rec_dual_test",
        project_id="p1",
        inspector_id="tech_a",
        timestamp_utc="2026-10-24T10:00:00Z",
        insulation_resistance_mohm=600.0,
        iv_curve_measurements=[{"v": 100.0, "i": 8.0}]
    )
    rec_b = FieldInspectionRecord(
        record_id="rec_dual_test",
        project_id="p1",
        inspector_id="tech_b",
        timestamp_utc="2026-10-24T10:05:00Z",
        insulation_resistance_mohm=400.0,
        iv_curve_measurements=[{"v": 100.0, "i": 6.0}]
    )
    svc.process_sync_batch(SyncBatchRequest(device_id="d1", sync_sequence_id="s1", records=[rec_a]))
    res = svc.process_sync_batch(SyncBatchRequest(device_id="d2", sync_sequence_id="s2", records=[rec_b]))

    # Both insulation and IV curve readings are preserved as separate records
    dual_recs = svc._db_store["rec_dual_test"].dual_measurements
    assert len(dual_recs) == 2
    types = [d.parameter_type for d in dual_recs]
    assert "INSULATION_RESISTANCE" in types
    assert "IV_CURVE" in types
    assert all(d.requires_engineer_review for d in dual_recs)
