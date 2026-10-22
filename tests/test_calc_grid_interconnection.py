"""
Automated CI Test: calc_grid_interconnection Package & Provenance Test
Per Technical Specification §4.4 Module 8 & Phase 2 Sprint 1 Scope
Asserts:
  1. Voltage level and feeder bay auto-sizing logic.
  2. Provenance envelope carrying standards citations.
"""

import pytest
from calc.calc_grid_interconnection.service import InterconnectionInput, calculate_grid_interconnection


def test_calc_grid_interconnection_mv_33kv():
    inputs = InterconnectionInput(
        plant_capacity_kw=5500.0,  # 5.5 MW C&I plant
        grid_impedance_ohm=0.15,
        profile_id="EU-DE-v1"
    )

    result = calculate_grid_interconnection(inputs)
    outputs = result.outputs
    provenance = result.provenance

    assert outputs["recommended_voltage_kv"] == 33.0
    assert outputs["voltage_class"] == "MV_33kV"
    assert outputs["total_substation_bays"] >= 2  # 1 feeder + 1 spare
    assert outputs["short_circuit_fault_current_ka"] > 0
    assert "VDE-AR-N 4110" in outputs["standard_citation"]
    assert provenance.calc_module == "calc_grid_interconnection"
    assert provenance.calc_version == "1.0.0"
    assert provenance.input_hash != ""
