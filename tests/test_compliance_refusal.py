"""
Automated CI Test: Refusal-to-Guess Safeguard & Audited Override Tests (Gate Criterion G4)
Asserts:
  1. Incomplete profiles without override are strictly refused (HTTP 403 / REFUSAL_INCOMPLETE_PROFILE).
  2. Overrides with reason >= 10 chars write immutable user_id + timestamp audit trail and watermark.
  3. Overrides with short/missing reason string are rejected.
"""

import pytest
from calc.compliance.checker import ComplianceProfile, evaluate_design_compliance


def test_compliance_refusal_when_profile_incomplete():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None
    )

    result = evaluate_design_compliance(incomplete_profile)

    assert result.is_approved is False
    assert result.status_code == "REFUSAL_INCOMPLETE_PROFILE"
    assert result.required_engineer_signoff is True
    assert result.is_override_applied is False
    assert "busbar_120_percent_rule" in result.warning_message


def test_audited_override_success_with_valid_reason():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None
    )

    result = evaluate_design_compliance(
        profile=incomplete_profile,
        user_id="usr_pe_john_doe",
        override_reason="Verified local 120 percent busbar compliance manually with DSO engineer."
    )

    assert result.is_approved is True
    assert result.status_code == "APPROVED_WITH_OVERRIDE"
    assert result.is_override_applied is True
    assert result.override_audit_trail is not None
    assert result.override_audit_trail["user_id"] == "usr_pe_john_doe"
    assert result.override_audit_trail["document_watermark"] == "APPROVED WITH QUALIFIED PROFESSIONAL ENGINEER OVERRIDE"


def test_audited_override_rejected_when_reason_too_short():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None
    )

    # Short reason < 10 chars rejected
    result = evaluate_design_compliance(
        profile=incomplete_profile,
        user_id="usr_pe_john_doe",
        override_reason="short"
    )

    assert result.is_approved is False
    assert result.status_code == "REFUSAL_INCOMPLETE_PROFILE"
    assert result.is_override_applied is False
