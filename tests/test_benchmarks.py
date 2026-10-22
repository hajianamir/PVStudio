"""
Automated CI Test: 10 Physics Benchmark Cases (Gate Criterion G2)
Asserts that physics engine outputs pass <= +-3.0% annual P50 and <= +-5.0% monthly tolerances.
"""

import pytest
from tests.benchmarks.harness import run_benchmark_harness


def test_benchmark_harness_execution():
    report = run_benchmark_harness()
    assert report["all_cases_passed"] is True
    assert len(report["case_results"]) == 10

    for case in report["case_results"]:
        assert case["annual_delta_percent"] <= 3.0
        assert case["max_monthly_delta_percent"] <= 5.0
        assert case["status"] == "PASS"
