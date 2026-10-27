"""Webhook Subscription & HMAC Signing Dispatch Service for CRM/ERP/BIM Integrations."""

import datetime
import hmac
import hashlib
import json
import uuid
from typing import Dict, Any, List
from app.schemas.webhook import WebhookSubscriptionRequest, WebhookEventPayload

class WebhookService:
    def __init__(self):
        self._subscriptions: Dict[str, WebhookSubscriptionRequest] = {}

    def register_subscription(self, sub: WebhookSubscriptionRequest) -> WebhookSubscriptionRequest:
        self._subscriptions[sub.subscription_id] = sub
        return sub

    def dispatch_event(self, event_type: str, project_id: str, payload_data: Dict[str, Any]) -> List[WebhookEventPayload]:
        """Dispatches event payload to all subscribed endpoints with HMAC SHA-256 signatures."""
        dispatched = []
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        for sub in self._subscriptions.values():
            if event_type in sub.subscribed_events:
                event_id = str(uuid.uuid4())
                raw_body = json.dumps({"event_id": event_id, "event_type": event_type, "project_id": project_id, "data": payload_data})
                signature = hmac.new(sub.secret_key.encode('utf-8'), raw_body.encode('utf-8'), hashlib.sha256).hexdigest()

                payload = WebhookEventPayload(
                    event_id=event_id,
                    event_type=event_type,
                    project_id=project_id,
                    timestamp_utc=now_str,
                    data=payload_data,
                    hmac_signature=signature
                )
                dispatched.append(payload)

        return dispatched
