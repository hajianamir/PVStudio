"""
Automated CI Test: B9 Micro-Inverter Per-Module MPPT Isolation Verification
Per Technical Specification §4.4 & Sprint 4 Clarification 2
Asserts that under micro-inverter architecture, a partially shaded module reduces output only proportionally
(1/N) without string-level series mismatch array collapse.
"""

import pytest
from calc.calc_yield.service import YieldInputSchema, calculate_yield_simulation


def test_micro_inverter_per_module_mppt_isolation():
    # 1. String Inverter with 15% shading -> String mismatch loss applied
    string_inputs = YieldInputSchema(
        capacity_kwp=5.0,
        pitch_deg=30.0,
        azimuth_deg=180.0,
        shading_percent=15.0,
        architecture="STRING"
    )
    string_res = calculate_yield_simulation(string_inputs)

    # 2. Micro Inverter with 15% shading on 1 module -> Shading derate mitigated by ~30%
    micro_inputs = YieldInputSchema(
        capacity_kwp=5.0,
        pitch_deg=30.0,
        azimuth_deg=180.0,
        shading_percent=15.0,
        architecture="MICRO"
    )
    micro_res = calculate_yield_simulation(micro_inputs)

    string_shading_loss = string_res.outputs["losses_breakdown_percent"]["shading"]
    micro_shading_loss = micro_res.outputs["losses_breakdown_percent"]["shading"]

    # Micro-inverter shading loss must be strictly lower than string inverter shading loss
    assert micro_shading_loss < string_shading_loss
    assert micro_shading_loss == 10.5  # 15% * 0.7 = 10.5%
    assert micro_res.outputs["annual_yield_kwh"] > string_res.outputs["annual_yield_kwh"]
