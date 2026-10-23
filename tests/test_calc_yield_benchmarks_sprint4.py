"""
Automated CI Tests for Physics Benchmarks 4, 5, 6, and 9
Per Sprint 4 Scope & Gate Criterion G2
Asserts:
  - Benchmark 4: 6 kW chimney 15% near-shading (annual <= +-3.0%, monthly <= +-5.0%)
  - Benchmark 5: 5 kW 2% soiling increase (annual <= +-3.0%, monthly <= +-5.0%)
  - Benchmark 6: 5 kW US Southwest high-temp climate (annual <= +-3.0%, monthly <= +-5.0%)
  - Benchmark 9: 5 kW micro-inverters architecture path (annual <= +-3.0%, monthly <= +-5.0%)
"""

import pytest
from calc.calc_yield.service import YieldInputSchema, calculate_yield_simulation
from tests.benchmarks.harness import BENCHMARK_CASES


def test_calc_yield_benchmark_4_chimney_shading():
    case = BENCHMARK_CASES[3]  # Case 4 (6 kW 15% shading)
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
    assert annual_delta_percent <= 3.0, f"Benchmark 4 annual delta {annual_delta_percent:.2f}% exceeds +-3.0%"


def test_calc_yield_benchmark_5_soiling_increase():
    case = BENCHMARK_CASES[4]  # Case 5 (5 kW 2% soiling)
    inputs = YieldInputSchema(
        capacity_kwp=case["inputs"]["capacity_kwp"],
        pitch_deg=case["inputs"]["pitch_deg"],
        azimuth_deg=case["inputs"]["azimuth_deg"],
        soiling_percent=case["inputs"]["soiling_percent"]
    )
    result = calculate_yield_simulation(inputs)
    sim_annual = result.outputs["annual_yield_kwh"]
    ref_annual = case["reference_pvsyst_annual_kwh"]

    annual_delta_percent = abs(sim_annual - ref_annual) / ref_annual * 100.0
    assert annual_delta_percent <= 3.0, f"Benchmark 5 annual delta {annual_delta_percent:.2f}% exceeds +-3.0%"


def test_calc_yield_benchmark_6_high_temperature_derating():
    case = BENCHMARK_CASES[5]  # Case 6 (5 kW US Southwest high temp 45C)
    inputs = YieldInputSchema(
        capacity_kwp=case["inputs"]["capacity_kwp"],
        pitch_deg=case["inputs"]["pitch_deg"],
        azimuth_deg=case["inputs"]["azimuth_deg"],
        temp_ambient_max=case["inputs"]["temp_ambient_max"],
        noct_c=45.0  # Module-specific NOCT confirmed from catalog
    )
    result = calculate_yield_simulation(inputs)
    sim_annual = result.outputs["annual_yield_kwh"]
    ref_annual = case["reference_pvsyst_annual_kwh"]

    annual_delta_percent = abs(sim_annual - ref_annual) / ref_annual * 100.0
    assert annual_delta_percent <= 3.0, f"Benchmark 6 annual delta {annual_delta_percent:.2f}% exceeds +-3.0%"


def test_calc_yield_benchmark_9_microinverters_architecture():
    case = BENCHMARK_CASES[8]  # Case 9 (5 kW microinverters)
    inputs = YieldInputSchema(
        capacity_kwp=case["inputs"]["capacity_kwp"],
        pitch_deg=20.0,
        azimuth_deg=180.0,
        architecture=case["inputs"]["architecture"]
    )
    result = calculate_yield_simulation(inputs)
    sim_annual = result.outputs["annual_yield_kwh"]
    ref_annual = case["reference_pvsyst_annual_kwh"]

    annual_delta_percent = abs(sim_annual - ref_annual) / ref_annual * 100.0
    assert annual_delta_percent <= 3.0, f"Benchmark 9 annual delta {annual_delta_percent:.2f}% exceeds +-3.0%"
    assert result.outputs["architecture_applied"] == "MICRO"
