"""
Automated CI Test: Two-Stage PE Override Workflow & Segregation of Duties Tests
Per Phase 2 Sprint 2 Scope & Action Item 2
Asserts:
  1. Two-stage override passes when Proposer != Approver PE and jurisdiction matches.
  2. Same user self-override is strictly rejected (REFUSAL_SELF_OVERRIDE_PROHIBITED).
  3. Mismatched PE license jurisdiction is strictly rejected (REFUSAL_PE_JURISDICTION_MISMATCH).
"""

import pytest
from calc.compliance.checker import ComplianceProfile, evaluate_design_compliance, OVERRIDE_WATERMARK_HEADER


def test_two_stage_pe_override_success():
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
        override_reason="Verified local 120 percent busbar compliance manually with DSO engineer."
    )

    assert result.is_approved is True
    assert result.status_code == "APPROVED_WITH_OVERRIDE"
    assert result.is_override_applied is True
    assert result.client_visible_watermark == OVERRIDE_WATERMARK_HEADER
    assert result.override_audit_trail["proposer_user_id"] == "usr_designer_alice"
    assert result.override_audit_trail["approver_pe_user_id"] == "usr_pe_bob"


def test_two_stage_pe_override_rejected_when_same_user():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None
    )

    # Self-override prohibited
    result = evaluate_design_compliance(
        profile=incomplete_profile,
        proposer_user_id="usr_pe_bob",
        approver_pe_user_id="usr_pe_bob",  # Same user!
        pe_license_jurisdiction="US-CA",
        override_reason="Verified local 120 percent busbar compliance manually with DSO engineer."
    )

    assert result.is_approved is False
    assert result.status_code == "REFUSAL_SELF_OVERRIDE_PROHIBITED"
    assert "Segregation of duties violation" in result.warning_message


def test_two_stage_pe_override_rejected_when_jurisdiction_mismatched():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None
    )

    # PE licensed in EU attempting US override
    result = evaluate_design_compliance(
        profile=incomplete_profile,
        proposer_user_id="usr_designer_alice",
        approver_pe_user_id="usr_pe_charlie",
        pe_license_jurisdiction="EU-DE",  # Mismatch!
        override_reason="Verified local 120 percent busbar compliance manually with DSO engineer."
    )

    assert result.is_approved is False
    assert result.status_code == "REFUSAL_PE_JURISDICTION_MISMATCH"
    assert "jurisdiction" in result.warning_message
