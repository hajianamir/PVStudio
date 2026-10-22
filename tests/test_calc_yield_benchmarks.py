"""
Automated CI Test: calc_yield v0 Engine Execution against Benchmarks 1-3
Per Sprint 2 Scope & Action Item 4 (Hard-Fail Monthly & Annual Assertions)
"""

import pytest
from calc.calc_yield.service import YieldInputSchema, calculate_yield_simulation
from tests.benchmarks.harness import BENCHMARK_CASES


def test_calc_yield_benchmark_1_eude_flat():
    case = BENCHMARK_CASES[0]  # Case 1
    inputs = YieldInputSchema(
        capacity_kwp=case["inputs"]["capacity_kwp"],
        pitch_deg=case["inputs"]["pitch_deg"],
        azimuth_deg=case["inputs"]["azimuth_deg"],
        shading_percent=case["inputs"]["shading_percent"]
    )
    result = calculate_yield_simulation(inputs)
    sim_annual = result.outputs["annual_yield_kwh"]
    ref_annual = case["reference_pvsyst_annual_kwh"]

    annual_delta_percent = abs(sim_annual - ref_annual) / ref_annual * 100.0
    assert annual_delta_percent <= 3.0, f"Benchmark 1 annual delta {annual_delta_percent:.2f}% exceeds +-3.0%"

    # Monthly hard-fail assertions
    sim_monthly = result.outputs["monthly_yield_kwh"]
    ref_monthly = case["reference_pvsyst_monthly_kwh"]
    monthly_deltas = [abs(sim - ref) / ref * 100.0 for sim, ref in zip(sim_monthly, ref_monthly)]
    max_monthly_delta = max(monthly_deltas)

    assert max_monthly_delta <= 5.0, f"Benchmark 1 max monthly delta {max_monthly_delta:.2f}% exceeds +-5.0%"


def test_calc_yield_benchmark_2_us_pitched():
    case = BENCHMARK_CASES[1]  # Case 2
    inputs = YieldInputSchema(
        capacity_kwp=case["inputs"]["capacity_kwp"],
        pitch_deg=case["inputs"]["pitch_deg"],
        azimuth_deg=case["inputs"]["azimuth_deg"],
        shading_percent=case["inputs"]["shading_percent"]
    )
    result = calculate_yield_simulation(inputs)
    sim_annual = result.outputs["annual_yield_kwh"]
    ref_annual = case["reference_pvsyst_annual_kwh"]

    annual_delta_percent = abs(sim_annual - ref_annual) / ref_annual * 100.0
    assert annual_delta_percent <= 3.0, f"Benchmark 2 annual delta {annual_delta_percent:.2f}% exceeds +-3.0%"

    sim_monthly = result.outputs["monthly_yield_kwh"]
    ref_monthly = case["reference_pvsyst_monthly_kwh"]
    monthly_deltas = [abs(sim - ref) / ref * 100.0 for sim, ref in zip(sim_monthly, ref_monthly)]
    max_monthly_delta = max(monthly_deltas)

    assert max_monthly_delta <= 5.0, f"Benchmark 2 max monthly delta {max_monthly_delta:.2f}% exceeds +-5.0%"


def test_calc_yield_benchmark_3_east_facing():
    case = BENCHMARK_CASES[2]  # Case 3
    inputs = YieldInputSchema(
        capacity_kwp=case["inputs"]["capacity_kwp"],
        pitch_deg=case["inputs"]["pitch_deg"],
        azimuth_deg=case["inputs"]["azimuth_deg"],
        shading_percent=case["inputs"]["shading_percent"]
    )
    result = calculate_yield_simulation(inputs)
    sim_annual = result.outputs["annual_yield_kwh"]
    ref_annual = case["reference_pvsyst_annual_kwh"]

    annual_delta_percent = abs(sim_annual - ref_annual) / ref_annual * 100.0
    assert annual_delta_percent <= 3.0, f"Benchmark 3 annual delta {annual_delta_percent:.2f}% exceeds +-3.0%"

    sim_monthly = result.outputs["monthly_yield_kwh"]
    ref_monthly = case["reference_pvsyst_monthly_kwh"]
    monthly_deltas = [abs(sim - ref) / ref * 100.0 for sim, ref in zip(sim_monthly, ref_monthly)]
    max_monthly_delta = max(monthly_deltas)

    assert max_monthly_delta <= 5.0, f"Benchmark 3 max monthly delta {max_monthly_delta:.2f}% exceeds +-5.0%"
