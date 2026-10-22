"""
Automated CI Test: 10 Physics Benchmark Cases & Dual Tolerance Failure Assertions
Asserts:
  1. Annual P50 delta <= +-3.0%
  2. Monthly P50 max delta <= +-5.0%
  3. Fails build if EITHER annual OR monthly tolerance is exceeded.
"""

import pytest
from tests.benchmarks.harness import run_benchmark_harness


def test_benchmark_harness_happy_path_passes():
    # Simulated runs within tolerance (+1% annual, +1.5% monthly)
    report = run_benchmark_harness(mock_annual_factor=1.01, mock_monthly_factor=1.015)
    assert report["all_cases_passed"] is True
    assert len(report["case_results"]) == 10

    for case in report["case_results"]:
        assert case["annual_delta_percent"] <= 3.0
        assert case["max_monthly_delta_percent"] <= 5.0
        assert case["status"] == "PASS"


def test_benchmark_harness_annual_failure_fails_build():
    # Simulated annual failure (+4% annual delta > 3%)
    report = run_benchmark_harness(mock_annual_factor=1.04, mock_monthly_factor=1.015)
    assert report["all_cases_passed"] is False
    assert report["case_results"][0]["annual_passed"] is False
    assert report["case_results"][0]["status"] == "FAIL"


def test_benchmark_harness_monthly_failure_fails_build():
    # Simulated monthly failure (+6% monthly delta > 5%)
    report = run_benchmark_harness(mock_annual_factor=1.01, mock_monthly_factor=1.06)
    assert report["all_cases_passed"] is False
    assert report["case_results"][0]["monthly_passed"] is False
    assert report["case_results"][0]["status"] == "FAIL"
