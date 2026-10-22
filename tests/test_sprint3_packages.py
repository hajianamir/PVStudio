"""
Automated CI Tests for Sprint 3 Computational Packages:
`calc_electrical_dc`, `calc_electrical_ac`, `calc_protection`, `calc_grounding_lightning`
"""

import pytest
from calc.calc_electrical_dc.service import DCElectricalInput, calculate_dc_electrical
from calc.calc_electrical_ac.service import ACElectricalInput, calculate_ac_electrical
from calc.calc_protection.service import ProtectionInput, calculate_protection
from calc.calc_grounding_lightning.service import GroundingLightningInput, calculate_grounding_lightning


def test_calc_electrical_dc():
    inputs = DCElectricalInput(i_mp_a=12.5, i_sc_a=13.5, cable_length_m=20.0, nominal_voltage_v=600.0)
    res = calculate_dc_electrical(inputs)
    assert res.outputs["selected_cable_mm2"] == 4.0
    assert res.outputs["voltage_drop_percent"] < 2.0
    assert res.outputs["is_compliant"] is True


def test_calc_electrical_ac():
    inputs = ACElectricalInput(p_ac_kw=5.0, v_ac_nominal_v=230.0, cable_length_m=15.0, phases=1)
    res = calculate_ac_electrical(inputs)
    assert res.outputs["selected_cable_mm2"] == 4.0
    assert res.outputs["voltage_drop_percent"] < 1.5
    assert res.outputs["is_compliant"] is True


def test_calc_protection():
    inputs = ProtectionInput(i_sc_stc_a=13.5, i_ac_nominal_a=21.7, parallel_strings=1)
    res = calculate_protection(inputs)
    assert res.outputs["is_dc_fuse_required"] is False
    assert res.outputs["recommended_ac_breaker_a"] == 32


def test_calc_grounding_lightning():
    inputs = GroundingLightningInput(soil_resistivity_ohm_m=100.0, earth_rod_length_m=3.0)
    res = calculate_grounding_lightning(inputs)
    assert res.outputs["earth_rod_resistance_ohms"] < 35.0
    assert res.outputs["target_impedance_ohms"] == 10.0
