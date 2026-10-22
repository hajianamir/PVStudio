"""
calc_grid_interconnection: C&I Interconnection Point Analysis, Bay Count & Voltage Sizing
Per Technical Specification §4.4 Module 8 & Phase 2 Sprint 1 Scope
Calculates interconnection voltage level, feeder bay count, and short-circuit fault current with mandatory provenance envelope.
"""

import math
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class InterconnectionInput(BaseModel):
    plant_capacity_kw: float = Field(..., gt=0, description="Total plant AC capacity [kW]")
    bay_max_ampacity_a: float = Field(default=630.0, gt=0, description="Substation bay circuit breaker ampacity [A]")
    grid_impedance_ohm: float = Field(default=0.15, gt=0, description="Upstream grid impedance at PCC [ohm]")
    power_factor: float = Field(default=0.95, ge=0.8, le=1.0)
    profile_id: str = Field(default="US-NEC-2020-v1")


PROFILE_GRID_CITATIONS = {
    "US-NEC-2020-v1": "IEEE 1547-2018 / UL 1741 SB / NEC Article 705",
    "EU-DE-v1": "VDE-AR-N 4110 (MV) / VDE-AR-N 4120 (HV) / EN 50549-2"
}


def calculate_grid_interconnection(inputs: InterconnectionInput) -> CalculationResult:
    citation = PROFILE_GRID_CITATIONS.get(inputs.profile_id, PROFILE_GRID_CITATIONS["US-NEC-2020-v1"])

    # 1. Voltage Level Determination Rule
    p_kw = inputs.plant_capacity_kw
    if p_kw < 250.0:
        recommended_voltage_kv = 0.4  # LV
        voltage_class = "LV_0.4kV"
    elif p_kw <= 20000.0:
        recommended_voltage_kv = 33.0  # MV
        voltage_class = "MV_33kV"
    else:
        recommended_voltage_kv = 110.0  # HV
        voltage_class = "HV_110kV"

    # 2. Total AC Current at Interconnection Voltage
    i_ac_interconnection_a = (p_kw * 1000.0) / (math.sqrt(3) * (recommended_voltage_kv * 1000.0) * inputs.power_factor)

    # 3. Feeder Bay Count Sizing Formula
    feeder_bays_required = math.ceil(i_ac_interconnection_a / inputs.bay_max_ampacity_a)
    total_bays_with_spare = feeder_bays_required + 1  # Mandatory 1 spare bay

    # 4. Short-Circuit Fault Current Contribution at PCC (Ik'')
    # Ik'' = (c * Un) / (sqrt(3) * Z_k)
    c_factor = 1.10
    v_nominal_v = recommended_voltage_kv * 1000.0
    i_fault_ka = (c_factor * v_nominal_v) / (math.sqrt(3) * inputs.grid_impedance_ohm * 1000.0)

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_grid_interconnection",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=[citation]
    )

    outputs = {
        "recommended_voltage_kv": recommended_voltage_kv,
        "voltage_class": voltage_class,
        "interconnection_current_a": round(i_ac_interconnection_a, 2),
        "feeder_bays_required": feeder_bays_required,
        "total_substation_bays": total_bays_with_spare,
        "short_circuit_fault_current_ka": round(i_fault_ka, 2),
        "standard_citation": citation
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
