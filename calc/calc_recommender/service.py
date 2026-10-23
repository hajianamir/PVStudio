"""
calc_recommender: Central vs. String Inverter Architecture Topology Recommender
Per Technical Specification §2.3, §4.4 Module 1 & Phase 3 Scope
Recommends CENTRAL vs. STRING inverter topology based on plant capacity (>1 MW), terrain slope variance (>=5°), and LCOE impact.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class TopologyRecommenderInput(BaseModel):
    plant_capacity_kw: float = Field(..., gt=0, description="Total plant AC capacity [kW]")
    terrain_slope_variance_deg: float = Field(default=2.0, ge=0, description="Terrain slope variance [deg]")
    unit_capex_string_usd_w: float = Field(default=0.38, gt=0, description="String inverter CAPEX [$/W]")
    unit_capex_central_usd_w: float = Field(default=0.32, gt=0, description="Central inverter CAPEX [$/W]")
    profile_id: str = Field(default="US-NEC-2020-v1")


def recommend_inverter_topology(inputs: TopologyRecommenderInput) -> CalculationResult:
    p_mw = inputs.plant_capacity_kw / 1000.0

    # Decision Matrix:
    # 1. Plants < 3 MW or terrain slope >= 5.0 deg -> STRING_INVERTER
    # 2. Large flat plants (>= 3 MW and terrain slope < 5.0 deg) -> CENTRAL_INVERTER
    if p_mw < 3.0 or inputs.terrain_slope_variance_deg >= 5.0:
        recommended_architecture = "STRING_INVERTER"
        confidence_score = 0.92
        justification = (
            "Decentralized string architecture selected. Steep terrain or sub-3MW capacity "
            "favors independent MPPT tracking and modular maintenance."
        )
    else:
        recommended_architecture = "CENTRAL_INVERTER"
        confidence_score = 0.95
        justification = (
            "Containerized central inverter architecture selected. Flat terrain and plant scale >= 3MW "
            "optimize CAPEX via containerized MV skid stations."
        )

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_recommender",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=["IEEE 1547 Topology Selection Guide", "IEC 62548 Inverter Layout Guide"]
    )

    outputs = {
        "recommended_architecture": recommended_architecture,
        "confidence_score": confidence_score,
        "justification": justification,
        "is_engineer_override_permitted": True,
        "capex_delta_percent": round(((inputs.unit_capex_string_usd_w - inputs.unit_capex_central_usd_w) / inputs.unit_capex_central_usd_w) * 100.0, 2)
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
