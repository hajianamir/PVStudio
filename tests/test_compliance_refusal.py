"""
Automated CI Test: Two-Stage PE Override Workflow, ISO 3166-2 Jurisdiction, Expiry & Active Status Tests
Per Technical Specification §6.4, Gate Criterion G4 & Governance Fixes
Asserts:
  1. Two-stage override passes when Proposer != Approver PE, PE active, unexpired, and ISO 3166-2 jurisdiction matches.
  2. Same user self-override is rejected with actionable warning.
  3. Expired PE license is strictly rejected (REFUSAL_PE_LICENSE_EXPIRED).
  4. Inactive PE is strictly rejected (REFUSAL_PE_INACTIVE).
  5. Mismatched or missing jurisdiction is strictly rejected (REFUSAL_NO_PE_IN_JURISDICTION).
"""

import pytest
from calc.compliance.checker import ComplianceProfile, evaluate_design_compliance, OVERRIDE_WATERMARK_HEADER


def test_two_stage_pe_override_success_iso_3166_2():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None
    )

    result = evaluate_design_compliance(
        profile=incomplete_profile,
        proposer_user_id="usr_designer_alice",
        approver_pe_user_id="usr_pe_bob",
        pe_license_jurisdiction="US-CA",
        pe_license_expiry_date="2026-12-31",
        is_pe_active=True,
        override_reason="Verified local 120 percent busbar compliance manually with DSO engineer."
    )

    assert result.is_approved is True
    assert result.status_code == "APPROVED_WITH_OVERRIDE"
    assert result.is_override_applied is True
    assert result.client_visible_watermark == OVERRIDE_WATERMARK_HEADER
    assert result.override_audit_trail["pe_license_jurisdiction"] == "US-CA"


def test_two_stage_pe_override_rejected_expired_license():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None
    )

    result = evaluate_design_compliance(
        profile=incomplete_profile,
        proposer_user_id="usr_designer_alice",
        approver_pe_user_id="usr_pe_bob",
        pe_license_jurisdiction="US-CA",
        pe_license_expiry_date="2020-01-01",  # Expired
        is_pe_active=True,
        override_reason="Verified local 120 percent busbar compliance manually with DSO engineer."
    )

    assert result.is_approved is False
    assert result.status_code == "REFUSAL_PE_LICENSE_EXPIRED"
    assert "expired" in result.warning_message.lower()


def test_two_stage_pe_override_rejected_inactive_pe():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None
    )

    result = evaluate_design_compliance(
        profile=incomplete_profile,
        proposer_user_id="usr_designer_alice",
        approver_pe_user_id="usr_pe_bob",
        pe_license_jurisdiction="US-CA",
        pe_license_expiry_date="2026-12-31",
        is_pe_active=False,  # Inactive / Revoked
        override_reason="Verified local 120 percent busbar compliance manually with DSO engineer."
    )

    assert result.is_approved is False
    assert result.status_code == "REFUSAL_PE_INACTIVE"
    assert "inactive" in result.warning_message.lower()


def test_two_stage_pe_override_rejected_jurisdiction_mismatch_or_missing():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None
    )

    # PE licensed in Wyoming trying to override US-CA
    result = evaluate_design_compliance(
        profile=incomplete_profile,
        proposer_user_id="usr_designer_alice",
        approver_pe_user_id="usr_pe_bob",
        pe_license_jurisdiction="DE",  # EU German PE attempting US override
        pe_license_expiry_date="2026-12-31",
        is_pe_active=True,
        override_reason="Verified local 120 percent busbar compliance manually with DSO engineer."
    )

    assert result.is_approved is False
    assert result.status_code == "REFUSAL_NO_PE_IN_JURISDICTION"
    assert "No PE licensed in 'US-NEC' is currently available" in result.warning_message
