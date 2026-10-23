"""
calc_protection: Profile-Driven LV/MV Breaker, Fuse, Numerical Relay & SPD Selection Package
Per Technical Specification §4.4 Module 5 & Sprint 3 MV Extension
Standards citations are strictly driven by active jurisdiction profile (US UL/IEEE vs EU IEC).
Supports LV breaker/fuse and MV numerical relay coordination, CT/VT sizing, and protection standards.
"""

import math
from typing import Optional
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class ProtectionInput(BaseModel):
    i_sc_stc_a: float = Field(default=13.41, gt=0, description="Module Isc at STC [A]")
    i_ac_nominal_a: float = Field(..., gt=0, description="Nominal AC inverter or feeder output current [A]")
    parallel_strings: int = Field(default=1, ge=1, description="Number of parallel strings per MPPT")
    voltage_class: str = Field(default="LV", description="LV (<1kV) or MV (>=1kV up to 35kV)")
    profile_id: str = Field(default="US-NEC-2020-v1")


PROFILE_PROTECTION_CITATIONS = {
    "US-NEC-2020-v1": {
        "fuse_standard": "UL 2579 (per NEC 690.9)",
        "breaker_standard": "UL 489 / NEC 240",
        "spd_standard": "UL 1449 Type 1 or Type 2",
        "mv_relay_standard": "IEEE C37.90 / IEEE 242 (Buff Book) / ANSI 50/51/51N",
        "ct_vt_standard": "IEEE C57.13 (Instrument Transformers)"
    },
    "EU-DE-v1": {
        "fuse_standard": "IEC 60269-6 (gPV)",
        "breaker_standard": "IEC 60364-4-43",
        "spd_standard": "IEC 61643-11 Class II",
        "mv_relay_standard": "IEC 60255-151 / VDE-AR-N 4110 / ANSI 50/51/51N",
        "ct_vt_standard": "IEC 61869-2 (Current) / IEC 61869-3 (Voltage)"
    }
}


def calculate_protection(inputs: ProtectionInput) -> CalculationResult:
    citations = PROFILE_PROTECTION_CITATIONS.get(inputs.profile_id, PROFILE_PROTECTION_CITATIONS["US-NEC-2020-v1"])

    is_mv = inputs.voltage_class.upper() == "MV"

    is_dc_fuse_required = inputs.parallel_strings >= 3
    recommended_fuse_rating_a = round(inputs.i_sc_stc_a * 1.56, 1) if is_dc_fuse_required else 0.0

    raw_breaker = inputs.i_ac_nominal_a * 1.25

    if is_mv:
        # MV Switchgear circuit breaker / numerical relay sizing
        standard_mv_breakers = [630, 800, 1250, 1600, 2000, 2500, 3150]
        selected_breaker_a = next((b for b in standard_mv_breakers if b >= raw_breaker), 3150)

        # Instrument transformer CT primary sizing
        standard_ct_primaries = [50, 100, 150, 200, 300, 400, 600, 800, 1000, 1200, 1500, 2000]
        recommended_ct_ratio = f"{next((ct for ct in standard_ct_primaries if ct >= raw_breaker), 2000)}/5A"

        relay_functions = ["50 (Instantaneous Overcurrent)", "51 (Time Overcurrent)", "51N (Earth Fault Overcurrent)", "27/59 (Under/Over Voltage)", "81O/U (Over/Under Frequency)"]
        standards_ref = [citations["mv_relay_standard"], citations["ct_vt_standard"]]
    else:
        standard_lv_breakers = [16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 400, 630]
        selected_breaker_a = next((b for b in standard_lv_breakers if b >= raw_breaker), 630)
        recommended_ct_ratio = "N/A (Direct LV Breaker)"
        relay_functions = ["Thermal-Magnetic / Electronic Trip Unit"]
        standards_ref = [citations["fuse_standard"], citations["breaker_standard"], citations["spd_standard"]]

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_protection",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=standards_ref
    )

    outputs = {
        "voltage_class": inputs.voltage_class.upper(),
        "is_dc_fuse_required": is_dc_fuse_required,
        "recommended_fuse_rating_a": recommended_fuse_rating_a,
        "recommended_ac_breaker_a": selected_breaker_a,
        "recommended_ct_ratio": recommended_ct_ratio,
        "numerical_relay_functions": relay_functions,
        "recommended_spd_type": "TYPE_1_2_COMBINED_MV_SURGE_ARRESTER" if is_mv else "TYPE_2_DC_AND_AC",
        "standard_citations": citations
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
