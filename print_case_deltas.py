import json
from tests.benchmarks.harness import run_benchmark_harness

report = run_benchmark_harness()

print("=== PER-BENCHMARK DELTA REPORT ===")
for c in report["case_results"]:
    if c["verification_type"] == "STRING_VOLTAGE_WINDOW":
        print(f"B{c['case_id']} ({c['name']}): max-cold Voc delta ±{c['voc_max_cold_delta_v']} V | min-hot Vmp delta ±{c['vmp_min_hot_delta_v']} V | string count match: {c['string_count_matched']}")
    else:
        print(f"B{c['case_id']} ({c['name']}): annual +{c['annual_delta_percent']}% | worst-month +{c['max_monthly_delta_percent']}% ({c['worst_month']})")
