"""
Automated Physics Benchmark Test Harness - Single Consolidated Runner
Executes Benchmarks 1–10 and outputs consolidated pass/fail report with exact deltas.
Marks B3 and B6 as Sensitivity Cases due to tighter monthly margins.
"""

import json
from tests.benchmarks.harness import run_benchmark_harness

SENSITIVITY_CASES = [3, 6]  # Cases with lower monthly tolerance margin


def run_consolidated_ci_benchmarks():
    report = run_benchmark_harness()
    print("=== CONSOLIDATED BENCHMARK SUITE REPORT (1-10) ===")
    for c in report["case_results"]:
        sensitivity_flag = " [SENSITIVITY CASE - MONITOR CLOSELY]" if c["case_id"] in SENSITIVITY_CASES else ""
        if c["verification_type"] == "STRING_VOLTAGE_WINDOW":
            print(f"B{c['case_id']} ({c['name']}): Voc_cold delta +- {c['voc_max_cold_delta_v']}V | Vmp_hot delta +- {c['vmp_min_hot_delta_v']}V | Count match: {c['string_count_matched']} | Status: {c['status']}{sensitivity_flag}")
        else:
            print(f"B{c['case_id']} ({c['name']}): Annual +{c['annual_delta_percent']}% | Worst-Month +{c['max_monthly_delta_percent']}% ({c['worst_month']}) | Status: {c['status']}{sensitivity_flag}")
    print(f"\nALL 10 BENCHMARKS PASSED: {report['all_cases_passed']}")
    return report

if __name__ == "__main__":
    run_consolidated_ci_benchmarks()
