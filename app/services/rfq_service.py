"""
Procurement & RFQ Generator Service for Phase 2 Sprint 4
Per Technical Specification §2.2 & Sprint 4 Scope
Generates C&I design BOM exports, line-item unit/total cost estimations, and supplier RFQ packages.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class RFQRequestInput(BaseModel):
    project_id: str = Field(..., description="Unique C&I project ID")
    project_name: str = Field(..., description="Project Title")
    plant_capacity_kw: float = Field(..., gt=0)
    inverter_model: str = Field(default="Huawei SUN2000-100KTL-M2")
    inverter_count: int = Field(default=7)
    transformer_model: str = Field(default="Schneider Trihal 1000kVA 0.8/33kV")
    switchgear_model: str = Field(default="ABB SafeRing 36kV 630A CCV Ring Main Unit")
    currency_symbol: str = Field(default="€")


class ProcurementRFQOutput(BaseModel):
    project_id: str
    project_name: str
    bom_line_items: List[Dict[str, Any]]
    total_estimated_capex: float
    currency_symbol: str
    rfq_document_text: str


class ProcurementRFQService:
    @staticmethod
    def generate_procurement_rfq(inputs: RFQRequestInput) -> ProcurementRFQOutput:
        module_qty = round(inputs.plant_capacity_kw * 1000 / 405)

        bom_line_items = [
            {
                "line_no": 1,
                "category": "PV_MODULES",
                "description": "Jinko / Trina 405W TOPCon N-type Monocrystalline PV Modules",
                "quantity": module_qty,
                "unit": "PCS",
                "estimated_unit_cost": 85.0,
                "estimated_total_cost": round(module_qty * 85.0, 2)
            },
            {
                "line_no": 2,
                "category": "INVERTERS",
                "description": f"Three-Phase String Inverters ({inputs.inverter_model})",
                "quantity": inputs.inverter_count,
                "unit": "UNITS",
                "estimated_unit_cost": 4200.0,
                "estimated_total_cost": round(inputs.inverter_count * 4200.0, 2)
            },
            {
                "line_no": 3,
                "category": "TRANSFORMER",
                "description": f"LV/MV Step-Up Transformer ({inputs.transformer_model})",
                "quantity": 1,
                "unit": "UNIT",
                "estimated_unit_cost": 28000.0,
                "estimated_total_cost": 28000.0
            },
            {
                "line_no": 4,
                "category": "SWITCHGEAR",
                "description": f"MV Switchgear Ring Main Unit ({inputs.switchgear_model})",
                "quantity": 1,
                "unit": "UNIT",
                "estimated_unit_cost": 18500.0,
                "estimated_total_cost": 18500.0
            },
            {
                "line_no": 5,
                "category": "CABLES_CONTAINMENT",
                "description": "33kV XLPE 3-Core MV AC Collection Cable & Cable Trays",
                "quantity": 250,
                "unit": "METERS",
                "estimated_unit_cost": 45.0,
                "estimated_total_cost": 11250.0
            },
            {
                "line_no": 6,
                "category": "CIVIL_FOUNDATIONS",
                "description": "Substation Pad, Foundation Concrete, and Grounding Mesh",
                "quantity": 1,
                "unit": "LOT",
                "estimated_unit_cost": 14500.0,
                "estimated_total_cost": 14500.0
            }
        ]

        total_capex = sum(item["estimated_total_cost"] for item in bom_line_items)

        rfq_text = f"""REQUEST FOR QUOTATION (RFQ) — C&I SOLAR EQUIPMENT
Project Name: {inputs.project_name} (ID: {inputs.project_id})
Plant Capacity: {inputs.plant_capacity_kw:.1f} kW AC
Generated via PVStudio Procurement Engine

EQUIPMENT SPECIFICATION SUMMARY:
- PV Modules: {module_qty}x 405W TOPCon N-type
- Inverters: {inputs.inverter_count}x {inputs.inverter_model}
- Step-Up Transformer: 1x {inputs.transformer_model}
- MV Switchgear: 1x {inputs.switchgear_model}

TOTAL ESTIMATED CAPEX: {inputs.currency_symbol}{total_capex:,.2f}

SUBMISSION INSTRUCTIONS:
Please submit line-item unit pricing, delivery lead times, and warranty certificates to procurement@pvstudio.io within 10 business days."""

        return ProcurementRFQOutput(
            project_id=inputs.project_id,
            project_name=inputs.project_name,
            bom_line_items=bom_line_items,
            total_estimated_capex=total_capex,
            currency_symbol=inputs.currency_symbol,
            rfq_document_text=rfq_text
        )
