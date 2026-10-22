"""
Compliance Layer & Refusal-to-Guess Safeguard Checker
Per Technical Specification §6.4 & Gate Criterion G4
Supports strict refusal on incomplete profiles and audited override paths with user identity & reason.

Phase 1 Single-Role Scaffolding Limitation:
  Currently permits single PE user override if valid reason (min 10 chars) provided.
  Multi-role requirement (Designer Proposes -> PE Approves) will be enforced at Gate G4.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

OVERRIDE_WATERMARK_HEADER = "APPROVED WITH QUALIFIED PROFESSIONAL ENGINEER OVERRIDE — LOCAL ENGINEER SIGN-OFF REQUIRED"


class ComplianceProfile(BaseModel):
    profile_id: str
    jurisdiction: str
    max_voltage_v: Optional[int] = None
    rapid_shutdown_required: Optional[bool] = None
    busbar_120_percent_rule: Optional[bool] = None


class ComplianceCheckResult(BaseModel):
    is_approved: bool
    status_code: str
    warning_message: Optional[str] = None
    required_engineer_signoff: bool = False
    is_override_applied: bool = False
    client_visible_watermark: Optional[str] = None
    override_audit_trail: Optional[Dict[str, Any]] = None


def evaluate_design_compliance(
    profile: ComplianceProfile,
    user_id: Optional[str] = None,
    override_reason: Optional[str] = None
) -> ComplianceCheckResult:
    """
    Evaluates design against compliance profile.
    Refuses auto-approval if any required profile parameter is None/missing.
    If override_reason is provided with min length 10 chars, applies audited override
    and attaches client-visible watermark to API response and PDF/DOCX headers.
    """
    profile_dict = profile.model_dump()
    required_rules = ["max_voltage_v", "rapid_shutdown_required", "busbar_120_percent_rule"]

    missing_rules = [rule for rule in required_rules if profile_dict.get(rule) is None]

    if missing_rules:
        # Check if valid override path requested
        if override_reason and len(override_reason.strip()) >= 10 and user_id:
            audit_record = {
                "override": True,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "override_reason": override_reason.strip(),
                "missing_rules": missing_rules,
                "client_visible_watermark": OVERRIDE_WATERMARK_HEADER
            }
            return ComplianceCheckResult(
                is_approved=True,
                status_code="APPROVED_WITH_OVERRIDE",
                warning_message=f"WARNING: Compliance profile incomplete. Manual PE override applied by {user_id}.",
                required_engineer_signoff=True,
                is_override_applied=True,
                client_visible_watermark=OVERRIDE_WATERMARK_HEADER,
                override_audit_trail=audit_record
            )

        # Standard Refusal Path
        return ComplianceCheckResult(
            is_approved=False,
            status_code="REFUSAL_INCOMPLETE_PROFILE",
            warning_message=f"CRITICAL: Refusal-to-Guess safeguard triggered. Missing rules: {', '.join(missing_rules)} in profile '{profile.profile_id}'.",
            required_engineer_signoff=True,
            is_override_applied=False,
            client_visible_watermark="UNAPPROVED DRAFT — INCOMPLETE COMPLIANCE PROFILE",
            override_audit_trail=None
        )

    return ComplianceCheckResult(
        is_approved=True,
        status_code="APPROVED",
        warning_message=None,
        required_engineer_signoff=False,
        is_override_applied=False,
        client_visible_watermark=None,
        override_audit_trail=None
    )
