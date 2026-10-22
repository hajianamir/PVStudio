"""
Automated CI Test: Refusal-to-Guess Safeguard & Client-Visible Watermark Tests (Gate Criterion G4)
Asserts:
  1. Incomplete profiles without override are strictly refused and return UNAPPROVED DRAFT watermark.
  2. Overrides return client-visible watermark OVERRIDE_WATERMARK_HEADER in API responses.
"""

import pytest
from calc.compliance.checker import ComplianceProfile, evaluate_design_compliance, OVERRIDE_WATERMARK_HEADER


def test_compliance_refusal_returns_unapproved_draft_watermark():
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
    assert result.client_visible_watermark == "UNAPPROVED DRAFT — INCOMPLETE COMPLIANCE PROFILE"


def test_audited_override_returns_client_visible_watermark():
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
    assert result.client_visible_watermark == OVERRIDE_WATERMARK_HEADER
    assert result.override_audit_trail["client_visible_watermark"] == OVERRIDE_WATERMARK_HEADER
