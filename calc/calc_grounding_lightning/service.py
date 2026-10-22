"""
calc_grounding_lightning: IEC 62305 / NFPA 780 Lightning Risk & Earthing Sizing
Per Technical Specification §4.4 Module 6 & Item 3 Response
Includes declared Ng (Ground Flash Density) data source provenance policy.
"""

import math
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash

NG_DATA_SOURCE_POLICY = "REGIONAL_MET_SERVICES_OR_VAISALA_GLD360"


class GroundingLightningInput(BaseModel):
    building_length_m: float = Field(default=12.0, gt=0)
    building_width_m: float = Field(default=10.0, gt=0)
    building_height_m: float = Field(default=7.0, gt=0)
    ground_flash_density_ng: float = Field(default=2.0, gt=0, description="Flashes per km2 per year from met service dataset")
    soil_resistivity_ohm_m: float = Field(default=100.0, gt=0, description="Soil resistivity [ohm*m]")
    earth_rod_length_m: float = Field(default=3.0, gt=0, description="Earth rod length [m]")
    profile_id: str = Field(default="EU-DE-v1")


PROFILE_EARTHING_CITATIONS = {
    "US-NEC-2020-v1": {
        "lightning_standard": "NFPA 780 / UL 96A",
        "grounding_standard": "NEC 2020 Article 250"
    },
    "EU-DE-v1": {
        "lightning_standard": "IEC 62305-2 / 62305-3",
        "grounding_standard": "IEC 60364-5-54"
    }
}


def calculate_grounding_lightning(inputs: GroundingLightningInput) -> CalculationResult:
    citations = PROFILE_EARTHING_CITATIONS.get(inputs.profile_id, PROFILE_EARTHING_CITATIONS["EU-DE-v1"])

    l, w, h = inputs.building_length_m, inputs.building_width_m, inputs.building_height_m
    ad = (l * w) + (6.0 * h * (l + w)) + (9.0 * math.pi * (h ** 2))

    nd = inputs.ground_flash_density_ng * ad * 1e-6

    d_m = 0.016
    rg_ohms = (inputs.soil_resistivity_ohm_m / (2.0 * math.pi * inputs.earth_rod_length_m)) * math.log((4.0 * inputs.earth_rod_length_m) / d_m)

    is_compliant = rg_ohms <= 10.0

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_grounding_lightning",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=[citations["lightning_standard"], citations["grounding_standard"]]
    )

    outputs = {
        "ng_data_source_policy": NG_DATA_SOURCE_POLICY,
        "equivalent_collection_area_m2": round(ad, 2),
        "lightning_direct_strikes_per_year": round(nd, 5),
        "earth_rod_resistance_ohms": round(rg_ohms, 2),
        "target_impedance_ohms": 10.0,
        "is_compliant": is_compliant,
        "standard_citations": citations
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
