"""Unit and Integration Tests for Phase 3 Sprint 3 Deliverables.

Verifies:
1. `calc_hv_protection` Distance (21), Transformer Differential (87T), and Busbar Differential (87B) relay settings.
2. 20-Year DSCR schedule table completeness and minimum endpoint in `calc_bankability`.
3. MENA-GCC compliance profile YAML structure and 132/400 kV HV voltage levels.
"""

import pytest
import yaml
from calc.calc_hv_protection.service import HVProtectionInputSchema, calculate_hv_protection
from calc.calc_bankability.service import BankabilityInputSchema, calculate_bankability_monte_carlo

def test_hv_protection_calculation():
    inputs = HVProtectionInputSchema(
        system_voltage_kv=110.0,
        line_length_km=15.0,
        line_impedance_ohm_per_km=0.38,
        transformer_mva=55.0,
        compliance_profile_id="EU-DE-v1"
    )
    res = calculate_hv_protection(inputs)
    outputs = res.outputs

    assert outputs["z_line_primary_ohms"] == 5.7
    distance_21 = outputs["ansi_21_distance"]
    assert distance_21["zone_1"]["reach_percent_line"] == 80.0
    assert distance_21["zone_1"]["reach_primary_ohms"] == 4.56
    assert distance_21["zone_1"]["time_delay_sec"] == 0.0

    assert distance_21["zone_2"]["reach_percent_line"] == 120.0
    assert distance_21["zone_2"]["time_delay_sec"] == 0.3

    assert distance_21["zone_3"]["reach_percent_line"] == 150.0
    assert distance_21["zone_3"]["time_delay_sec"] == 0.8

    diff_87t = outputs["ansi_87t_transformer_differential"]
    assert diff_87t["slope_1_percent"] == 25.0
    assert diff_87t["slope_2_percent"] == 60.0
    assert diff_87t["standard_citation"] == "IEC 60255-187-1"

    diff_87b = outputs["ansi_87b_busbar_differential"]
    assert diff_87b["operation_time_ms"] == 15.0
    assert diff_87b["standard_citation"] == "IEEE C37.234"

def test_full_twenty_year_dscr_table_output():
    inputs = BankabilityInputSchema()
    res = calculate_bankability_monte_carlo(inputs)
    schedule = res.outputs["dscr_twenty_year_schedule"]

    assert len(schedule) == 20
    assert schedule[0]["year"] == 1
    assert schedule[19]["year"] == 20
    assert schedule[0]["dscr_p90"] >= 1.20
    assert abs(schedule[19]["dscr_p90"] - 1.20) <= 0.05

def test_mena_gcc_profile_yaml_loading():
    with open("calc/compliance/profiles/MENA-GCC-v1.yaml", "r") as f:
        data = yaml.safe_load(f)
    assert data["id"] == "MENA-GCC-v1"
    assert data["jurisdiction"] == "MENA-GCC"
    assert data["hv_voltage_levels_kv"] == [132, 220, 400]
    assert data["min_required_dscr"] == 1.15
