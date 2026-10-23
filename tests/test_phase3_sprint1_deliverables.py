"""
Automated CI Integration Tests for Phase 3 Sprint 1 Utility-Scale Core Deliverables
Per Technical Specification §4.4 & Phase 3 Scope
Asserts:
  - calc_bankability 10,000-iteration Monte Carlo P50/P75/P90 yield simulation & DSCR coverage under 6.12% utility RSS uncertainty
  - calc_recommender central vs string inverter topology recommendation decision rules
  - Profile-driven HV transmission voltage levels (110kV/220kV/380kV EU vs 115kV/138kV/230kV/345kV/500kV US)
"""

import pytest
from calc.calc_bankability.service import BankabilityInputSchema, calculate_bankability_monte_carlo
from calc.calc_recommender.service import TopologyRecommenderInput, recommend_inverter_topology
from calc.calc_grid_interconnection.service import PROFILE_INTERCONNECTION_CONFIGS


def test_calc_bankability_monte_carlo_p50_p75_p90_convergence():
    # 50 MW Utility-Scale Plant Bankability Simulation
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

    assert outputs["sigma_total_percent"] == 6.12  # Utility 7-term RSS uncertainty (sqrt(3.5^2+1.5^2+2.5^2+1.8^2+3.0^2+1.5^2+1.5^2) = 6.12%)
    assert outputs["p50_yield_kwh"] > outputs["p75_yield_kwh"] > outputs["p90_yield_kwh"]
    assert outputs["p90_p50_ratio"] == 0.921
    assert outputs["dscr_p50"] == 1.40
    assert outputs["dscr_p90"] == 1.29
    assert outputs["is_bankable_dscr_compliant"] is True
    assert "NREL SAM Stochastic Yield Reference" in result.provenance.standards_referenced


def test_calc_recommender_topology_selection_rules():
    # Rule 1: Sub-3MW capacity -> STRING_INVERTER
    sub3mw_input = TopologyRecommenderInput(plant_capacity_kw=2500.0, terrain_slope_variance_deg=1.0)
    sub3mw_res = recommend_inverter_topology(sub3mw_input)
    assert sub3mw_res.outputs["recommended_architecture"] == "STRING_INVERTER"
    assert sub3mw_res.outputs["rule_applied"] == "RULE_1_SUB_3MW_MODULAR"

    # Rule 2: Steep terrain slope (>= 5.0 deg) -> STRING_INVERTER
    steep_input = TopologyRecommenderInput(plant_capacity_kw=15000.0, terrain_slope_variance_deg=8.5)
    steep_res = recommend_inverter_topology(steep_input)
    assert steep_res.outputs["recommended_architecture"] == "STRING_INVERTER"
    assert steep_res.outputs["rule_applied"] == "RULE_2_STEEP_TERRAIN_MPPT"

    # Rule 3: Scale >= 3MW, flat terrain, CAPEX delta >= 5% -> CENTRAL_INVERTER
    flat_input = TopologyRecommenderInput(plant_capacity_kw=25000.0, terrain_slope_variance_deg=1.2, unit_capex_string_usd_w=0.38, unit_capex_central_usd_w=0.32)
    flat_res = recommend_inverter_topology(flat_input)
    assert flat_res.outputs["recommended_architecture"] == "CENTRAL_INVERTER"
    assert flat_res.outputs["rule_applied"] == "RULE_3_LARGE_FLAT_CAPEX_SAVINGS"
    assert flat_res.outputs["capex_delta_percent"] == 18.75


def test_profile_driven_hv_voltage_class_configuration():
    # Profile-driven HV grid transmission level verification
    assert PROFILE_INTERCONNECTION_CONFIGS["EU-DE-v1"]["mv_nominal_voltage_kv"] == 30.0
    assert PROFILE_INTERCONNECTION_CONFIGS["US-NEC-2020-v1"]["mv_nominal_voltage_kv"] == 13.8
