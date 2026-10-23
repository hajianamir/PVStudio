"""
calc_recommender: Central vs. String Inverter Architecture Topology Recommender
Per Technical Specification §2.3, §4.4 Module 1 & Phase 3 Scope
Recommends CENTRAL vs. STRING inverter topology based on plant capacity (>=3.0 MW threshold),
terrain slope variance (>=5.0° threshold), and LCOE CAPEX delta threshold (5.0%).
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class TopologyRecommenderInput(BaseModel):
    plant_capacity_kw: float = Field(..., gt=0, description="Total plant AC capacity [kW]")
    terrain_slope_variance_deg: float = Field(default=2.0, ge=0, description="Terrain slope variance [deg]")
    unit_capex_string_usd_w: float = Field(default=0.38, gt=0, description="String inverter CAPEX [$/W]")
    unit_capex_central_usd_w: float = Field(default=0.32, gt=0, description="Central inverter CAPEX [$/W]")
    capex_switch_threshold_percent: float = Field(default=5.0, ge=0, description="LCOE/CAPEX delta threshold to trigger architecture switch [%]")
    profile_id: str = Field(default="US-NEC-2020-v1")


def recommend_inverter_topology(inputs: TopologyRecommenderInput) -> CalculationResult:
    """
    Explicit Utility-Scale Topology Decision Rules:
      Rule 1: Plant capacity < 3,000 kW (3 MW) -> STRING_INVERTER (modular installation)
      Rule 2: Terrain slope variance >= 5.0° -> STRING_INVERTER (decentralized MPPT optimization)
      Rule 3: Plant capacity >= 3,000 kW AND terrain slope < 5.0° AND CAPEX delta > 5.0% -> CENTRAL_INVERTER (containerized skid economy of scale)
    """
    p_mw = inputs.plant_capacity_kw / 1000.0
    capex_delta_percent = ((inputs.unit_capex_string_usd_w - inputs.unit_capex_central_usd_w) / inputs.unit_capex_central_usd_w) * 100.0

    if p_mw < 3.0:
        recommended_architecture = "STRING_INVERTER"
        confidence_score = 0.92
        rule_applied = "RULE_1_SUB_3MW_MODULAR"
        justification = "Rule 1: Sub-3MW plant capacity favors decentralized string inverter modularity and lower installation overhead."
    elif inputs.terrain_slope_variance_deg >= 5.0:
        recommended_architecture = "STRING_INVERTER"
        confidence_score = 0.95
        rule_applied = "RULE_2_STEEP_TERRAIN_MPPT"
        justification = "Rule 2: Terrain slope variance >= 5.0° favors string inverters to mitigate inter-row shading and non-uniform tilt mismatch via multi-MPPT tracking."
    elif capex_delta_percent >= inputs.capex_switch_threshold_percent:
        recommended_architecture = "CENTRAL_INVERTER"
        confidence_score = 0.96
        rule_applied = "RULE_3_LARGE_FLAT_CAPEX_SAVINGS"
        justification = f"Rule 3: Plant capacity >= 3MW ({p_mw:.1f} MW), flat terrain ({inputs.terrain_slope_variance_deg:.1f}°), and CAPEX savings >= 5.0% ({capex_delta_percent:.1f}%) favor containerized central inverter skid stations."
    else:
        recommended_architecture = "STRING_INVERTER"
        confidence_score = 0.88
        rule_applied = "RULE_4_MARGINAL_CAPEX_DELTA_STRING_DEFAULT"
        justification = "Rule 4: Marginal CAPEX savings (< 5.0%) default to string architecture for O&M flexibility."

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
        "rule_applied": rule_applied,
        "justification": justification,
        "is_engineer_override_permitted": True,
        "capex_delta_percent": round(capex_delta_percent, 2),
        "decision_thresholds_applied": {
            "capacity_threshold_mw": 3.0,
            "slope_variance_threshold_deg": 5.0,
            "capex_switch_threshold_percent": inputs.capex_switch_threshold_percent
        }
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
