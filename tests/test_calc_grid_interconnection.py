"""
Automated CI Test: calc_grid_interconnection Refactored Bay Count & Standards Test
Per Technical Specification §4.4 Module 8 & Sprint 1 Refactor
Asserts:
  1. Bay count breakdown (incomer + transformer + metering + spare = 4 bays total for 5.5MW 33kV).
  2. Split citations: IEEE 1547 (Interconnection) vs IEEE 141 (Short Circuit) for US profile.
  3. requires_utility_data_verification flag set when impedance assumed.
"""

import pytest
from calc.calc_grid_interconnection.service import InterconnectionInput, calculate_grid_interconnection


def test_calc_grid_interconnection_refactored_bay_breakdown_us():
    inputs = InterconnectionInput(
        plant_capacity_kw=5500.0,  # 5.5 MW
        grid_impedance_ohm=0.15,
        is_grid_impedance_assumed=True,
        profile_id="US-NEC-2020-v1"
    )

    result = calculate_grid_interconnection(inputs)
    outputs = result.outputs
    citations = outputs["standards_citations"]

    # Bay count assertion: 1 incomer + 1 transformer + 1 metering + 1 spare = 4 bays
    breakdown = outputs["bay_breakdown"]
    assert breakdown["incomer_bays"] == 1
    assert breakdown["transformer_bays"] == 1
    assert breakdown["metering_bays"] == 1
    assert breakdown["spare_bays"] == 1
    assert outputs["total_substation_bays"] == 4

    # Citation split assertions
    assert "IEEE 1547-2018" in citations["interconnection_standard"]
    assert "IEEE 141 (Red Book)" in citations["short_circuit_methodology_standard"]
    assert outputs["requires_utility_data_verification"] is True
