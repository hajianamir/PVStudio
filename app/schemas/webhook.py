"""Webhook Event Subscription Schemas for CRM/ERP/BIM System Integrations."""

import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class WebhookSubscriptionRequest(BaseModel):
    subscription_id: str = Field(..., description="Unique client subscription UUID")
    client_name: str = Field(..., description="Target system (e.g. Salesforce CRM, SAP ERP, Autodesk BIM)")
    target_url: str = Field(..., description="HTTPS webhook payload listener URL")
    subscribed_events: List[str] = Field(..., description="List of event topics (e.g. PROJECT_APPROVED, INSPECTION_COMPLETED)")
    secret_key: str = Field(..., description="Shared HMAC signing secret")

class WebhookEventPayload(BaseModel):
    event_id: str
    event_type: str
    project_id: str
    timestamp_utc: str
    data: Dict[str, Any]
    hmac_signature: str
