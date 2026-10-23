"""
Compliance Layer & Refusal-to-Guess Safeguard Checker
Per Technical Specification §6.4 & Gate Criterion G4
Supports strict refusal on incomplete profiles and audited 2-Stage PE Override Workflow
with controlled ISO 3166-2 jurisdiction matching, license expiry checks, and active status verification.
"""

from datetime import datetime, timezone, date
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

OVERRIDE_WATERMARK_HEADER = "APPROVED WITH QUALIFIED PROFESSIONAL ENGINEER OVERRIDE — LOCAL ENGINEER SIGN-OFF REQUIRED"

# Controlled ISO 3166-2 Jurisdiction Codes
VALID_ISO_3166_2_JURISDICTIONS = {
    "US-CA", "US-NY", "US-TX", "US-FL", "US-WY", "US-MA",
    "DE", "DE-BY", "DE-BE", "AU-NSW", "AU-VIC", "AU-QLD"
}


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
    pe_license_expiry_date: Optional[str] = None,  # YYYY-MM-DD
    is_pe_active: bool = True,
    override_reason: Optional[str] = None
) -> ComplianceCheckResult:
    """
    Evaluates design against compliance profile.
    Refuses auto-approval if any required profile parameter is None/missing.

    Phase 2 Two-Stage PE Override Workflow:
      1. Proposer and Approver MUST be different users (Segregation of Duties).
      2. Approver MUST be active and have unexpired PE license matching profile ISO 3166-2 jurisdiction.
      3. Override reason MUST be >= 10 characters.
    """
    profile_dict = profile.model_dump()
    required_rules = ["max_voltage_v", "rapid_shutdown_required", "busbar_120_percent_rule"]

    missing_rules = [rule for rule in required_rules if profile_dict.get(rule) is None]

    if missing_rules:
        # Check 2-Stage PE Override Path
        if override_reason and len(override_reason.strip()) >= 10 and proposer_user_id and approver_pe_user_id:
            # 1. Segregation of Duties Assertion
            if proposer_user_id == approver_pe_user_id:
                return ComplianceCheckResult(
                    is_approved=False,
                    status_code="REFUSAL_SELF_OVERRIDE_PROHIBITED",
                    warning_message=f"You cannot approve your own design override. Ask a PE licensed in '{profile.jurisdiction}' to review and confirm this override.",
                    required_engineer_signoff=True,
                    is_override_applied=False,
                    client_visible_watermark="UNAPPROVED DRAFT — SEGREGATION OF DUTIES VIOLATION",
                    override_audit_trail=None
                )

            # 2. PE Active Status Verification
            if not is_pe_active:
                return ComplianceCheckResult(
                    is_approved=False,
                    status_code="REFUSAL_PE_INACTIVE",
                    warning_message=f"CRITICAL: PE user '{approver_pe_user_id}' is inactive or revoked. Override rejected.",
                    required_engineer_signoff=True,
                    is_override_applied=False,
                    client_visible_watermark="UNAPPROVED DRAFT — INACTIVE PE USER",
                    override_audit_trail=None
                )

            # 3. PE License Expiry Verification
            if pe_license_expiry_date:
                today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                if pe_license_expiry_date < today_str:
                    return ComplianceCheckResult(
                        is_approved=False,
                        status_code="REFUSAL_PE_LICENSE_EXPIRED",
                        warning_message=f"CRITICAL: PE license for '{approver_pe_user_id}' expired on {pe_license_expiry_date}. Override rejected.",
                        required_engineer_signoff=True,
                        is_override_applied=False,
                        client_visible_watermark="UNAPPROVED DRAFT — EXPIRED PE LICENSE",
                        override_audit_trail=None
                    )

            # 4. Controlled ISO 3166-2 Jurisdiction License Matching
            # Match jurisdiction prefix or exact sub-region match (e.g. EU-DE matches DE / DE-BY / DE-BE; US-NEC matches US-CA / US-NY / etc.)
            profile_jur = profile.jurisdiction.upper()
            profile_parts = profile_jur.split("-")

            is_valid_jurisdiction = False
            if pe_license_jurisdiction in VALID_ISO_3166_2_JURISDICTIONS:
                if pe_license_jurisdiction == profile_jur:
                    is_valid_jurisdiction = True
                elif any(part in pe_license_jurisdiction for part in profile_parts):
                    is_valid_jurisdiction = True
                elif any(pe_part in profile_jur for pe_part in pe_license_jurisdiction.split("-")):
                    is_valid_jurisdiction = True

            if not pe_license_jurisdiction or not is_valid_jurisdiction:
                return ComplianceCheckResult(
                    is_approved=False,
                    status_code="REFUSAL_NO_PE_IN_JURISDICTION",
                    warning_message=f"No PE licensed in '{profile.jurisdiction}' is currently available on the platform for override approval. Contact platform administration.",
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
                "pe_license_jurisdiction": pe_license_jurisdiction,
                "pe_license_expiry_date": pe_license_expiry_date,
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
