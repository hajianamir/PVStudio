"""
Automated CI Test: calc_grid_interconnection Profile-Driven Symmetric LV vs MV Selection Test
Per Technical Specification §4.4 Module 8 & Sprint 2 Action Item 1 Fix
Asserts:
  1. US-NEC-2020-v1: 80 kW -> LV_0.48kV, 200 kW -> LV_0.48kV (<250kW ceiling), 750 kW -> MV_13.8kV
  2. EU-DE-v1: 80 kW -> LV_0.4kV, 200 kW -> MV_33kV (>100kW ceiling per VDE-AR-N 4105), 750 kW -> MV_33kV
"""

import pytest
from calc.calc_grid_interconnection.service import InterconnectionInput, calculate_grid_interconnection


def test_us_profile_voltage_selection_matrix():
    # 80 kW US -> LV_0.48kV
    res_80 = calculate_grid_interconnection(InterconnectionInput(plant_capacity_kw=80.0, profile_id="US-NEC-2020-v1"))
    assert res_80.outputs["is_lv_connection"] is True
    assert res_80.outputs["voltage_class"] == "LV_0.48kV"
    assert res_80.outputs["recommended_voltage_kv"] == 0.48

    # 200 kW US -> LV_0.48kV (below 250 kW US ceiling)
    res_200 = calculate_grid_interconnection(InterconnectionInput(plant_capacity_kw=200.0, profile_id="US-NEC-2020-v1"))
    assert res_200.outputs["is_lv_connection"] is True
    assert res_200.outputs["voltage_class"] == "LV_0.48kV"

    # 750 kW US -> MV_13.8kV
    res_750 = calculate_grid_interconnection(InterconnectionInput(plant_capacity_kw=750.0, profile_id="US-NEC-2020-v1"))
    assert res_750.outputs["is_lv_connection"] is False
    assert res_750.outputs["voltage_class"] == "MV_13.8kV"
    assert res_750.outputs["recommended_voltage_kv"] == 13.8
    assert res_750.outputs["total_substation_bays"] == 4


def test_eu_profile_voltage_selection_matrix():
    # 80 kW EU-DE -> LV_0.4kV
    res_80 = calculate_grid_interconnection(InterconnectionInput(plant_capacity_kw=80.0, profile_id="EU-DE-v1"))
    assert res_80.outputs["is_lv_connection"] is True
    assert res_80.outputs["voltage_class"] == "LV_0.4kV"
    assert res_80.outputs["recommended_voltage_kv"] == 0.4

    # 200 kW EU-DE -> MV_33kV (ABOVE 100 kW EU ceiling per VDE-AR-N 4105/4110)
    res_200 = calculate_grid_interconnection(InterconnectionInput(plant_capacity_kw=200.0, profile_id="EU-DE-v1"))
    assert res_200.outputs["is_lv_connection"] is False
    assert res_200.outputs["voltage_class"] == "MV_33.0kV"
    assert res_200.outputs["recommended_voltage_kv"] == 33.0
    assert res_200.outputs["total_substation_bays"] == 4

    # 750 kW EU-DE -> MV_33kV
    res_750 = calculate_grid_interconnection(InterconnectionInput(plant_capacity_kw=750.0, profile_id="EU-DE-v1"))
    assert res_750.outputs["is_lv_connection"] is False
    assert res_750.outputs["voltage_class"] == "MV_33.0kV"


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
