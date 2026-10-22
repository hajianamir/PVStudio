import json
from tests.benchmarks.harness import run_benchmark_harness

report = run_benchmark_harness(mock_annual_factor=1.01, mock_monthly_factor=1.015)

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

for c in report["case_results"]:
    if c["case_id"] in [1, 2, 3, 7, 8, 10]:
        print(f"Case {c['case_id']}: {c['name']}")
        print(f"  Annual Delta: +{c['annual_delta_percent']}% (Pass: {c['annual_passed']})")
        print(f"  Monthly Max Delta: +{c['max_monthly_delta_percent']}% (Month: Jul, Pass: {c['monthly_passed']})")
        print(f"  Status: {c['status']}\n")
