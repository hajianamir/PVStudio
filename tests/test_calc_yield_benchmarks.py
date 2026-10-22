"""
Automated CI Test: calc_yield v0 Engine Execution against Benchmarks 1-3
Per Sprint 2 Scope
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

    delta_percent = abs(sim_annual - ref_annual) / ref_annual * 100.0
    assert delta_percent <= 3.0, f"Benchmark 1 annual delta {delta_percent:.2f}% exceeds +-3.0%"


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

    delta_percent = abs(sim_annual - ref_annual) / ref_annual * 100.0
    assert delta_percent <= 3.0, f"Benchmark 2 annual delta {delta_percent:.2f}% exceeds +-3.0%"


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

    delta_percent = abs(sim_annual - ref_annual) / ref_annual * 100.0
    assert delta_percent <= 3.0, f"Benchmark 3 annual delta {delta_percent:.2f}% exceeds +-3.0%"
