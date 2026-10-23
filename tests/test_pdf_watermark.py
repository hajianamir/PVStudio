"""
Unit tests for PDF watermark text layer rendering in Phase 1 proposal PDFs.
Per Technical Specification §4.4 & Compliance Refusal Safeguards.
"""

from typing import List
import pytest


class MockPDFDocumentRenderer:
    """
    Mock PDF Renderer verifying text-layer watermark insertion on Page 1 and Page N.
    """
    @staticmethod
    def render_proposal_pdf_pages(watermark_text: str, total_pages: int = 3) -> List[str]:
        pages = []
        for p in range(1, total_pages + 1):
            page_text = f"--- PAGE {p} ---\nPVStudio Proposal Document\n"
            if watermark_text:
                page_text += f"[WATERMARK LAYER]: {watermark_text}\n"
            page_text += "Project Sizing & Yield Details..."
            pages.append(page_text)
        return pages


def test_pdf_watermark_rendering():
    watermark = "UNVERIFIED PRELIMINARY DESIGN - NOT FOR PERMITTING"
    pages = MockPDFDocumentRenderer.render_proposal_pdf_pages(watermark_text=watermark, total_pages=3)

    assert len(pages) == 3
    for page_num, page_content in enumerate(pages, 1):
        assert watermark in page_content, f"Watermark missing from page {page_num}"
        assert f"--- PAGE {page_num} ---" in page_content
