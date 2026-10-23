"""
Automated CI Test: calc_grid_interconnection Profile-Driven LV vs MV Voltage Selection Test
Per Technical Specification §4.4 Module 8 & Sprint 2 Fixes
Asserts:
  1. Sub-250kW US plant (e.g. 200 kW) selects LV_0.48kV (is_lv_connection=True, bay count N/A = 0).
  2. 750 kW C&I plant selects MV_13.8kV (US) or MV_33kV (EU-DE) with 4 substation bays.
  3. Synthetic Multi-Incomer Plant (35 MW at 33kV) exercises N_incomer = 2 bays (5 bays total).
"""

import pytest
from calc.calc_grid_interconnection.service import InterconnectionInput, calculate_grid_interconnection


def test_calc_grid_interconnection_sub_threshold_lv_200kw():
    inputs = InterconnectionInput(
        plant_capacity_kw=200.0,  # 200 kW sub-250kW LV US plant
        profile_id="US-NEC-2020-v1"
    )

    result = calculate_grid_interconnection(inputs)
    outputs = result.outputs

    assert outputs["is_lv_connection"] is True
    assert outputs["recommended_voltage_kv"] == 0.48
    assert outputs["voltage_class"] == "LV_0.48kV"
    assert outputs["total_substation_bays"] == 0
    assert outputs["lv_main_breaker_rating_a"] > 0


def test_calc_grid_interconnection_cand_i_750kw_mv():
    inputs = InterconnectionInput(
        plant_capacity_kw=750.0,  # 750 kW C&I plant -> MV interconnection
        profile_id="US-NEC-2020-v1"
    )

    result = calculate_grid_interconnection(inputs)
    outputs = result.outputs

    assert outputs["is_lv_connection"] is False
    assert outputs["recommended_voltage_kv"] == 13.8
    assert outputs["voltage_class"] == "MV_13.8kV"
    breakdown = outputs["bay_breakdown"]
    assert breakdown["incomer_bays"] == 1
    assert breakdown["transformer_bays"] == 1
    assert breakdown["metering_bays"] == 1
    assert breakdown["spare_bays"] == 1
    assert outputs["total_substation_bays"] == 4


def test_calc_grid_interconnection_multi_incomer_synthetic_plant():
    inputs = InterconnectionInput(
        plant_capacity_kw=35000.0,  # 35 MW Synthetic Plant
        bay_max_ampacity_a=630.0,
        profile_id="EU-DE-v1"
    )

    result = calculate_grid_interconnection(inputs)
    outputs = result.outputs
    breakdown = outputs["bay_breakdown"]

    assert outputs["recommended_voltage_kv"] == 33.0
    assert breakdown["incomer_bays"] == 2
    assert outputs["total_substation_bays"] == 5
