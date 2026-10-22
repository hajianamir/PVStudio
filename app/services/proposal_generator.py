"""
Proposal Generator Service
Per Technical Specification §5.3 & Gate Criteria G5/G6
Generates proposal HTML/PDF text layers responding dynamically to SectionToggles, BrandingConfig, Weather Metadata, and 3D Viewport Embed.
"""

from typing import Dict, Any
from app.schemas.report import ReportConfig
from calc.weather.service import DatasetMetadata, WEATHER_SOURCE_POLICY


class ProposalGeneratorService:
    @staticmethod
    def generate_proposal_text_layer(
        project_data: Dict[str, Any],
        calc_results: Dict[str, Any],
        weather_meta: DatasetMetadata,
        report_config: ReportConfig,
        watermark_header: str = "",
        embedded_3d_viewport_image_b64: str = ""
    ) -> Dict[str, Any]:
        """
        Generates document text layer rendering section toggles, white-label branding,
        G5 weather metadata, and embedded 3D roof viewport screenshots.
        """
        sections_rendered = []

        # 1. Header & Watermark (Printed on Page 1 and Page N)
        header_text = f"=== {report_config.branding_config.company_name.upper()} PROPOSAL ==="
        if watermark_header:
            header_text += f"\n{watermark_header}"

        # 2. Section Toggles Dynamic Rendering
        toggles = report_config.section_toggles

        if toggles.include_executive_summary:
            sections_rendered.append("SECTION 1: Executive Summary & System Overview")

        if toggles.include_3d_roof_layout:
            viewport_embed_text = " [3D R3F VIEWPORT EMBEDDED]" if embedded_3d_viewport_image_b64 else ""
            sections_rendered.append(f"SECTION 2: 3D Roof Layout & Shading Heatmap Overlay{viewport_embed_text}")

        if toggles.include_system_bill_of_materials:
            sections_rendered.append("SECTION 3: System Bill of Materials (BOM)")

        if toggles.include_electrical_sld:
            sections_rendered.append("SECTION 4: LV Single-Line Diagram (SLD) & Protection")

        if toggles.include_financial_cashflow:
            sections_rendered.append("SECTION 5: 25-Year Financial Cashflow & LCOE Analysis")

        if toggles.include_compliance_checklist:
            sections_rendered.append("SECTION 6: Jurisdictional Regulatory Compliance Checklist")

        # 3. G5 Weather Metadata Block (Mandatory Printed Block)
        weather_block = f"""
WEATHER DATASET METADATA (GATE CRITERION G5 STAMP):
- Provider Name: {weather_meta.provider_name}
- Vintage Range: {weather_meta.vintage_year_range}
- Spatial Resolution: {weather_meta.spatial_resolution}
- User Override Status: {'USER_OVERRIDDEN' if weather_meta.is_user_override else 'DEFAULT'}
- Weather Policy Applied: {weather_meta.policy_applied}
- Divergence Flagged: {weather_meta.divergence_flagged}
"""

        # 4. Standard Citations Block
        standards_text = f"Compliance Profile: {project_data.get('profile_id', 'US-NEC-2020-v1')}"

        return {
            "document_header": header_text,
            "branding_company_name": report_config.branding_config.company_name,
            "sections_rendered_count": len(sections_rendered),
            "sections_list": sections_rendered,
            "weather_metadata_stamp": weather_block.strip(),
            "standards_text": standards_text,
            "has_embedded_3d_viewport": bool(embedded_3d_viewport_image_b64),
            "page_1_text_layer": f"{header_text}\n{weather_block.strip()}\n{sections_rendered[0] if sections_rendered else ''}",
            "page_n_text_layer": f"{header_text}\n{sections_rendered[-1] if sections_rendered else ''}"
        }
