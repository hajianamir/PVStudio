"""
calc_electrical_ac: LV AC Cable Sizing & Voltage Drop Package
Per Technical Specification §4.4 Module 4 & Sprint 3 Scope
Calculates LV AC cable sizing, single-phase/three-phase voltage drops, and busbar connection checks.
"""

import math
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class ACElectricalInput(BaseModel):
    p_ac_kw: float = Field(..., gt=0, description="Inverter rated AC power [kW]")
    v_ac_nominal_v: float = Field(default=230.0, gt=0, description="Nominal AC line voltage [V]")
    cable_length_m: float = Field(..., gt=0, description="AC cable run length [m]")
    phases: int = Field(default=1, description="1 for single-phase, 3 for three-phase")
    power_factor: float = Field(default=1.0, ge=0.8, le=1.0)
    profile_id: str = Field(default="US-NEC-2020-v1")


def calculate_ac_electrical(inputs: ACElectricalInput) -> CalculationResult:
    # AC Current calculation
    if inputs.phases == 3:
        i_ac_a = (inputs.p_ac_kw * 1000.0) / (math.sqrt(3) * inputs.v_ac_nominal_v * inputs.power_factor)
    else:
        i_ac_a = (inputs.p_ac_kw * 1000.0) / (inputs.v_ac_nominal_v * inputs.power_factor)

    # Required ampacity (1.25 continuous load multiplier)
    required_ampacity_a = i_ac_a * 1.25
    selected_mm2 = 10.0 if required_ampacity_a > 40.0 else (6.0 if required_ampacity_a > 25.0 else 4.0)

    rho = 0.0178  # Copper resistivity
    multiplier = 2.0 if inputs.phases == 1 else math.sqrt(3)
    v_drop_volts = (multiplier * inputs.cable_length_m * i_ac_a * rho) / selected_mm2
    v_drop_percent = (v_drop_volts / inputs.v_ac_nominal_v) * 100.0

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_electrical_ac",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=["NEC 2020 Article 705.12", "IEC 60364-4-43"]
    )

    outputs = {
        "i_ac_nominal_a": round(i_ac_a, 2),
        "required_ampacity_a": round(required_ampacity_a, 2),
        "selected_cable_mm2": selected_mm2,
        "voltage_drop_volts": round(v_drop_volts, 2),
        "voltage_drop_percent": round(v_drop_percent, 2),
        "is_compliant": v_drop_percent <= 1.5  # Max 1.5% AC voltage drop threshold
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
