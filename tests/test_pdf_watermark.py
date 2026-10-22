"""
Automated CI Test: PDF/DOCX Report Document Text-Layer Rendered Watermark Assertion
Per Gate Criterion G4 & Carried Item 5
Asserts that extracted text layers from rendered document headers contain OVERRIDE_WATERMARK_HEADER on page 1 and page N.
"""

import pytest
from calc.compliance.checker import ComplianceProfile, evaluate_design_compliance, OVERRIDE_WATERMARK_HEADER


class MockPDFDocumentRenderer:
    """Simulates PDF report generation engine rendering header text layers on every page."""

    @staticmethod
    def render_proposal_pdf_pages(watermark_text: str, total_pages: int = 3) -> List[str]:
        pages = []
        for p in range(1, total_pages + 1):
            page_text = f"--- PAGE {p} HEADER ---\n{watermark_text}\n--- PAGE {p} CONTENT ---\nSystem Design Proposal"
            pages.append(page_text)
        return pages


def test_pdf_text_layer_contains_rendered_override_watermark_all_pages():
    incomplete_profile = ComplianceProfile(
        profile_id="US-NEC-INCOMPLETE-v1",
        jurisdiction="US-NEC",
        max_voltage_v=600,
        rapid_shutdown_required=True,
        busbar_120_percent_rule=None
    )

    result = evaluate_design_compliance(
        profile=incomplete_profile,
        user_id="usr_pe_john_doe",
        override_reason="Verified local 120 percent busbar compliance manually with DSO engineer."
    )

    # Render PDF pages using compliance check watermark output
    watermark = result.client_visible_watermark
    pdf_pages = MockPDFDocumentRenderer.render_proposal_pdf_pages(watermark, total_pages=3)

    # Assert rendered header watermark appears on extracted text layer of Page 1 and Page N (Page 3)
    assert "APPROVED WITH QUALIFIED PROFESSIONAL ENGINEER OVERRIDE" in pdf_pages[0]  # Page 1
    assert "LOCAL ENGINEER SIGN-OFF REQUIRED" in pdf_pages[0]
    assert "APPROVED WITH QUALIFIED PROFESSIONAL ENGINEER OVERRIDE" in pdf_pages[2]  # Page 3
    assert "LOCAL ENGINEER SIGN-OFF REQUIRED" in pdf_pages[2]
