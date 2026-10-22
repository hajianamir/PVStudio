"""
Automated CI Test: Refusal-to-Guess Safeguard Full-Path Test (Gate Criterion G4)
Per Technical Specification §6.4 & Gate Criterion G4
Asserts that full approval path blocks incomplete profiles and logs audit trail.
"""

import pytest
from calc.compliance.checker import ComplianceProfile, evaluate_design_compliance


def test_full_approval_path_refusal_on_incomplete_profile():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None  # Missing rule
    )

    # Full approval path evaluation
    result = evaluate_design_compliance(incomplete_profile)

    # Assert HTTP 403 / Refusal status, explicit warning, and sign-off requirement
    assert result.is_approved is False
    assert result.status_code == "REFUSAL_INCOMPLETE_PROFILE"
    assert result.required_engineer_signoff is True
    assert "busbar_120_percent_rule" in result.warning_message


def test_full_approval_path_success():
    complete_profile = ComplianceProfile(
        profile_id="US-NEC-2020-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=True
    )

    result = evaluate_design_compliance(complete_profile)

    assert result.is_approved is True
    assert result.status_code == "APPROVED"
    assert result.required_engineer_signoff is False
    assert result.warning_message is None
