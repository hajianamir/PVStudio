"""
Automated CI Integration Tests for Phase 3 Sprint 1 Utility-Scale Core Deliverables
Per Technical Specification §4.4 & Phase 3 Scope
Asserts:
  - calc_bankability 10,000-iteration Monte Carlo P50/P75/P90 yield simulation & 20-year DSCR schedule
  - calc_recommender central vs string inverter topology recommendation decision rules (B-R1 through B-R4)
  - Profile-driven HV transmission voltage levels (110kV/220kV/380kV EU vs 115kV/138kV/230kV/345kV/500kV US)
"""

import pytest
from calc.calc_bankability.service import BankabilityInputSchema, calculate_bankability_monte_carlo
from calc.calc_recommender.service import TopologyRecommenderInput, recommend_inverter_topology
from calc.calc_grid_interconnection.service import InterconnectionInput, calculate_grid_interconnection, PROFILE_INTERCONNECTION_CONFIGS


def test_calc_bankability_monte_carlo_p50_p75_p90_convergence():
    # 50 MW AC / 53.5 MW DC Utility-Scale Plant Bankability Simulation (Seville, Spain POA 2050 kWh/m2, 81.5% PR)
    inputs = BankabilityInputSchema(
        plant_capacity_kw=50000.0,
        annual_p50_yield_kwh=89385875.0,  # 89.39 GWh P50
        turnkey_project_capex_usd=40000000.0,  # $40M CAPEX ($0.80/W DC)
        iterations=10000,
        debt_service_annual_usd=2500000.0,
        net_operating_income_year1_p50_usd=3600000.0,
        loan_tenor_years=20,
        profile_id="EU-DE-v1"
    )
    result = calculate_bankability_monte_carlo(inputs)
    outputs = result.outputs

    assert outputs["sigma_total_percent"] == 6.26  # Utility 9-term RSS uncertainty (sqrt(39.13) = 6.26%)
    assert abs(outputs["p50_yield_gwh"] - 89.39) <= 0.03
    assert abs(outputs["p90_yield_gwh"] - 82.21) <= 0.10
    assert outputs["p90_p50_ratio"] == 0.919
    assert abs(outputs["specific_yield_ac_kwh_kwac_yr"] - 1787.7) <= 1.0
    assert abs(outputs["specific_yield_dc_kwh_kwp_yr"] - 1670.8) <= 1.0
    assert outputs["performance_ratio_pr"] == 0.815
    assert len(outputs["dscr_twenty_year_schedule"]) == 20
    assert outputs["dscr_year1_p50"] == 1.44  # P50 Basis Year-1 DSCR ($3.6M / $2.5M = 1.44x)
    assert outputs["dscr_year1_p90"] == 1.32  # P90 Basis Year-1 DSCR ($3.311M / $2.5M = 1.32x)
    assert outputs["minimum_dscr_p90"] == 1.20  # Minimum DSCR occurring in Year 20 ($3.01M / $2.5M = 1.20x)
    assert outputs["minimum_dscr_year"] == 20
    assert outputs["is_bankable_dscr_compliant"] is True

    # Capital Structure & Leverage Rollup Assertions
    cap = outputs["capital_structure_and_debt_sizing"]
    assert cap["turnkey_project_capex_usd"] == 40000000.0
    assert cap["senior_debt_principal_usd"] == 28674803.05
    assert cap["leverage_debt_ratio_percent"] == 71.69

    # SAM 2023.12.08 Reference Harness Comparison
    sam = outputs["sam_reference_baseline_comparison"]
    assert sam["sam_p90_yield_kwh"] == 82450000.0
    assert sam["delta_percent"] == 0.35  # Structural RSS vs Monte Carlo delta
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


def test_hv_substation_grid_interconnection_50mw():
    # 50 MW Utility-Scale Plant Interconnection at 110 kV HV (EU-DE-v1)
    hv_input = InterconnectionInput(
        plant_capacity_kw=50000.0,
        profile_id="EU-DE-v1"
    )
    hv_res = calculate_grid_interconnection(hv_input)
    outputs = hv_res.outputs

    assert outputs["voltage_class"] == "HV_110.0kV"
    assert outputs["recommended_voltage_kv"] == 110.0
    assert outputs["transformer_mva_recommended"] == 55.0  # 50MW / 0.95 = 52.6MVA -> 55 MVA
    assert outputs["grid_short_circuit_capacity_mva"] == 3500.0  # 3500 MVA HV utility transmission capacity
    assert outputs["switchgear_interrupting_rating_ka"] == 25.0  # Selected 25 kA switchgear for 20.21 kA fault current
    assert outputs["short_circuit_fault_current_ka"] == 20.21  # (1.10 * 3500) / (sqrt(3) * 110) = 20.21 kA
    assert outputs["scada_poi_specification"]["scada_rtu_telemetry_protocol"] == "IEC 60870-5-104 / DNP3 over IP"
    assert outputs["requires_utility_data_verification"] is True
    assert outputs["fault_current_warning"] is None
