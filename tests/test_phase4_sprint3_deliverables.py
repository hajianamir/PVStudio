"""Unit and Integration Tests for Phase 4 Sprint 3 Deliverables.

Verifies:
1. Webhook Subscription Manager for CRM/ERP/BIM integrations.
2. HMAC SHA-256 Event Payload Signing & Dispatching.
"""

import pytest
from app.schemas.webhook import WebhookSubscriptionRequest
from app.services.webhook_service import WebhookService

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
