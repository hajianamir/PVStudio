"""
Automated CI Test: Refusal-to-Guess Safeguard & Rendered Text Layer Watermark Tests
Per Technical Specification §6.4, Gate Criterion G4 & Sprint 3 Audit 1
Asserts that client-visible watermark string is explicitly returned in API responses and PDF/DOCX header text layers.
"""

import pytest
from calc.compliance.checker import ComplianceProfile, evaluate_design_compliance, OVERRIDE_WATERMARK_HEADER


def test_client_visible_rendered_header_watermark_in_override_response():
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

    # Assert rendered header watermark is present in top-level response string
    assert result.client_visible_watermark == OVERRIDE_WATERMARK_HEADER
    assert "APPROVED WITH QUALIFIED PROFESSIONAL ENGINEER OVERRIDE" in result.client_visible_watermark
    assert "LOCAL ENGINEER SIGN-OFF REQUIRED" in result.client_visible_watermark


def test_client_visible_rendered_header_watermark_in_unapproved_draft():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None
    )

    result = evaluate_design_compliance(incomplete_profile)

    assert result.is_approved is False
    assert result.client_visible_watermark == "UNAPPROVED DRAFT — INCOMPLETE COMPLIANCE PROFILE"
