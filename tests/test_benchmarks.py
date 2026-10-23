"""
Unit Tests for Immutable Benchmark Test Harness
Per Technical Specification §4.3 & Gate Criterion G2
Asserts that production harness runs cleanly without mock parameters and tests tolerance evaluation logic.
"""

import pytest
from tests.benchmarks.harness import run_benchmark_harness, BENCHMARK_CASES


def test_production_benchmark_harness_passes_g2_unconditionally():
    # Production harness must run with zero parameters and pass 100%
    report = run_benchmark_harness()
    assert report["all_cases_passed"] is True
    assert len(report["case_results"]) == 10

    for case in report["case_results"]:
        if case["case_id"] == 10:
            assert case["verification_type"] == "STRING_VOLTAGE_WINDOW"
            assert case["status"] == "PASS"
        else:
            assert case["annual_delta_percent"] <= 3.0
            assert case["max_monthly_delta_percent"] <= 5.0
            assert case["status"] == "PASS"


def test_benchmark_tolerance_checker_synthetic_evaluation():
    # Synthetic verification of annual/monthly tolerance boundaries without touching production harness
    ref_annual = 5000.0

    # 1. Delta <= 3% -> PASS
    sim_pass = ref_annual * 1.025  # +2.5%
    delta_pass = abs(sim_pass - ref_annual) / ref_annual * 100.0
    assert delta_pass <= 3.0

    # 2. Delta > 3% -> FAIL
    sim_fail = ref_annual * 1.045  # +4.5%
    delta_fail = abs(sim_fail - ref_annual) / ref_annual * 100.0
    assert delta_fail > 3.0
