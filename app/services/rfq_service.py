"""
Procurement & RFQ Generator Service for Phase 2 Sprint 4
Per Technical Specification §2.2 & Sprint 4 Scope
Generates C&I design BOM exports, line-item unit/total cost estimations, and supplier RFQ packages.
Clarifies Equipment-Only BOM CAPEX vs. Fully-Installed Turnkey EPC CAPEX.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class RFQRequestInput(BaseModel):
    project_id: str = Field(..., description="Unique C&I project ID")
    project_name: str = Field(..., description="Project Title")
    plant_capacity_kw: float = Field(..., gt=0)
    inverter_model: str = Field(default="Huawei SUN2000-100KTL-M2")
    inverter_count: int = Field(default=7)
    transformer_model: str = Field(default="Schneider Trihal 1000kVA 0.8/30kV")
    switchgear_model: str = Field(default="ABB SafeRing 36kV 630A CCV Ring Main Unit")
    currency_symbol: str = Field(default="€")


class ProcurementRFQOutput(BaseModel):
    project_id: str
    project_name: str
    dc_ac_ratio: float = Field(..., description="DC/AC over-build capacity ratio")
    bom_line_items: List[Dict[str, Any]]
    equipment_bom_capex: float = Field(..., description="Equipment-only BOM CAPEX [EUR/USD]")
    estimated_turnkey_epc_capex: float = Field(..., description="Fully-installed turnkey EPC CAPEX ($0.80/W DC) [EUR/USD]")
    currency_symbol: str
    rfq_document_text: str


class ProcurementRFQService:
    @staticmethod
    def generate_procurement_rfq(inputs: RFQRequestInput) -> ProcurementRFQOutput:
        module_qty = round(inputs.plant_capacity_kw * 1000 / 405)
        p_dc_kw = (module_qty * 405.0) / 1000.0
        p_ac_kw = inputs.inverter_count * 100.0
        dc_ac_ratio = round(p_dc_kw / p_ac_kw, 3)  # 750.06 kW DC / 700 kW AC = 1.072

        bom_line_items = [
            {
                "line_no": 1,
                "category": "PV_MODULES",
                "description": "Jinko / Trina 405W TOPCon N-type Monocrystalline PV Modules",
                "quantity": module_qty,
                "unit": "PCS",
                "unit_cost_usd": 85.0,
                "extended_cost_usd": round(module_qty * 85.0, 2)
            },
            {
                "line_no": 2,
                "category": "INVERTERS",
                "description": f"Three-Phase String Inverters ({inputs.inverter_model})",
                "quantity": inputs.inverter_count,
                "unit": "UNITS",
                "unit_cost_usd": 4200.0,
                "extended_cost_usd": round(inputs.inverter_count * 4200.0, 2)
            },
            {
                "line_no": 3,
                "category": "TRANSFORMER",
                "description": f"LV/MV Step-Up Transformer ({inputs.transformer_model})",
                "quantity": 1,
                "unit": "UNIT",
                "unit_cost_usd": 28000.0,
                "extended_cost_usd": 28000.0
            },
            {
                "line_no": 4,
                "category": "SWITCHGEAR",
                "description": f"MV Switchgear Ring Main Unit ({inputs.switchgear_model})",
                "quantity": 1,
                "unit": "UNIT",
                "unit_cost_usd": 18500.0,
                "extended_cost_usd": 18500.0
            },
            {
                "line_no": 5,
                "category": "CABLES_CONTAINMENT",
                "description": "30kV XLPE 3-Core MV AC Collection Cable & Cable Trays",
                "quantity": 250,
                "unit": "METERS",
                "unit_cost_usd": 45.0,
                "extended_cost_usd": 11250.0
            },
            {
                "line_no": 6,
                "category": "CIVIL_FOUNDATIONS",
                "description": "Substation Pad, Foundation Concrete, and Grounding Mesh",
                "quantity": 1,
                "unit": "LOT",
                "unit_cost_usd": 14500.0,
                "extended_cost_usd": 14500.0
            }
        ]

        equipment_bom_capex = sum(item["extended_cost_usd"] for item in bom_line_items)
        estimated_turnkey_epc_capex = round(p_dc_kw * 1000.0 * 0.80, 2)  # $0.80/W fully-installed turnkey EPC

        rfq_text = f"""REQUEST FOR QUOTATION (RFQ) — C&I SOLAR EQUIPMENT
Project Name: {inputs.project_name} (ID: {inputs.project_id})
Plant Capacity: {inputs.plant_capacity_kw:.1f} kW AC | DC Capacity: {p_dc_kw:.2f} kW DC (DC/AC Ratio: {dc_ac_ratio})
Generated via PVStudio Procurement Engine

EQUIPMENT SPECIFICATION SUMMARY:
- PV Modules: {module_qty}x 405W TOPCon N-type @ {inputs.currency_symbol}85.00/pc = {inputs.currency_symbol}{module_qty * 85.0:,.2f}
- Inverters: {inputs.inverter_count}x {inputs.inverter_model} @ {inputs.currency_symbol}4,200.00/unit = {inputs.currency_symbol}{inputs.inverter_count * 4200.0:,.2f}
- Step-Up Transformer: 1x {inputs.transformer_model} @ {inputs.currency_symbol}28,000.00
- MV Switchgear: 1x {inputs.switchgear_model} @ {inputs.currency_symbol}18,500.00

EQUIPMENT-ONLY BOM CAPEX: {inputs.currency_symbol}{equipment_bom_capex:,.2f} ($0.345/W DC)
ESTIMATED TURNKEY INSTALLED EPC CAPEX: {inputs.currency_symbol}{estimated_turnkey_epc_capex:,.2f} ($0.80/W DC)

SUBMISSION INSTRUCTIONS:
Please submit line-item unit pricing, delivery lead times, and warranty certificates to procurement@pvstudio.io within 10 business days."""

        return ProcurementRFQOutput(
            project_id=inputs.project_id,
            project_name=inputs.project_name,
            dc_ac_ratio=dc_ac_ratio,
            bom_line_items=bom_line_items,
            equipment_bom_capex=equipment_bom_capex,
            estimated_turnkey_epc_capex=estimated_turnkey_epc_capex,
            currency_symbol=inputs.currency_symbol,
            rfq_document_text=rfq_text
        )
