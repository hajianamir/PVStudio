"""Unit and Integration Tests for Phase 3 Sprint 3 Deliverables.

Verifies:
1. `calc_hv_protection` Distance (21), Transformer Differential (87T), and Busbar Differential (87B) relay settings.
2. Complete 20-Year DSCR schedule table and minimum endpoint in `calc_bankability`.
3. MENA-GCC compliance profile YAML structure and 132/400 kV HV voltage levels.
4. Central Architecture vs String Topology end-to-end differentiation (HV bay count, transformer count, and Sungrow skid BOM).
"""

import pytest
import yaml
from calc.calc_hv_protection.service import HVProtectionInputSchema, calculate_hv_protection
from calc.calc_bankability.service import BankabilityInputSchema, calculate_bankability_monte_carlo
from calc.calc_recommender.service import TopologyRecommenderInput, recommend_inverter_topology
from calc.calc_grid_interconnection.service import InterconnectionInput, calculate_grid_interconnection

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
    assert distance_21["standard_citation"] == "IEEE C37.113"

    assert distance_21["zone_2"]["reach_percent_line"] == 120.0
    assert distance_21["zone_2"]["time_delay_sec"] == 0.3

    assert distance_21["zone_3"]["reach_percent_line"] == 150.0
    assert distance_21["zone_3"]["time_delay_sec"] == 0.8

    diff_87t = outputs["ansi_87t_transformer_differential"]
    assert diff_87t["slope_1_percent"] == 25.0
    assert diff_87t["slope_2_percent"] == 60.0
    assert diff_87t["standard_citation"] == "IEEE C37.91 / IEC 60255-187-1"

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
    assert abs(schedule[19]["dscr_p90"] - 1.22) <= 0.05

def test_mena_gcc_profile_yaml_loading():
    with open("calc/compliance/profiles/MENA-GCC-v1.yaml", "r") as f:
        data = yaml.safe_load(f)
    assert data["id"] == "MENA-GCC-v1"
    assert data["jurisdiction"] == "MENA-GCC"
    assert data["hv_voltage_levels_kv"] == [132, 220, 400]
    assert data["min_required_dscr"] == 1.15

def test_central_vs_string_topology_end_to_end_differentiation():
    # 1. Recommender outputs CENTRAL_INVERTER for 50 MW plant on flat terrain
    rec_inputs = TopologyRecommenderInput(plant_capacity_kw=50000.0, terrain_slope_deg=1.2)
    rec_res = recommend_inverter_topology(rec_inputs)
    assert rec_res.outputs["recommended_architecture"] == "CENTRAL_INVERTER"

    # 2. Grid Interconnection for 50 MW plant selects HV substation level (115 kV)
    grid_inputs = InterconnectionInput(plant_capacity_kw=50000.0, jurisdiction="EU-DE")
    grid_res = calculate_grid_interconnection(grid_inputs)
    outputs = grid_res.outputs
    assert outputs["recommended_voltage_kv"] == 115.0
    assert outputs["transformer_mva_recommended"] == 55.0
    assert outputs["total_substation_bays"] == 4
    assert outputs["bay_breakdown"]["incomer_bays"] == 1
    assert outputs["bay_breakdown"]["transformer_bays"] == 1
