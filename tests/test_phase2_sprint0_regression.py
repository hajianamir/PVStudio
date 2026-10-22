"""
Phase 2 Sprint 0 Regression Baseline Test Suite
Per Phase 2 Readiness Memo & Kickoff Directive
Asserts that all Phase 1 gates remain 100% green before any Phase 2 C&I feature code is added.
"""

import pytest
from tests.run_phase1_acceptance_gates import run_phase1_acceptance_gates


def test_phase2_sprint0_regression_baseline():
    report = run_phase1_acceptance_gates()
    assert report["automated_gates_passed"] is True
    assert report["gates_passed"] == 9  # 9 automated PASS + 1 MANUAL_REQUIRED
    assert report["manual_required_count"] == 1
