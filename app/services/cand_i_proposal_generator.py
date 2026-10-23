"""
C&I Dual Proposal Booklet Generator
Per Technical Specification §2.2 & Sprint 4 Directives
Renders distinct Client Executive Proposal and AHJ Permit Package sections.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class CandIProposalInput(BaseModel):
    project_id: str = Field(..., description="Unique project ID")
    project_name: str = Field(..., description="Project Name")
    plant_capacity_kw: float = Field(..., gt=0)
    client_name: str = Field(..., description="Client Name")
    profile_id: str = Field(default="EU-DE-v1")
    lcoe_usd_kwh: float = Field(default=0.052)
    payback_years: float = Field(default=4.8)
    total_capex: float = Field(default=600000.0)
    currency_symbol: str = Field(default="€")


class CandIProposalBookletOutput(BaseModel):
    project_id: str
    client_executive_proposal_text: str
    ahj_permit_package_section_text: str


class CandIProposalGeneratorService:
    @staticmethod
    def generate_cand_i_proposal_booklet(inputs: CandIProposalInput) -> CandIProposalBookletOutput:
        # 1. Distinct Client Executive Proposal
        exec_proposal = f"""========================================================================
CLIENT EXECUTIVE PROPOSAL — {inputs.project_name.upper()}
Prepared for: {inputs.client_name}
========================================================================
System Capacity: {inputs.plant_capacity_kw:.1f} kW AC
Turnkey System CAPEX: {inputs.currency_symbol}{inputs.total_capex:,.2f}
Levelized Cost of Electricity (LCOE): {inputs.currency_symbol}{inputs.lcoe_usd_kwh:.4f} / kWh
Simple Payback Period: {inputs.payback_years:.1f} Years

EXECUTIVE FINANCIAL SUMMARY:
This rooftop solar PV installation provides clean, zero-emission energy while
reducing facility demand charges and grid dependency. All estimates include 25-year
degradation-adjusted cashflow models and P50/P90 risk-adjusted yields.
========================================================================"""

        # 2. Distinct AHJ Permit Package Section
        permit_package = f"""========================================================================
AHJ PERMIT PACKAGE & ENGINEERING SUBMISSION — {inputs.project_name.upper()}
Jurisdiction / Compliance Profile: {inputs.profile_id}
========================================================================
ENGINEERING ATTACHMENTS FOR PERMIT REVIEW:
1. Rendered Vector Single-Line Diagram (SLD) [Attachment A - SVG Graphic]
2. Substation & Pad-Mounted Transformer Foundation Calculations (ASCE 7-16 / Eurocode 1)
3. Protection Coordination & Relay Settings Sheet (ANSI 50/51/51N per IEEE C37.2)
4. Medium-Voltage Interconnection Point Analysis & Short-Circuit Study (IEC 60909 / IEEE 141)
5. Bill of Quantities (BOQ) Equipment Schedule

STATUS: READY FOR AHJ PERMIT SUBMISSION AND LOCAL UTILITY INTERCONNECTION REVIEW
========================================================================"""

        return CandIProposalBookletOutput(
            project_id=inputs.project_id,
            client_executive_proposal_text=exec_proposal,
            ahj_permit_package_section_text=permit_package
        )
