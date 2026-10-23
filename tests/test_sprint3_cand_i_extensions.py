"""
Unit & Integration Tests for Phase 2 Sprint 3 C&I AC Collection, MV Protection Extension & Permit Package
Per Technical Specification §4.4 & Sprint 3 Directives
"""

import pytest
from calc.calc_electrical_ac.service import ACElectricalInput, calculate_ac_electrical
from calc.calc_protection.service import ProtectionInput, calculate_protection


def test_mv_ac_collection_cable_and_transformer_sizing():
    # 750 kW C&I Plant at 33 kV MV Collection (EU-DE)
    inputs = ACElectricalInput(
        p_ac_kw=750.0,
        v_ac_nominal_v=33.0,  # 33 kV
        cable_length_m=250.0,
        phases=3,
        power_factor=0.95,
        voltage_class="MV",
        profile_id="EU-DE-v1"
    )
    result = calculate_ac_electrical(inputs)
    outputs = result.outputs

    assert outputs["voltage_class"] == "MV"
    assert outputs["i_ac_nominal_a"] == 13.81  # I = 750kW / (sqrt(3) * 33kV * 0.95)
    assert outputs["required_ampacity_a"] == 17.27  # 13.81 * 1.25
    assert outputs["selected_cable_mm2"] == 70.0  # Min MV XLPE 70mm2
    assert outputs["transformer_kva_recommended"] == 800.0  # 750/0.95 = 789.47 -> 800 kVA
    assert outputs["is_compliant"] is True
    assert "IEEE 141 (AC Feeder Sizing)" in result.provenance.standards_referenced


def test_mv_numerical_relay_and_ct_vt_protection():
    # 750 kW MV Feeder Protection (US-NEC)
    inputs = ProtectionInput(
        i_ac_nominal_a=35.0,  # 35 A MV current
        voltage_class="MV",
        profile_id="US-NEC-2020-v1"
    )
    result = calculate_protection(inputs)
    outputs = result.outputs

    assert outputs["voltage_class"] == "MV"
    assert outputs["recommended_ac_breaker_a"] == 630  # Standard MV Switchgear Breaker
    assert outputs["recommended_ct_ratio"] == "50/5A"
    assert "50 (Instantaneous Overcurrent)" in outputs["numerical_relay_functions"]
    assert "IEEE C37.90 / IEEE 242 (Buff Book) / ANSI 50/51/51N" in result.provenance.standards_referenced
