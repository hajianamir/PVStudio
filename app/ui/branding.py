"""
White-Label Branding UI & Report Renderer Component
Per Technical Specification §5.3, Gate Criterion G6 & Sprint 6 Scope
Renders custom company branding (company_name, logo_url, primary_color_hex, footer) into proposal layouts.
"""

from typing import Dict, Any
from app.schemas.report import BrandingConfig


class WhiteLabelBrandingRenderer:
    @staticmethod
    def render_branded_header_html(config: BrandingConfig) -> str:
        """
        Renders HTML header component formatted with enterprise branding config.
        """
        logo_html = f'<img src="{config.logo_url}" alt="{config.company_name} Logo" class="brand-logo" />' if config.logo_url else ""

        return f"""
<div class="brand-header" style="border-bottom: 3px solid {config.primary_color_hex}; padding: 12px;">
    {logo_html}
    <h1 style="color: {config.primary_color_hex}; font-family: Inter, sans-serif;">{config.company_name}</h1>
    <p class="disclaimer" style="font-size: 0.8rem; color: #64748B;">{config.footer_disclaimer_text}</p>
</div>
""".strip()
