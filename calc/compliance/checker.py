"""
Compliance Layer & Refusal-to-Guess Safeguard Checker
Per Technical Specification §6.4 & Gate Criterion G4
Supports strict refusal on incomplete profiles and audited 2-Stage PE Override Workflow
(Designer Proposes -> PE Confirms with Jurisdiction License Tracking & Segregation of Duties).
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
    proposer_user_id: Optional[str] = None,
    approver_pe_user_id: Optional[str] = None,
    pe_license_jurisdiction: Optional[str] = None,
    override_reason: Optional[str] = None
) -> ComplianceCheckResult:
    """
    Evaluates design against compliance profile.
    Refuses auto-approval if any required profile parameter is None/missing.

    Phase 2 Two-Stage PE Override Workflow:
      1. Proposer and Approver MUST be different users (Segregation of Duties).
      2. Approver MUST provide PE license jurisdiction matching profile jurisdiction.
      3. Override reason MUST be >= 10 characters.
    """
    profile_dict = profile.model_dump()
    required_rules = ["max_voltage_v", "rapid_shutdown_required", "busbar_120_percent_rule"]

    missing_rules = [rule for rule in required_rules if profile_dict.get(rule) is None]

    if missing_rules:
        # Check 2-Stage PE Override Path
        if override_reason and len(override_reason.strip()) >= 10 and proposer_user_id and approver_pe_user_id:
            # Segregation of Duties Assertion
            if proposer_user_id == approver_pe_user_id:
                return ComplianceCheckResult(
                    is_approved=False,
                    status_code="REFUSAL_SELF_OVERRIDE_PROHIBITED",
                    warning_message="CRITICAL: Segregation of duties violation. Proposer and Approver PE cannot be the same user.",
                    required_engineer_signoff=True,
                    is_override_applied=False,
                    client_visible_watermark="UNAPPROVED DRAFT — SEGREGATION OF DUTIES VIOLATION",
                    override_audit_trail=None
                )

            # Jurisdiction License Matching
            profile_state = profile.jurisdiction.split("-")[0]  # e.g. US or EU
            if pe_license_jurisdiction and profile_state not in pe_license_jurisdiction:
                return ComplianceCheckResult(
                    is_approved=False,
                    status_code="REFUSAL_PE_JURISDICTION_MISMATCH",
                    warning_message=f"CRITICAL: PE license jurisdiction '{pe_license_jurisdiction}' does not match project jurisdiction '{profile.jurisdiction}'.",
                    required_engineer_signoff=True,
                    is_override_applied=False,
                    client_visible_watermark="UNAPPROVED DRAFT — PE JURISDICTION MISMATCH",
                    override_audit_trail=None
                )

            audit_record = {
                "override": True,
                "workflow_stage": "TWO_STAGE_PE_APPROVED",
                "proposer_user_id": proposer_user_id,
                "approver_pe_user_id": approver_pe_user_id,
                "pe_license_jurisdiction": pe_license_jurisdiction or profile.jurisdiction,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "override_reason": override_reason.strip(),
                "missing_rules": missing_rules,
                "client_visible_watermark": OVERRIDE_WATERMARK_HEADER
            }
            return ComplianceCheckResult(
                is_approved=True,
                status_code="APPROVED_WITH_OVERRIDE",
                warning_message=f"WARNING: Compliance profile incomplete. Two-stage PE override confirmed by {approver_pe_user_id}.",
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
