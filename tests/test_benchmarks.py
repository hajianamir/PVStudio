"""
Unit Tests for Benchmark Test Harness & Golden Fixtures
Per Technical Specification §4.3 & Gate Criterion G2
"""

import pytest
from tests.benchmarks.harness import run_benchmark_harness, BENCHMARK_CASES


def test_benchmark_harness_happy_path_passes():
    # Simulated runs within tolerance (+1% annual, +1.5% monthly)
    report = run_benchmark_harness(mock_annual_factor=1.01, mock_monthly_factor=1.015)
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


def test_benchmark_harness_annual_failure_fails_build():
    # Simulated run exceeding annual threshold (+4.5%)
    report = run_benchmark_harness(mock_annual_factor=1.045, mock_monthly_factor=1.01)
    assert report["all_cases_passed"] is False


def test_benchmark_harness_monthly_failure_fails_build():
    # Simulated run exceeding monthly threshold (+6.0%)
    report = run_benchmark_harness(mock_annual_factor=1.01, mock_monthly_factor=1.060)
    assert report["all_cases_passed"] is False
