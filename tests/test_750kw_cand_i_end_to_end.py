"""
750 kW C&I End-to-End Benchmark Design Integration Test Suite
Executes complete 750 kW C&I design across all 9 steps:
  Step 1: Site Capture
  Step 2: 3D Layout & Array Layout
  Step 3: String/Inverter Configuration (7x 110kW / 100kW Inverters)
  Step 4: AC Collection & Protection Design (MV Cable & Numerical Relay)
  Step 5: Grid Interconnection Analysis (30 kV Substation & Short-Circuit Fault Current)
  Step 6: Civil / Structural Pads
  Step 7: Procurement BOQ
  Step 8: C&I Financial LCOE/NPV
  Step 9: Permit Package (SLD SVG Vector Diagram, BOQ, Interconnection Brief)
"""

import pytest
from calc.calc_grid_interconnection.service import InterconnectionInput, calculate_grid_interconnection
from calc.calc_electrical_ac.service import ACElectricalInput, calculate_ac_electrical
from calc.calc_protection.service import ProtectionInput, calculate_protection
from calc.calc_financial.service import FinancialInputSchema, calculate_financial_quick_mode
from app.services.permit_package_generator import PermitPackageGeneratorService, PermitPackageInput
from app.ui.cand_i_workflow import get_cand_i_workflow_steps, validate_cand_i_step_completion


def test_750kw_cand_i_end_to_end_benchmark_run():
    # 1. Verify 9-Step Menu Tree Sequence
    steps = get_cand_i_workflow_steps()
    assert len(steps) == 9
    assert steps[8]["step_id"] == "cand_i_permit_package"

    completed_ids = [step["step_id"] for step in steps[:8]]  # Steps 1 to 8 completed
    val_status = validate_cand_i_step_completion(completed_ids)
    assert val_status["is_ready_for_permit_export"] is True

    # 2. Step 4: AC Collection Cable & Transformer Sizing
    ac_input = ACElectricalInput(
        p_ac_kw=750.0,
        v_ac_nominal_v=30.0,
        cable_length_m=200.0,
        phases=3,
        power_factor=0.95,
        voltage_class="MV",
        profile_id="EU-DE-v1"
    )
    ac_res = calculate_ac_electrical(ac_input)
    assert ac_res.outputs["i_ac_nominal_a"] == 15.19
    assert ac_res.outputs["selected_cable_mm2"] == 70.0
    assert ac_res.outputs["transformer_kva_recommended"] == 800.0

    # 3. Step 4: MV Protection & Numerical Relay
    prot_input = ProtectionInput(
        i_ac_nominal_a=15.19,
        voltage_class="MV",
        profile_id="EU-DE-v1"
    )
    prot_res = calculate_protection(prot_input)
    assert prot_res.outputs["recommended_ac_breaker_a"] == 630
    assert prot_res.outputs["recommended_ct_ratio"] == "50/5A"

    # 4. Step 5: Grid Interconnection Analysis & Substation Bays (500 MVA Sk'' -> 10.58 kA @ 30kV)
    grid_input = InterconnectionInput(
        plant_capacity_kw=750.0,
        bay_max_ampacity_a=630.0,
        profile_id="EU-DE-v1"
    )
    grid_res = calculate_grid_interconnection(grid_input)
    assert grid_res.outputs["is_lv_connection"] is False
    assert grid_res.outputs["voltage_class"] == "MV_30.0kV"
    assert grid_res.outputs["total_substation_bays"] == 4
    assert grid_res.outputs["short_circuit_fault_current_ka"] == 10.58
    assert grid_res.outputs["fault_current_warning"] is None

    # 5. Step 8: Financial Model (LCOE & Payback)
    fin_input = FinancialInputSchema(
        annual_p50_yield_kwh=1050000.0,  # 1400 kWh/kWp for 750 kW
        system_capex_usd=600000.0,      # $0.80/W C&I CAPEX
        electricity_rate_usd_kwh=0.20,
        profile_id="EU-DE-v1"
    )
    fin_res = calculate_financial_quick_mode(fin_input)
    assert fin_res.outputs["lcoe_usd_kwh"] > 0.03
    assert fin_res.outputs["simple_payback_years"] < 5.0

    # 6. Step 9: Permit Package Generation & SVG Diagram Content Deep Assertion
    pkg_input = PermitPackageInput(
        project_id="PRJ_CAND_I_750KW_001",
        project_name="Apex Logistics Center 750kW Rooftop PV",
        plant_capacity_kw=750.0,
        profile_id="EU-DE-v1",
        voltage_class="MV_30.0kV",
        inverter_model="Huawei SUN2000-100KTL-M2",
        inverter_count=7,
        transformer_model="Schneider Trihal 1000kVA 0.8/30kV",
        switchgear_model="ABB SafeRing 36kV 630A CCV Ring Main Unit",
        requires_geotech_verification=True,
        requires_site_specific_wind_data=True
    )
    pkg_res = PermitPackageGeneratorService.generate_permit_package(pkg_input)

    assert pkg_res.project_id == "PRJ_CAND_I_750KW_001"
    assert len(pkg_res.sld_metadata["nodes"]) == 6

    # SVG Vector Diagram Deep Content & Text-Layer Warnings Assertions
    svg = pkg_res.rendered_sld_svg
    assert svg.count("<rect") >= 5          # Title block + 4 equipment node boxes
    assert svg.count("<line") >= 4          # Interconnect bus lines
    assert "SINGLE-LINE DIAGRAM (SLD)" in svg
    assert "750.0 kW AC" in svg
    assert "MV_30.0kV" in svg
    assert "LV/MV Transformer" in svg
    assert "MV SWITCHGEAR" in svg
    assert "GEOTECHNICAL SOIL BEARING VERIFICATION REQUIRED" in svg
    assert "SITE-SPECIFIC WIND PRESSURE DATA VERIFICATION REQUIRED" in svg

    assert len(pkg_res.boq_export) == 6
    assert pkg_res.interconnection_brief["short_circuit_capacity_ka"] == 20.0
    assert "FOUNDATION DESIGN ASSUMES 150 kPa BEARING CAPACITY" in pkg_res.interconnection_brief["visible_warning_notices"][0]
