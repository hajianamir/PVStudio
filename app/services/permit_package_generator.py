"""
Permit Package Generator Service for Step 9 C&I Workflow
Per Technical Specification §2.2 & Sprint 3 Scope
Generates SLD metadata (single line / three line diagram), BOQ export, civil pad dimensions, and interconnection brief.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class PermitPackageInput(BaseModel):
    project_id: str = Field(..., description="Unique C&I project ID")
    project_name: str = Field(..., description="Project Title")
    plant_capacity_kw: float = Field(..., gt=0)
    profile_id: str = Field(default="US-NEC-2020-v1")
    voltage_class: str = Field(default="MV_13.8kV")
    inverter_model: str = Field(default="SMA Sunny Tripower CORE2 110kW")
    inverter_count: int = Field(default=7)
    transformer_model: str = Field(default="Schneider Trihal Cast Resin Transformer 1000kVA")
    switchgear_model: str = Field(default="ABB SafeRing 36kV 630A CCV Ring Main Unit")


class PermitPackageOutput(BaseModel):
    project_id: str
    project_name: str
    sld_metadata: Dict[str, Any]
    boq_export: List[Dict[str, Any]]
    civil_structural_brief: Dict[str, Any]
    interconnection_brief: Dict[str, Any]


class PermitPackageGeneratorService:
    @staticmethod
    def generate_permit_package(inputs: PermitPackageInput) -> PermitPackageOutput:
        # 1. Single-Line Diagram (SLD) Schema Structure
        sld_metadata = {
            "diagram_type": "SINGLE_LINE_DIAGRAM_AND_THREE_LINE_SCHEMATIC",
            "voltage_levels": {
                "dc_string_v": 1000.0,
                "ac_inverter_output_v": 400.0,
                "ac_grid_interconnection_kv": inputs.voltage_class
            },
            "nodes": [
                {"id": "NODE_PV_STRINGS", "label": f"{inputs.inverter_count * 10} PV Strings (1000V DC)", "type": "DC_GENERATION"},
                {"id": "NODE_INVERTERS", "label": f"{inputs.inverter_count}x {inputs.inverter_model}", "type": "INVERTER_STAGE"},
                {"id": "NODE_AC_PANEL", "label": "LV AC Combiner Panelboard (400V 3-phase)", "type": "LV_COLLECTION"},
                {"id": "NODE_TRANSFORMER", "label": f"1x {inputs.transformer_model}", "type": "LV_MV_STEP_UP"},
                {"id": "NODE_SWITCHGEAR", "label": f"1x {inputs.switchgear_model}", "type": "MV_SWITCHGEAR_PCC"},
                {"id": "NODE_UTILITY_POI", "label": "Utility Point of Interconnection (POI)", "type": "GRID_INTERFACE"}
            ],
            "protection_relays_mapped": ["ANSI 50/51/51N (Overcurrent & Earth Fault)", "ANSI 27/59 (Voltage)", "ANSI 81O/U (Frequency)"]
        }

        # 2. Bill of Quantities (BOQ) Export
        boq_export = [
            {"item_no": "1.1", "description": "PV Modules 405W TOPCon N-type", "quantity": round(inputs.plant_capacity_kw * 1000 / 405), "unit": "PCS"},
            {"item_no": "2.1", "description": f"Three-Phase String Inverters ({inputs.inverter_model})", "quantity": inputs.inverter_count, "unit": "UNITS"},
            {"item_no": "3.1", "description": f"LV/MV Step-Up Transformer ({inputs.transformer_model})", "quantity": 1, "unit": "UNIT"},
            {"item_no": "4.1", "description": f"MV Switchgear Ring Main Unit ({inputs.switchgear_model})", "quantity": 1, "unit": "UNIT"},
            {"item_no": "5.1", "description": "33kV XLPE 3-Core MV AC Collection Cable (70mm2)", "quantity": 250, "unit": "METERS"},
            {"item_no": "6.1", "description": "Substation Grounding Grid & Copper Earth Rod Network", "quantity": 1, "unit": "LOT"}
        ]

        # 3. Civil / Structural Pad Brief
        civil_structural_brief = {
            "transformer_pad_dimensions_m": {"length": 3.5, "width": 2.5, "thickness": 0.3},
            "switchgear_kiosk_pad_m": {"length": 4.0, "width": 2.0, "thickness": 0.3},
            "cable_trench_depth_m": 1.0,
            "containment_bunding_liters": 1500.0,
            "foundation_concrete_grade": "C30/37 per EN 206"
        }

        # 4. Interconnection Brief
        interconnection_brief = {
            "interconnection_voltage": inputs.voltage_class,
            "nominal_plant_capacity_kw": inputs.plant_capacity_kw,
            "short_circuit_capacity_ka": 20.0,
            "grid_code_compliance_citations": ["IEEE 1547-2018 / UL 1741 SB" if "US" in inputs.profile_id else "VDE-AR-N 4110 (Mittelspannung)"],
            "requires_utility_witness_testing": True
        }

        return PermitPackageOutput(
            project_id=inputs.project_id,
            project_name=inputs.project_name,
            sld_metadata=sld_metadata,
            boq_export=boq_export,
            civil_structural_brief=civil_structural_brief,
            interconnection_brief=interconnection_brief
        )
