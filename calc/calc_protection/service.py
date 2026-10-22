"""
calc_protection: Profile-Driven Breaker, Fuse & SPD Selection Package
Per Technical Specification §4.4 Module 5 & Critical Issue 2 Fix
Standards citations are strictly driven by active jurisdiction profile (US UL vs EU IEC).
"""

from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class ProtectionInput(BaseModel):
    i_sc_stc_a: float = Field(..., gt=0, description="Module Isc at STC [A]")
    i_ac_nominal_a: float = Field(..., gt=0, description="Nominal AC inverter output current [A]")
    parallel_strings: int = Field(default=1, ge=1, description="Number of parallel strings per MPPT")
    profile_id: str = Field(default="US-NEC-2020-v1")


PROFILE_PROTECTION_CITATIONS = {
    "US-NEC-2020-v1": {
        "fuse_standard": "UL 2579 (per NEC 690.9)",
        "breaker_standard": "UL 489 / NEC 240",
        "spd_standard": "UL 1449 Type 1 or Type 2"
    },
    "EU-DE-v1": {
        "fuse_standard": "IEC 60269-6 (gPV)",
        "breaker_standard": "IEC 60364-4-43",
        "spd_standard": "IEC 61643-11 Class II"
    }
}


def calculate_protection(inputs: ProtectionInput) -> CalculationResult:
    citations = PROFILE_PROTECTION_CITATIONS.get(inputs.profile_id, PROFILE_PROTECTION_CITATIONS["US-NEC-2020-v1"])

    is_dc_fuse_required = inputs.parallel_strings >= 3
    recommended_fuse_rating_a = round(inputs.i_sc_stc_a * 1.56, 1) if is_dc_fuse_required else 0.0

    raw_breaker = inputs.i_ac_nominal_a * 1.25
    standard_breakers = [16, 20, 25, 32, 40, 50, 63]
    selected_breaker_a = next((b for b in standard_breakers if b >= raw_breaker), 63)

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_protection",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=[citations["fuse_standard"], citations["breaker_standard"], citations["spd_standard"]]
    )

    outputs = {
        "is_dc_fuse_required": is_dc_fuse_required,
        "recommended_fuse_rating_a": recommended_fuse_rating_a,
        "recommended_ac_breaker_a": selected_breaker_a,
        "recommended_spd_type": "TYPE_2_DC_AND_AC",
        "standard_citations": citations
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
