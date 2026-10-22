"""
Automated CI Test: calc_sizing_dc Non-Trivial Intermediate Voltage Assertions
Per Technical Specification §5.2 & Sprint 4 Kickoff Item 2
Asserts that calc_sizing_dc returns non-trivial cold Voc (> 40V) and hot Vmp (> 30V) intermediate values.
"""

import pytest
from calc.calc_sizing_dc.service import DCSizingInput, calculate_dc_sizing


def test_calc_sizing_dc_intermediate_values_non_trivial():
    inputs = DCSizingInput(
        v_oc_stc=49.5,
        v_mp_stc=41.2,
        noct_c=45.0,
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

    # Non-trivial value assertions proving calculations actually executed
    assert inter["v_oc_module_max_cold_v"] > 40.0
    assert inter["v_mp_module_min_hot_v"] > 30.0
    assert inter["v_oc_module_max_cold_v"] == 54.35
    assert inter["v_mp_module_min_hot_v"] == 39.04
    assert inter["t_cell_cold_c"] == 21.25  # NOCT cell temp under 1000 W/m2 at -10 C ambient
    assert inter["i_sc_module_max_hot_a"] > 0
