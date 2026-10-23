"""
C&I Workflow Navigation & Step Definition Service
Per Technical Specification §2.2 & Sprint 3 Scope
Extends menu tree to 9 explicit steps including Step 9: Permit Package Generation.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class WorkflowStepItem(BaseModel):
    step_index: int
    step_id: str
    label: str
    required: bool = True


class CommercialIndustrialWorkflowTree(BaseModel):
    segment: str = Field(default="COMMERCIAL_INDUSTRIAL")
    total_steps: int = 9
    workflow_steps: List[WorkflowStepItem] = Field(default_factory=list)


CAND_I_WORKFLOW_STEPS: List[Dict[str, Any]] = [
    {"step_index": 1, "step_id": "site_geospatial", "label": "Site & Geospatial Capture", "required": True},
    {"step_index": 2, "step_id": "cand_i_3d_layout", "label": "3D Roof/Ground Layout & Shading", "required": True},
    {"step_index": 3, "step_id": "cand_i_string_inverter_config", "label": "String & Inverter Configuration", "required": True},
    {"step_index": 4, "step_id": "ac_collection_protection", "label": "AC Collection & Protection Design", "required": True},
    {"step_index": 5, "step_id": "interconnection_analysis", "label": "Interconnection Point Analysis", "required": True},
    {"step_index": 6, "step_id": "cand_i_civil_structural", "label": "Civil & Structural Design", "required": True},
    {"step_index": 7, "step_id": "procurement_rfq", "label": "Procurement & RFQ Tracking", "required": True},
    {"step_index": 8, "step_id": "cand_i_financial_model", "label": "C&I Financial & Peak Shaving Model", "required": True},
    {"step_index": 9, "step_id": "cand_i_permit_package", "label": "Permit Package & Engineering SLD Export", "required": True}
]


def get_cand_i_workflow_steps() -> List[Dict[str, Any]]:
    return CAND_I_WORKFLOW_STEPS


def get_cand_i_workflow_tree() -> CommercialIndustrialWorkflowTree:
    items = [WorkflowStepItem(**s) for s in CAND_I_WORKFLOW_STEPS]
    return CommercialIndustrialWorkflowTree(workflow_steps=items)


def validate_cand_i_step_completion(completed_step_ids: List[str]) -> Dict[str, Any]:
    all_required = {step["step_id"] for step in CAND_I_WORKFLOW_STEPS if step["required"]}
    completed_set = set(completed_step_ids)
    missing = all_required - completed_set

    return {
        "is_ready_for_permit_export": len(missing) == 0 or (len(missing) == 1 and "cand_i_permit_package" in missing),
        "total_steps": len(CAND_I_WORKFLOW_STEPS),
        "completed_count": len(completed_set),
        "missing_steps": list(missing)
    }
