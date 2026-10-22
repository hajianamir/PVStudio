"""
C&I Market Segment Distinct 8-Step Workflow Menu Tree Architecture
Per Technical Specification §2.2 & §7.1 (Distinct from Residential 5-Step Flow)
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class WorkflowStep(BaseModel):
    step_number: int
    step_id: str
    title: str
    description: str
    is_completed: bool = False
    required_inputs: List[str]


class CommercialIndustrialWorkflowTree(BaseModel):
    segment: str = "COMMERCIAL_INDUSTRIAL"
    total_steps: int = 8
    workflow_steps: List[WorkflowStep] = [
        WorkflowStep(
            step_number=1,
            step_id="site_geospatial",
            title="1. Site & Geospatial Analysis",
            description="Property boundary import, terrain contours, keep-out zones, roof/ground plane drawing.",
            required_inputs=["boundary_polygon", "keepout_zones", "dem_raster"]
        ),
        WorkflowStep(
            step_number=2,
            step_id="3d_layout",
            title="2. 3D Roof / Ground Array Layout",
            description="Commercial row-spacing optimization, pitch/azimuth, cable tray routes, equipment pads.",
            required_inputs=["row_spacing_m", "module_selection", "pad_locations"]
        ),
        WorkflowStep(
            step_number=3,
            step_id="string_inverter_config",
            title="3. String & 3-Phase Inverter Configuration",
            description="3-Phase string inverter sizing (50-250 kW), multi-MPPT allocation, string routing.",
            required_inputs=["inverter_selection_3phase", "strings_per_mppt"]
        ),
        WorkflowStep(
            step_number=4,
            step_id="ac_collection_protection",
            title="4. AC Collection & Protection Coordination",
            description="LV/MV cable schedules, pad-mounted transformer sizing (0.8/33 kV), breaker coordination.",
            required_inputs=["transformer_selection", "cable_schedule_ac", "breaker_ratings"]
        ),
        WorkflowStep(
            step_number=5,
            step_id="interconnection_analysis",
            title="5. Interconnection Point Analysis (PCC)",
            description="Short-circuit fault current (Ik''), MV feeder bay count auto-sizing, VDE/IEEE grid compliance.",
            required_inputs=["pcc_voltage_kv", "grid_impedance_ohm"]
        ),
        WorkflowStep(
            step_number=6,
            step_id="civil_structural",
            title="6. Civil, Structural & Foundation Sizing",
            description="Wind uplift (Eurocode 1 / ASCE 7-16), pile embedment depth, access road grading.",
            required_inputs=["wind_speed_m_s", "soil_skin_friction_kPa"]
        ),
        WorkflowStep(
            step_number=7,
            step_id="procurement_rfq",
            title="7. Procurement & RFQ Management",
            description="Verified BOQ generation, RFQ package export, supplier submission tracking.",
            required_inputs=["boq_items", "supplier_list"]
        ),
        WorkflowStep(
            step_number=8,
            step_id="cand_i_financial_model",
            title="8. C&I Financial Model & Permit Package",
            description="Demand-charge peak shaving, IRR, NPV, LCOE, permit-ready 3-line SLD export.",
            required_inputs=["retail_tou_tariff", "demand_charge_usd_kw"]
        )
    ]


def get_cand_i_workflow_tree() -> CommercialIndustrialWorkflowTree:
    """Returns the C&I distinct 8-step workflow object."""
    return CommercialIndustrialWorkflowTree()
