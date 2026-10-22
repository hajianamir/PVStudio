"""
Automated CI Test: calc_grid_interconnection Package Refactored Bay Count & Multi-Incomer Test
Per Technical Specification §4.4 Module 8 & Sprint 2 Kickoff Item 1
Asserts:
  1. Sub-1 MW C&I Benchmark (750 kW at 33kV) produces 1 incomer + 1 transformer + 1 metering + 1 spare = 4 bays total.
  2. Synthetic Multi-Incomer Plant (35 MW at 33kV, >630A current) exercises N_incomer = 2 bays (5 bays total).
"""

import pytest
from calc.calc_grid_interconnection.service import InterconnectionInput, calculate_grid_interconnection


def test_calc_grid_interconnection_sub_1mw_cand_i_benchmark():
    inputs = InterconnectionInput(
        plant_capacity_kw=750.0,  # 750 kW Sub-1 MW C&I Benchmark
        grid_impedance_ohm=0.15,
        is_grid_impedance_assumed=True,
        profile_id="US-NEC-2020-v1"
    )

    result = calculate_grid_interconnection(inputs)
    outputs = result.outputs

    assert outputs["recommended_voltage_kv"] == 33.0
    breakdown = outputs["bay_breakdown"]
    assert breakdown["incomer_bays"] == 1
    assert breakdown["transformer_bays"] == 1
    assert breakdown["metering_bays"] == 1
    assert breakdown["spare_bays"] == 1
    assert outputs["total_substation_bays"] == 4


def test_calc_grid_interconnection_multi_incomer_synthetic_plant():
    inputs = InterconnectionInput(
        plant_capacity_kw=35000.0,  # 35 MW Synthetic Plant exceeding 630A bay ampacity
        bay_max_ampacity_a=630.0,
        grid_impedance_ohm=0.05,
        profile_id="US-NEC-2020-v1"
    )

    result = calculate_grid_interconnection(inputs)
    outputs = result.outputs
    breakdown = outputs["bay_breakdown"]

    # 35 MW at 33kV = ~644 A -> ceil(644/630) = 2 incomer bays
    assert breakdown["incomer_bays"] == 2
    assert breakdown["transformer_bays"] == 1
    assert breakdown["metering_bays"] == 1
    assert breakdown["spare_bays"] == 1
    assert outputs["total_substation_bays"] == 5
