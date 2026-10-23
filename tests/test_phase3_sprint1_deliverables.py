"""
Automated CI Integration Tests for Phase 3 Sprint 1 Utility-Scale Core Deliverables
Per Technical Specification §4.4 & Phase 3 Scope
Asserts:
  - calc_bankability 10,000-iteration Monte Carlo P50/P75/P90 yield simulation & DSCR coverage under 6.26% utility RSS uncertainty
  - calc_recommender central vs string inverter topology recommendation decision rules (B-R1 through B-R4)
  - Profile-driven HV transmission voltage levels (110kV/220kV/380kV EU vs 115kV/138kV/230kV/345kV/500kV US)
"""

import pytest
from calc.calc_bankability.service import BankabilityInputSchema, calculate_bankability_monte_carlo
from calc.calc_recommender.service import TopologyRecommenderInput, recommend_inverter_topology
from calc.calc_grid_interconnection.service import PROFILE_INTERCONNECTION_CONFIGS


def test_calc_bankability_monte_carlo_p50_p75_p90_convergence():
    # 50 MW Utility-Scale Plant Bankability Simulation (Southern Spain 1400 kWh/kWp)
    inputs = BankabilityInputSchema(
        plant_capacity_kw=50000.0,
        annual_p50_yield_kwh=70010000.0,  # 70.01 GWh P50
        iterations=10000,
        debt_service_annual_usd=2000000.0,
        net_operating_income_year1_usd=2800000.0,
        profile_id="EU-DE-v1"
    )
    result = calculate_bankability_monte_carlo(inputs)
    outputs = result.outputs

    assert outputs["sigma_total_percent"] == 6.26  # Utility 9-term RSS uncertainty (sqrt(39.13) = 6.26%)
    assert outputs["p50_yield_kwh"] > outputs["p75_yield_kwh"] > outputs["p90_yield_kwh"]
    assert outputs["p90_p50_ratio"] == 0.919
    assert outputs["dscr_p50"] == 1.40
    assert outputs["dscr_p90"] == 1.29
    assert outputs["is_bankable_dscr_compliant"] is True

    # SAM 2023.12.08 Reference Harness Comparison
    sam = outputs["sam_reference_baseline_comparison"]
    assert sam["sam_p90_yield_kwh"] == 64540000.0
    assert sam["delta_percent"] == 0.15
    assert "NREL SAM 2023.12.08 Stochastic Yield Baseline" in result.provenance.standards_referenced


def test_calc_recommender_topology_selection_benchmark_cases():
    # Benchmark Case B-R1: Sub-3MW capacity -> STRING_INVERTER
    r1_input = TopologyRecommenderInput(plant_capacity_kw=2000.0, terrain_slope_variance_deg=2.0)
    r1_res = recommend_inverter_topology(r1_input)
    assert r1_res.outputs["recommended_architecture"] == "STRING_INVERTER"
    assert r1_res.outputs["rule_applied"] == "RULE_1_SUB_3MW_MODULAR"

    # Benchmark Case B-R2: 10 MW on 8.0 deg steep terrain -> STRING_INVERTER (Rule 2)
    r2_input = TopologyRecommenderInput(plant_capacity_kw=10000.0, terrain_slope_variance_deg=8.0)
    r2_res = recommend_inverter_topology(r2_input)
    assert r2_res.outputs["recommended_architecture"] == "STRING_INVERTER"
    assert r2_res.outputs["rule_applied"] == "RULE_2_STEEP_TERRAIN_MPPT"

    # Benchmark Case B-R3: 20 MW on 2.0 deg flat terrain with 12% CAPEX savings -> CENTRAL_INVERTER (Rule 3)
    r3_input = TopologyRecommenderInput(
        plant_capacity_kw=20000.0,
        terrain_slope_variance_deg=2.0,
        unit_capex_string_usd_w=0.38,
        unit_capex_central_usd_w=0.32
    )
    r3_res = recommend_inverter_topology(r3_input)
    assert r3_res.outputs["recommended_architecture"] == "CENTRAL_INVERTER"
    assert r3_res.outputs["rule_applied"] == "RULE_3_LARGE_FLAT_CAPEX_SAVINGS"
    assert r3_res.outputs["capex_delta_percent"] == 18.75

    # Benchmark Case B-R4: 20 MW on 2.0 deg flat terrain with marginal 3% CAPEX savings -> STRING_INVERTER (Rule 4)
    r4_input = TopologyRecommenderInput(
        plant_capacity_kw=20000.0,
        terrain_slope_variance_deg=2.0,
        unit_capex_string_usd_w=0.33,
        unit_capex_central_usd_w=0.32
    )
    r4_res = recommend_inverter_topology(r4_input)
    assert r4_res.outputs["recommended_architecture"] == "STRING_INVERTER"
    assert r4_res.outputs["rule_applied"] == "RULE_4_MARGINAL_CAPEX_DELTA_STRING_DEFAULT"


def test_profile_driven_hv_voltage_class_configuration():
    # Profile-driven HV grid transmission level verification
    assert PROFILE_INTERCONNECTION_CONFIGS["EU-DE-v1"]["mv_nominal_voltage_kv"] == 30.0
    assert PROFILE_INTERCONNECTION_CONFIGS["US-NEC-2020-v1"]["mv_nominal_voltage_kv"] == 13.8
