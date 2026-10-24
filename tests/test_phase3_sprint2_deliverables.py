"""
Automated CI Integration Tests for Phase 3 Sprint 2 Utility-Scale Core Deliverables
Per Technical Specification §4.4 & Phase 3 Scope
Asserts:
  - calc_bankability 20-year DSCR schedule with fixed escalating OPEX, P50/P90 NOI breakdown, and debt sizing
  - calc_grid_interconnection HV transmission short-circuit fault current, switchgear ratings, and SCADA RTU specs
  - POA irradiance transposition physics for Seville, Spain benchmark
"""

import pytest
from calc.calc_bankability.service import BankabilityInputSchema, calculate_bankability_monte_carlo
from calc.calc_grid_interconnection.service import InterconnectionInput, calculate_grid_interconnection
from calc.calc_recommender.service import TopologyRecommenderInput, recommend_inverter_topology
from calc.catalog.seed_data import SEED_INVERTERS


def test_poa_transposition_seville_physics():
    # 50 MW AC / 53.5 MW DC Seville Benchmark (GHI 1820 -> POA 2050 kWh/m2, PR 81.5%)
    inputs = BankabilityInputSchema(plant_capacity_kw=50000.0, annual_p50_yield_kwh=89385875.0)
    res = calculate_bankability_monte_carlo(inputs)
    outputs = res.outputs

    assert outputs["performance_ratio_pr"] == 0.815
    assert abs(outputs["specific_yield_ac_kwh_kwac_yr"] - 1787.4) <= 1.0
    assert abs(outputs["specific_yield_dc_kwh_kwp_yr"] - 1670.5) <= 1.0
    assert outputs["p50_yield_gwh"] == 89.37
    assert outputs["p90_yield_gwh"] == 82.16


def test_dscr_20_year_schedule_with_fixed_escalating_opex():
    inputs = BankabilityInputSchema(
        plant_capacity_kw=50000.0,
        annual_p50_yield_kwh=89385875.0,
        ppa_tariff_usd_kwh=0.050,
        turnkey_project_capex_usd=40000000.0,
        opex_year1_usd=600000.0,
        opex_escalation_annual_percent=2.0,
        debt_service_annual_usd=2350000.0,
        loan_tenor_years=20
    )
    res = calculate_bankability_monte_carlo(inputs)
    outputs = res.outputs

    noi = outputs["noi_and_dscr_breakdown"]
    assert abs(noi["year_1_noi_p50_usd"] - 3868568.27) <= 100.0
    assert abs(noi["year_1_noi_p90_usd"] - 3508003.02) <= 100.0
    assert noi["year_1_dscr_p50"] == 1.65
    assert noi["year_1_dscr_p90"] == 1.49
    assert noi["year_20_dscr_p90"] == 1.22
    assert noi["minimum_dscr_p90"] == 1.22
    assert noi["minimum_dscr_year"] == 20

    cap = outputs["capital_structure_and_debt_sizing"]
    assert cap["turnkey_project_capex_usd"] == 40000000.0
    assert cap["senior_debt_principal_usd"] == 26954314.86
    assert cap["leverage_debt_ratio_percent"] == 67.39


def test_dscr_p50_vs_p90_noi_breakdown():
    inputs = BankabilityInputSchema(
        plant_capacity_kw=50000.0,
        annual_p50_yield_kwh=89385875.0,
        debt_service_annual_usd=2350000.0
    )
    res = calculate_bankability_monte_carlo(inputs)
    outputs = res.outputs

    sam = outputs["sam_reference_baseline_comparison"]
    assert sam["sam_p90_yield_kwh"] == 82450000.0
    assert sam["delta_percent"] == 0.35  # Exact inline delta: |82,450,000 - 82,163,330| / 82,450,000 = 0.35%


def test_hv_short_circuit_110kv_iec60909():
    hv_input = InterconnectionInput(plant_capacity_kw=50000.0, profile_id="EU-DE-v1")
    hv_res = calculate_grid_interconnection(hv_input)
    outputs = hv_res.outputs

    assert outputs["voltage_class"] == "HV_110.0kV"
    assert outputs["grid_short_circuit_capacity_mva"] == 3500.0
    assert outputs["short_circuit_fault_current_ka"] == 20.21
    assert outputs["switchgear_interrupting_rating_ka"] == 25.0
    assert outputs["requires_utility_data_verification"] is True


def test_hv_substation_transformer_and_switchgear_selection():
    hv_input = InterconnectionInput(plant_capacity_kw=50000.0, profile_id="EU-DE-v1")
    hv_res = calculate_grid_interconnection(hv_input)
    outputs = hv_res.outputs

    assert outputs["transformer_mva_recommended"] == 55.0
    assert outputs["total_substation_bays"] == 4
    assert outputs["scada_poi_specification"]["scada_rtu_telemetry_protocol"] == "IEC 60870-5-104 / DNP3 over IP"


def test_sungrow_sg3125hv_central_skid_catalog_entry():
    sungrow = next(inv for inv in SEED_INVERTERS if inv["id"] == "inv_util_sungrow_3125kw_central")
    assert sungrow["inverter_type"] == "CENTRAL_SKID"
    assert sungrow["p_ac_kw"] == 3125.0
    assert sungrow["v_ac_nominal_v"] == 30000.0
    assert sungrow["v_dc_max_v"] == 1500.0
