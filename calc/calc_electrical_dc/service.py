"""
calc_electrical_dc: DC Cable Sizing, Ampacity & Voltage Drop Package
Per Technical Specification §4.4 Module 3 & Critical Issue 3 Fix
Ampacity factor is strictly profile-driven (e.g. 1.25x for NEC 2020 / IEC 60364-7-712).
"""

from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class DCElectricalInput(BaseModel):
    i_mp_a: float = Field(..., gt=0, description="String Imp current [A]")
    i_sc_a: float = Field(..., gt=0, description="String Isc current [A]")
    cable_length_m: float = Field(..., gt=0, description="One-way DC cable run length [m]")
    nominal_voltage_v: float = Field(..., gt=0, description="Nominal DC string voltage [V]")
    conductor_material: str = Field(default="COPPER", description="COPPER or ALUMINUM")
    profile_id: str = Field(default="US-NEC-2020-v1")


PROFILE_DC_AMPACITY_FACTORS = {
    "US-NEC-2020-v1": {"factor": 1.25, "citation": "NEC 2020 Article 690.8(B)"},
    "US-NEC-2017-v1": {"factor": 1.5625, "citation": "NEC 2017 Article 690.8"},
    "EU-DE-v1": {"factor": 1.25, "citation": "IEC 60364-7-712 Section 712.522"}
}


def calculate_dc_electrical(inputs: DCElectricalInput) -> CalculationResult:
    # Look up profile-driven ampacity factor
    profile_info = PROFILE_DC_AMPACITY_FACTORS.get(inputs.profile_id, PROFILE_DC_AMPACITY_FACTORS["US-NEC-2020-v1"])
    ampacity_factor = profile_info["factor"]
    citation = profile_info["citation"]

    # Profile-driven ampacity requirement
    required_ampacity_a = inputs.i_sc_a * ampacity_factor

    # Select standard cross section (4.0 mm2 or 6.0 mm2 default for residential)
    selected_mm2 = 6.0 if required_ampacity_a > 30.0 else 4.0

    # Resistivity: Copper = 0.0178 ohm*mm2/m, Aluminum = 0.0285
    rho = 0.0178 if inputs.conductor_material.upper() == "COPPER" else 0.0285

    # Voltage drop percentage
    v_drop_volts = (2.0 * inputs.cable_length_m * inputs.i_mp_a * rho) / selected_mm2
    v_drop_percent = (v_drop_volts / inputs.nominal_voltage_v) * 100.0

    is_compliant = v_drop_percent <= 2.0  # Max 2% DC voltage drop threshold

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_electrical_dc",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=[citation]
    )

    outputs = {
        "applied_ampacity_factor": ampacity_factor,
        "standard_reference": citation,
        "required_ampacity_a": round(required_ampacity_a, 2),
        "selected_cable_mm2": selected_mm2,
        "voltage_drop_volts": round(v_drop_volts, 2),
        "voltage_drop_percent": round(v_drop_percent, 2),
        "is_compliant": is_compliant
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
