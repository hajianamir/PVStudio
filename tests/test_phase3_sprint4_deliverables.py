"""Unit and Integration Tests for Phase 3 Sprint 4 Deliverables (HV Protection Reference Benchmarks).

Verifies:
1. ANSI 21 Distance Protection Reach settings vs IEEE C37.113 Worked Example.
2. ANSI 87T Transformer Differential Protection settings vs IEEE C37.91 / IEC 60255-187-1.
3. ANSI 87B Busbar Differential Protection settings vs IEEE C37.234.
"""

import pytest
from calc.calc_hv_protection.service import HVProtectionInputSchema, calculate_hv_protection

def test_ansi_21_distance_protection_ieee_c37_113_reference():
    # IEEE C37.113 Worked Example Baseline:
    # 110 kV line, 15 km, 0.38 ohm/km -> Z_primary = 5.70 ohms
    # CT: 1200:5 (ratio 240), VT: 110kV:110V (ratio 1000) -> Conversion factor = 240 / 1000 = 0.24
    inputs = HVProtectionInputSchema(
        system_voltage_kv=110.0,
        line_length_km=15.0,
        line_impedance_ohm_per_km=0.38,
        ct_primary_ratio=1200.0,
        ct_secondary_ratio=5.0,
        vt_primary_kv=110.0,
        vt_secondary_v=110.0
    )
    res = calculate_hv_protection(inputs)
    outputs = res.outputs

    # Primary line impedance
    assert abs(outputs["z_line_primary_ohms"] - 5.70) <= 0.01
    # Secondary line impedance = 5.70 * 0.24 = 1.368 ohms
    assert abs(outputs["z_line_secondary_ohms"] - 1.368) <= 0.01

    dist_21 = outputs["ansi_21_distance"]
    # Zone 1 (80% reach)
    assert abs(dist_21["zone_1"]["reach_primary_ohms"] - 4.56) <= 0.01
    assert abs(dist_21["zone_1"]["reach_secondary_ohms"] - 1.094) <= 0.005
    assert dist_21["zone_1"]["time_delay_sec"] == 0.00

    # Zone 2 (120% reach)
    assert abs(dist_21["zone_2"]["reach_primary_ohms"] - 6.84) <= 0.01
    assert abs(dist_21["zone_2"]["reach_secondary_ohms"] - 1.642) <= 0.005
    assert dist_21["zone_2"]["time_delay_sec"] == 0.30

    # Zone 3 (150% reach)
    assert abs(dist_21["zone_3"]["reach_primary_ohms"] - 8.55) <= 0.01
    assert abs(dist_21["zone_3"]["reach_secondary_ohms"] - 2.052) <= 0.005
    assert dist_21["zone_3"]["time_delay_sec"] == 0.80

def test_ansi_87t_transformer_differential_ieee_c37_91_reference():
    # IEEE C37.91 Worked Example Baseline:
    # 55 MVA 110 kV Transformer -> Inom_primary = 55,000 kVA / (1.73205 * 110 kV) = 288.68 A
    # CT: 1200:5 (ratio 240) -> Secondary nominal current = 288.68 / 240 = 1.203 A
    inputs = HVProtectionInputSchema(
        system_voltage_kv=110.0,
        transformer_mva=55.0,
        ct_primary_ratio=1200.0,
        ct_secondary_ratio=5.0
    )
    res = calculate_hv_protection(inputs)
    diff_87t = res.outputs["ansi_87t_transformer_differential"]

    # Pickup differential threshold (20% of rated secondary)
    assert abs(diff_87t["pickup_differential_a"] - 0.241) <= 0.01
    assert diff_87t["slope_1_percent"] == 25.0
    assert diff_87t["slope_2_percent"] == 60.0
    # Unrestrained high-set instantaneous trip (8x nominal)
    assert abs(diff_87t["unrestrained_pickup_a"] - 9.623) <= 0.05
    assert diff_87t["standard_citation"] == "IEEE C37.91 / IEC 60255-187-1"

def test_ansi_87b_busbar_differential_ieee_c37_234_reference():
    # IEEE C37.234 Worked Example Baseline:
    inputs = HVProtectionInputSchema(ct_secondary_ratio=5.0)
    res = calculate_hv_protection(inputs)
    diff_87b = res.outputs["ansi_87b_busbar_differential"]

    # Busbar differential pickup = 50% CT secondary = 2.5 A
    assert abs(diff_87b["pickup_current_a"] - 2.50) <= 0.01
    assert diff_87b["operation_time_ms"] == 15.0
    assert diff_87b["standard_citation"] == "IEEE C37.234"

def test_ansi_21_dynamic_computation_scaling():
    # Verify line length scaling (30 km vs 15 km line)
    inputs_15km = HVProtectionInputSchema(line_length_km=15.0)
    inputs_30km = HVProtectionInputSchema(line_length_km=30.0)

    res_15 = calculate_hv_protection(inputs_15km)
    res_30 = calculate_hv_protection(inputs_30km)

    # 30 km line impedance must be exactly 2x 15 km line impedance
    assert res_30.outputs["z_line_primary_ohms"] == 2 * res_15.outputs["z_line_primary_ohms"]
    assert res_30.outputs["ansi_21_distance"]["zone_1"]["reach_primary_ohms"] == 2 * res_15.outputs["ansi_21_distance"]["zone_1"]["reach_primary_ohms"]

def test_ansi_87t_and_87b_dynamic_computation_scaling():
    # 87T Scaling Test: 55 MVA vs 110 MVA Transformer
    inputs_55mva = HVProtectionInputSchema(transformer_mva=55.0)
    inputs_110mva = HVProtectionInputSchema(transformer_mva=110.0)

    res_55 = calculate_hv_protection(inputs_55mva)
    res_110 = calculate_hv_protection(inputs_110mva)

    pickup_55 = res_55.outputs["ansi_87t_transformer_differential"]["pickup_differential_a"]
    pickup_110 = res_110.outputs["ansi_87t_transformer_differential"]["pickup_differential_a"]

    # 110 MVA transformer secondary current doubles, pickup doubles
    assert abs(pickup_110 - 2 * pickup_55) <= 0.005

    # 87B Scaling Test: 5A vs 1A CT Secondary Rating
    inputs_ct5a = HVProtectionInputSchema(ct_secondary_ratio=5.0)
    inputs_ct1a = HVProtectionInputSchema(ct_secondary_ratio=1.0)

    res_5a = calculate_hv_protection(inputs_ct5a)
    res_1a = calculate_hv_protection(inputs_ct1a)

    pickup_5a = res_5a.outputs["ansi_87b_busbar_differential"]["pickup_current_a"]
    pickup_1a = res_1a.outputs["ansi_87b_busbar_differential"]["pickup_current_a"]

    # 5A secondary yields 2.5A pickup; 1A secondary yields 0.5A pickup (exactly 5:1 ratio)
    assert pickup_5a == 2.50
    assert pickup_1a == 0.50
    assert pickup_5a == 5 * pickup_1a
