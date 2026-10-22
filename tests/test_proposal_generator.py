"""
Automated CI Test: Proposal Generator, Section Toggles, 3D Embed & G5 Weather Metadata Wiring Test
Per Technical Specification §5.3 & Gate Criteria G5/G6
Asserts:
  1. SectionToggles dynamically include/exclude sections in rendered document text layers.
  2. G5 Weather Metadata stamp (provider, vintage, resolution, override, policy, divergence) is printed on every generated proposal.
  3. 3D roof viewport screenshot embedding is supported.
"""

import pytest
from app.schemas.report import ReportConfig, SectionToggles, BrandingConfig
from app.services.proposal_generator import ProposalGeneratorService
from calc.weather.service import PVGISProvider


def test_proposal_generator_all_sections_and_weather_metadata():
    pvgis = PVGISProvider()
    weather_meta = pvgis.get_metadata()
    weather_meta.divergence_flagged = True

    config = ReportConfig(
        branding_config=BrandingConfig(company_name="Acme Solar Engineering"),
        section_toggles=SectionToggles(include_financial_cashflow=True, include_3d_roof_layout=True)
    )

    doc_all = ProposalGeneratorService.generate_proposal_text_layer(
        project_data={"profile_id": "US-NEC-2020-v1"},
        calc_results={},
        weather_meta=weather_meta,
        report_config=config,
        watermark_header="APPROVED WITH OVERRIDE",
        embedded_3d_viewport_image_b64="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )

    assert doc_all["branding_company_name"] == "Acme Solar Engineering"
    assert doc_all["sections_rendered_count"] == 6
    assert doc_all["has_embedded_3d_viewport"] is True
    assert "[3D R3F VIEWPORT EMBEDDED]" in doc_all["sections_list"][1]
    assert "WEATHER DATASET METADATA (GATE CRITERION G5 STAMP):" in doc_all["weather_metadata_stamp"]
    assert "Provider Name: PVGIS-ERA5" in doc_all["weather_metadata_stamp"]
    assert "Divergence Flagged: True" in doc_all["weather_metadata_stamp"]
    assert "APPROVED WITH OVERRIDE" in doc_all["page_1_text_layer"]


def test_proposal_generator_section_toggle_disabled():
    pvgis = PVGISProvider()
    weather_meta = pvgis.get_metadata()

    # Disable financial section
    config_disabled = ReportConfig(
        section_toggles=SectionToggles(include_financial_cashflow=False)
    )

    doc_disabled = ProposalGeneratorService.generate_proposal_text_layer(
        project_data={"profile_id": "EU-DE-v1"},
        calc_results={},
        weather_meta=weather_meta,
        report_config=config_disabled
    )

    assert doc_disabled["sections_rendered_count"] == 5
    assert "SECTION 5: 25-Year Financial Cashflow" not in doc_disabled["sections_list"]
