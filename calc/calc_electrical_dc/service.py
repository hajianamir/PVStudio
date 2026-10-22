"""
calc_electrical_dc: DC Cable Sizing, Ampacity & Voltage Drop Package
Per Technical Specification §4.4 Module 3 & Sprint 3 Scope
Calculates copper/aluminum cable sizing, ampacity derating, and DC voltage drop.
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


def calculate_dc_electrical(inputs: DCElectricalInput) -> CalculationResult:
    # 1. Ampacity requirement (NEC 690.8: 1.25 * 1.25 * Isc = 1.56 * Isc)
    required_ampacity_a = inputs.i_sc_a * 1.56

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
        standards_referenced=["NEC 2020 Article 690.8", "IEC 60364-5-52"]
    )

    outputs = {
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
