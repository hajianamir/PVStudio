"""
Automated CI Test: G6 White-Label Branding UI & PDF Component Test
Per Technical Specification §5.3, Gate Criterion G6 & Sprint 6 Scope
Asserts that company_name, primary_color_hex, and logo_url render dynamically in proposal headers.
"""

import pytest
from app.schemas.report import BrandingConfig, ReportConfig
from app.ui.branding import WhiteLabelBrandingRenderer
from app.services.proposal_generator import ProposalGeneratorService
from calc.weather.service import PVGISProvider


def test_whitelabel_branding_renderer_html():
    config = BrandingConfig(
        company_name="Apex Solar Systems",
        logo_url="https://apexsolar.com/logo.png",
        primary_color_hex="#1e40af",
        footer_disclaimer_text="Custom Legal Disclaimer"
    )

    rendered_html = WhiteLabelBrandingRenderer.render_branded_header_html(config)

    assert "Apex Solar Systems" in rendered_html
    assert "https://apexsolar.com/logo.png" in rendered_html
    assert "#1e40af" in rendered_html
    assert "Custom Legal Disclaimer" in rendered_html


def test_whitelabel_branding_proposal_generator_integration():
    pvgis = PVGISProvider()
    weather_meta = pvgis.get_metadata()

    report_config = ReportConfig(
        branding_config=BrandingConfig(
            company_name="Apex Solar Systems",
            primary_color_hex="#1e40af"
        )
    )

    doc = ProposalGeneratorService.generate_proposal_text_layer(
        project_data={"profile_id": "US-NEC-2020-v1"},
        calc_results={},
        weather_meta=weather_meta,
        report_config=report_config
    )

    assert doc["branding_company_name"] == "Apex Solar Systems"
    assert "APEX SOLAR SYSTEMS" in doc["document_header"]
