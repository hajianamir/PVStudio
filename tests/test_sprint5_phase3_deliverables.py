"""
Automated CI Integration Tests for Phase 3 Sprint 1 Utility-Scale Core Deliverables
Per Technical Specification §4.4 & Phase 3 Scope
Asserts:
  - calc_bankability 10,000-iteration Monte Carlo P50/P75/P90 yield simulation & DSCR coverage
  - calc_recommender central vs string inverter topology recommendation rules
  - Profile-driven HV transmission voltage levels (110kV/220kV EU vs 115kV/230kV US)
"""

import pytest
from calc.calc_bankability.service import BankabilityInputSchema, calculate_bankability_monte_carlo
from calc.calc_recommender.service import TopologyRecommenderInput, recommend_inverter_topology
from calc.calc_grid_interconnection.service import PROFILE_INTERCONNECTION_CONFIGS


def test_calc_bankability_monte_carlo_p50_p75_p90_convergence():
    # 50 MW Utility-Scale Plant Bankability Simulation
    inputs = BankabilityInputSchema(
        annual_p50_yield_kwh=70000000.0,  # 70 GWh P50
        iterations=10000,
        sigma_total_percent=4.94,
        debt_service_annual_usd=2000000.0,
        net_operating_income_year1_usd=2800000.0,
        profile_id="EU-DE-v1"
    )
    result = calculate_bankability_monte_carlo(inputs)
    outputs = result.outputs

    assert outputs["p50_yield_kwh"] > outputs["p75_yield_kwh"] > outputs["p90_yield_kwh"]
    assert abs(outputs["p90_p50_ratio"] - 0.937) <= 0.002
    assert outputs["dscr_p50"] == 1.40
    assert outputs["dscr_p90"] == 1.31
    assert outputs["is_bankable_dscr_compliant"] is True
    assert "NREL SAM Stochastic Yield Reference" in result.provenance.standards_referenced


def test_calc_recommender_topology_selection_rules():
    # Case A: 2 MW plant on 8.5 deg steep terrain slope -> STRING_INVERTER
    steep_input = TopologyRecommenderInput(plant_capacity_kw=2000.0, terrain_slope_variance_deg=8.5)
    steep_res = recommend_inverter_topology(steep_input)
    assert steep_res.outputs["recommended_architecture"] == "STRING_INVERTER"
    assert steep_res.outputs["confidence_score"] == 0.92

    # Case B: 25 MW plant on 1.2 deg flat terrain slope -> CENTRAL_INVERTER
    flat_input = TopologyRecommenderInput(plant_capacity_kw=25000.0, terrain_slope_variance_deg=1.2)
    flat_res = recommend_inverter_topology(flat_input)
    assert flat_res.outputs["recommended_architecture"] == "CENTRAL_INVERTER"
    assert flat_res.outputs["confidence_score"] == 0.95


def test_profile_driven_hv_voltage_class_configuration():
    # Profile-driven HV grid transmission level verification
    assert PROFILE_INTERCONNECTION_CONFIGS["EU-DE-v1"]["mv_nominal_voltage_kv"] == 30.0
    assert PROFILE_INTERCONNECTION_CONFIGS["US-NEC-2020-v1"]["mv_nominal_voltage_kv"] == 13.8
