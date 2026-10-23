"""
Automated CI Integration Tests for Phase 2 Sprint 4 Core Deliverables
Per Technical Specification §4.4 & Sprint 4 Scope
Asserts:
  - calc_civil pad dimensions, concrete volume, overturning safety factor (>= 1.5), and trench depths
  - ProcurementRFQService BOQ line items and RFQ document generation
  - CandIProposalGeneratorService distinct Client Executive Proposal and AHJ Permit Package sections
"""

import pytest
from calc.calc_civil.service import CivilInputSchema, calculate_civil_foundations
from app.services.rfq_service import ProcurementRFQService, RFQRequestInput
from app.services.cand_i_proposal_generator import CandIProposalGeneratorService, CandIProposalInput


def test_calc_civil_foundation_and_trench_sizing():
    # 750 kW Substation Transformer Pad Sizing (EU-DE)
    inputs = CivilInputSchema(
        equipment_weight_kg=3500.0,
        equipment_height_m=2.2,
        equipment_width_m=1.8,
        equipment_length_m=2.5,
        basic_wind_speed_m_s=35.0,
        allowable_soil_bearing_capacity_kpa=150.0,
        profile_id="EU-DE-v1"
    )
    result = calculate_civil_foundations(inputs)
    outputs = result.outputs

    assert outputs["pad_dimensions_m"]["length"] == 3.5  # 2.5 + 1.0 margin
    assert outputs["pad_dimensions_m"]["width"] == 2.8   # 1.8 + 1.0 margin
    assert outputs["concrete_volume_m3"] == 3.43        # 3.5 * 2.8 * 0.35
    assert outputs["is_overturning_safe"] is True
    assert outputs["overturning_safety_factor"] >= 1.5
    assert outputs["is_bearing_capacity_compliant"] is True
    assert outputs["cable_trench_recommendations"]["depth_m"] == 1.0
    assert "Eurocode 1" in result.provenance.standards_referenced[0]


def test_procurement_rfq_service_generation():
    inputs = RFQRequestInput(
        project_id="PRJ_CAND_I_750KW_001",
        project_name="Apex Logistics Center 750kW Rooftop PV",
        plant_capacity_kw=750.0,
        inverter_model="Huawei SUN2000-100KTL-M2",
        inverter_count=7,
        currency_symbol="€"
    )
    res = ProcurementRFQService.generate_procurement_rfq(inputs)

    assert res.project_id == "PRJ_CAND_I_750KW_001"
    assert len(res.bom_line_items) == 6
    assert res.total_estimated_capex > 200000.0
    assert "REQUEST FOR QUOTATION (RFQ)" in res.rfq_document_text
    assert "Apex Logistics Center" in res.rfq_document_text


def test_cand_i_proposal_booklet_dual_section_generation():
    inputs = CandIProposalInput(
        project_id="PRJ_CAND_I_750KW_001",
        project_name="Apex Logistics Center 750kW Rooftop PV",
        plant_capacity_kw=750.0,
        client_name="Apex Logistics GmbH",
        profile_id="EU-DE-v1",
        lcoe_usd_kwh=0.052,
        payback_years=4.8,
        total_capex=600000.0,
        currency_symbol="€"
    )
    res = CandIProposalGeneratorService.generate_cand_i_proposal_booklet(inputs)

    assert "CLIENT EXECUTIVE PROPOSAL" in res.client_executive_proposal_text
    assert "Apex Logistics GmbH" in res.client_executive_proposal_text
    assert "AHJ PERMIT PACKAGE" in res.ahj_permit_package_section_text
    assert "Eurocode 1" in res.ahj_permit_package_section_text or "IEEE C37.2" in res.ahj_permit_package_section_text or "EU-DE-v1" in res.ahj_permit_package_section_text
