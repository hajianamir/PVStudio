"""
Permit Package Generator Service for Step 9 C&I Workflow
Per Technical Specification §2.2 & Sprint 3 Scope
Generates rendered vector SVG Single Line Diagram (SLD), line-item BOQ, civil pad specifications, and interconnection briefs.
Visibly surfaces diagnostic flags (geotech & site-specific wind verification) on SVG diagrams and briefs.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class PermitPackageInput(BaseModel):
    project_id: str = Field(..., description="Unique C&I project ID")
    project_name: str = Field(..., description="Project Title")
    plant_capacity_kw: float = Field(..., gt=0)
    profile_id: str = Field(default="US-NEC-2020-v1")
    voltage_class: str = Field(default="MV_30.0kV")
    inverter_model: str = Field(default="SMA Sunny Tripower CORE2 110kW")
    inverter_count: int = Field(default=7)
    transformer_model: str = Field(default="Schneider Trihal Cast Resin Transformer 1000kVA")
    switchgear_model: str = Field(default="ABB SafeRing 36kV 630A CCV Ring Main Unit")
    requires_geotech_verification: bool = Field(default=True, description="Surfaces geotech bearing verification flag")
    requires_site_specific_wind_data: bool = Field(default=True, description="Surfaces wind pressure verification flag")


class PermitPackageOutput(BaseModel):
    project_id: str
    project_name: str
    sld_metadata: Dict[str, Any]
    rendered_sld_svg: str = Field(..., description="Rendered engineering Vector SVG Single-Line Diagram for AHJ submission")
    boq_export: List[Dict[str, Any]]
    civil_structural_brief: Dict[str, Any]
    interconnection_brief: Dict[str, Any]


class PermitPackageGeneratorService:
    @staticmethod
    def _render_vector_sld_svg(
        project_name: str,
        plant_capacity_kw: float,
        voltage_class: str,
        inverter_count: int,
        inverter_model: str,
        requires_geotech_verification: bool = True,
        requires_site_specific_wind_data: bool = True
    ) -> str:
        """
        Renders an engineering vector SVG Single-Line Diagram for AHJ permit submission
        with visible diagnostic warning banners.
        """
        geotech_warning = " [NOTICE: GEOTECHNICAL SOIL BEARING VERIFICATION REQUIRED PRIOR TO CONSTRUCTION]" if requires_geotech_verification else ""
        wind_warning = " [NOTICE: SITE-SPECIFIC WIND PRESSURE DATA VERIFICATION REQUIRED]" if requires_site_specific_wind_data else ""

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 650" width="100%" height="100%">
  <style>
    .title {{ font-family: sans-serif; font-weight: bold; font-size: 18px; fill: #0f172a; }}
    .subtitle {{ font-family: sans-serif; font-size: 12px; fill: #475569; }}
    .warning-banner {{ font-family: sans-serif; font-weight: bold; font-size: 11px; fill: #b91c1c; }}
    .box {{ fill: #f8fafc; stroke: #1e293b; stroke-width: 2; }}
    .bus {{ stroke: #0f172a; stroke-width: 4; }}
    .text {{ font-family: monospace; font-size: 11px; fill: #0f172a; }}
    .symbol {{ fill: none; stroke: #2563eb; stroke-width: 2; }}
  </style>

  <!-- Title Block -->
  <rect x="10" y="10" width="980" height="70" fill="#ffffff" stroke="#cbd5e1" />
  <text x="25" y="32" class="title">SINGLE-LINE DIAGRAM (SLD) — {project_name}</text>
  <text x="25" y="48" class="subtitle">Capacity: {plant_capacity_kw} kW AC | Grid Interconnection: {voltage_class} | Compliance Profile: IEC/IEEE</text>
  <text x="25" y="66" class="warning-banner">{geotech_warning}{wind_warning}</text>

  <!-- PV Array Node -->
  <rect x="50" y="120" width="160" height="80" class="box" />
  <text x="60" y="150" class="text">PV ARRAY STAGE</text>
  <text x="60" y="170" class="text">{inverter_count * 10}x Strings (1000V DC)</text>

  <!-- DC Bus Line -->
  <line x1="210" y1="160" x2="280" y2="160" class="bus" />

  <!-- Inverters Block -->
  <rect x="280" y="120" width="180" height="80" class="box" />
  <text x="290" y="150" class="text">INVERTER BANK</text>
  <text x="290" y="170" class="text">{inverter_count}x {inverter_model}</text>

  <!-- AC Collection Bus (400V) -->
  <line x1="460" y1="160" x2="540" y2="160" class="bus" />

  <!-- LV/MV Step-Up Transformer -->
  <rect x="540" y="120" width="160" height="80" class="box" />
  <circle cx="600" cy="160" r="20" class="symbol" />
  <circle cx="640" cy="160" r="20" class="symbol" />
  <text x="550" y="190" class="text">LV/MV Transformer</text>

  <!-- MV Bus (30kV / 13.8kV) -->
  <line x1="700" y1="160" x2="780" y2="160" class="bus" />

  <!-- MV Switchgear / PCC Breaker -->
  <rect x="780" y="120" width="160" height="80" class="box" />
  <text x="790" y="150" class="text">MV SWITCHGEAR</text>
  <text x="790" y="170" class="text">Relay: ANSI 50/51/51N</text>

  <!-- Utility Interconnection Arrow -->
  <line x1="940" y1="160" x2="980" y2="160" class="bus" />
  <polygon points="980,155 990,160 980,165" fill="#0f172a" />
</svg>"""
        return svg

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

        # Rendered vector SVG diagram
        rendered_sld_svg = PermitPackageGeneratorService._render_vector_sld_svg(
            project_name=inputs.project_name,
            plant_capacity_kw=inputs.plant_capacity_kw,
            voltage_class=inputs.voltage_class,
            inverter_count=inputs.inverter_count,
            inverter_model=inputs.inverter_model,
            requires_geotech_verification=inputs.requires_geotech_verification,
            requires_site_specific_wind_data=inputs.requires_site_specific_wind_data
        )

        # 2. Bill of Quantities (BOQ) Export
        boq_export = [
            {"item_no": "1.1", "description": "PV Modules 405W TOPCon N-type", "quantity": round(inputs.plant_capacity_kw * 1000 / 405), "unit": "PCS"},
            {"item_no": "2.1", "description": f"Three-Phase String Inverters ({inputs.inverter_model})", "quantity": inputs.inverter_count, "unit": "UNITS"},
            {"item_no": "3.1", "description": f"LV/MV Step-Up Transformer ({inputs.transformer_model})", "quantity": 1, "unit": "UNIT"},
            {"item_no": "4.1", "description": f"MV Switchgear Ring Main Unit ({inputs.switchgear_model})", "quantity": 1, "unit": "UNIT"},
            {"item_no": "5.1", "description": "30kV XLPE 3-Core MV AC Collection Cable (70mm2)", "quantity": 250, "unit": "METERS"},
            {"item_no": "6.1", "description": "Substation Grounding Grid & Copper Earth Rod Network", "quantity": 1, "unit": "LOT"}
        ]

        # 3. Civil / Structural Pad Brief
        civil_structural_brief = {
            "transformer_pad_dimensions_m": {"length": 3.5, "width": 2.5, "thickness": 0.35},
            "switchgear_kiosk_pad_m": {"length": 4.0, "width": 2.0, "thickness": 0.35},
            "cable_trench_depth_m": 1.0,
            "containment_bunding_liters": 1500.0,
            "foundation_concrete_grade": "C30/37 per EN 206",
            "required_field_verifications": [
                "GEOTECHNICAL_SOIL_BEARING_PRESSURE_VERIFICATION",
                "SITE_SPECIFIC_WIND_PRESSURE_VERIFICATION"
            ]
        }

        # 4. Interconnection Brief
        interconnection_brief = {
            "interconnection_voltage": inputs.voltage_class,
            "nominal_plant_capacity_kw": inputs.plant_capacity_kw,
            "short_circuit_capacity_ka": 20.0,
            "grid_code_compliance_citations": ["IEEE 1547-2018 / UL 1741 SB" if "US" in inputs.profile_id else "VDE-AR-N 4110 (Mittelspannung)"],
            "requires_utility_witness_testing": True,
            "visible_warning_notices": [
                "FOUNDATION DESIGN ASSUMES 150 kPa BEARING CAPACITY — GEOTECHNICAL VERIFICATION REQUIRED PRIOR TO CONSTRUCTION",
                "WIND PRESSURE ASSUMES DEFAULT 0.75 kPa — SITE-SPECIFIC WIND DATA VERIFICATION REQUIRED"
            ]
        }

        return PermitPackageOutput(
            project_id=inputs.project_id,
            project_name=inputs.project_name,
            sld_metadata=sld_metadata,
            rendered_sld_svg=rendered_sld_svg,
            boq_export=boq_export,
            civil_structural_brief=civil_structural_brief,
            interconnection_brief=interconnection_brief
        )
