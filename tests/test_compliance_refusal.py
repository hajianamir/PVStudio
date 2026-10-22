"""
Automated CI Test: Refusal-to-Guess Safeguard (Gate Criterion G4)
Asserts that incomplete compliance profiles block auto-approval and emit explicit sign-off warnings.
"""

import pytest
from calc.compliance.checker import ComplianceProfile, evaluate_design_compliance


def test_compliance_refusal_when_profile_incomplete():
    # Incomplete profile missing busbar_120_percent_rule
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None  # Missing rule
    )

    result = evaluate_design_compliance(incomplete_profile)

    assert result.is_approved is False
    assert result.status_code == "REFUSAL_INCOMPLETE_PROFILE"
    assert result.required_engineer_signoff is True
    assert "busbar_120_percent_rule" in result.warning_message


def test_compliance_approval_when_profile_complete():
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
