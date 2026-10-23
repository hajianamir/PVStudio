"""
Automated CI Test: calc_sizing_dc Physical Cell Derating Model Unit Tests
Per Technical Specification §4.4 Module 2 & Sprint 4 Clarification 2
Asserts:
  1. Cold Voc calculated at T_cell = T_amb_min (-10 C)
  2. Hot Vmp calculated with NOCT derating model (T_cell = 71.25 C at 40 C amb)
  3. Intermediate values exposed for calculation transparency side-panel
"""

import pytest
from calc.calc_sizing_dc.service import DCSizingInput, calculate_dc_sizing


def test_calc_sizing_dc_physical_derating_values():
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

    # 1. Cold Voc Verification (T_cell = T_amb_min = -10 C)
    assert inter["t_cell_cold_c"] == -10.0
    assert inter["v_oc_module_max_cold_v"] == 54.35  # 49.5 * (1 + (-0.0028 * -35)) = 54.35 V
    assert inter["v_oc_module_max_cold_v"] > inputs.v_oc_stc * 1.05

    # 2. Hot Vmp Verification (T_cell = 71.25 C at 40 C amb)
    assert inter["t_cell_hot_c"] == 71.25
    assert abs(inter["v_mp_module_min_hot_v"] - 34.52) <= 0.02  # 41.2 * (1 + (-0.0035 * 46.25)) = 34.53 V
