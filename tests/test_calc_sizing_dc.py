"""
Automated CI Test: calc_sizing_dc Intermediate Transparency Output Test
Per Technical Specification §5.2 & Sprint 3 Core Scope
Asserts that calc_sizing_dc returns intermediate hot/cold module voltages, currents, and delta_t values.
"""

import pytest
from calc.calc_sizing_dc.service import DCSizingInput, calculate_dc_sizing


def test_calc_sizing_dc_intermediate_values_present():
    inputs = DCSizingInput(
        v_oc_stc=49.5,
        v_mp_stc=41.2,
        temp_coeff_voc_percent=-0.28,
        temp_coeff_pmp_percent=-0.35,
        site_temp_min_c=-10.0,
        site_temp_max_c=40.0,
        inverter_v_max_dc=1000.0,
        inverter_v_mppt_min=200.0,
        inverter_v_mppt_max=800.0,
        total_modules_count=36
    )

    result = calculate_dc_sizing(inputs)
    outputs = result.outputs

    assert outputs["is_compliant"] is True
    assert outputs["max_modules_per_string"] == 18
    assert "intermediate_values" in outputs

    inter = outputs["intermediate_values"]
    assert inter["v_oc_module_max_cold_v"] == 54.35
    assert inter["v_mp_module_min_hot_v"] == 39.04
    assert inter["delta_t_cold_c"] == -35.0
    assert inter["delta_t_hot_c"] == 15.0
    assert inter["i_sc_module_max_hot_a"] > 0
