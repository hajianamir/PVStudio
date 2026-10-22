"""
calc_grid_interconnection: C&I Interconnection Point Analysis, Substation Bay Sizing & Short-Circuit Fault Current
Per Technical Specification §4.4 Module 8 & Sprint 1 Clarifications
Refactored:
  1. Bay count explicitly computes incomer_bays + transformer_bays + metering_bays + spare_bays.
  2. Standard citations split into Interconnection Requirements (IEEE 1547 / VDE 4110) and Short-Circuit Calculation Methodology (IEEE 141 / IEC 60909).
  3. Declared GRID_IMPEDANCE_SOURCE_POLICY with requires_utility_data_verification flag.
"""

import math
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash

GRID_IMPEDANCE_SOURCE_POLICY = "USER_UTILITY_INPUT_WITH_DEFAULT_FALLBACK"


class InterconnectionInput(BaseModel):
    plant_capacity_kw: float = Field(..., gt=0, description="Total plant AC capacity [kW]")
    bay_max_ampacity_a: float = Field(default=630.0, gt=0, description="Substation bay circuit breaker ampacity [A]")
    grid_impedance_ohm: float = Field(default=0.15, gt=0, description="Upstream grid impedance at PCC [ohm]")
    is_grid_impedance_assumed: bool = Field(default=True, description="True if default impedance fallback used")
    spare_bays_requested: int = Field(default=1, ge=0, description="Number of spare substation bays")
    power_factor: float = Field(default=0.95, ge=0.8, le=1.0)
    profile_id: str = Field(default="US-NEC-2020-v1")


PROFILE_GRID_CITATIONS = {
    "US-NEC-2020-v1": {
        "interconnection_standard": "IEEE 1547-2018 / UL 1741 SB / NEC Article 705",
        "short_circuit_methodology_standard": "IEEE 141 (Red Book) / IEEE 242 (Buff Book)"
    },
    "EU-DE-v1": {
        "interconnection_standard": "VDE-AR-N 4110 (MV) / VDE-AR-N 4120 (HV) / EN 50549-2",
        "short_circuit_methodology_standard": "IEC 60909 (Short-Circuit Calculation) / IEC 60947"
    }
}


def calculate_grid_interconnection(inputs: InterconnectionInput) -> CalculationResult:
    citations = PROFILE_GRID_CITATIONS.get(inputs.profile_id, PROFILE_GRID_CITATIONS["US-NEC-2020-v1"])

    # 1. Voltage Level Determination Rule
    p_kw = inputs.plant_capacity_kw
    if p_kw < 250.0:
        recommended_voltage_kv = 0.4
        voltage_class = "LV_0.4kV"
    elif p_kw <= 20000.0:
        recommended_voltage_kv = 33.0
        voltage_class = "MV_33kV"
    else:
        recommended_voltage_kv = 110.0
        voltage_class = "HV_110kV"

    # 2. Total AC Current at Interconnection Voltage
    i_ac_interconnection_a = (p_kw * 1000.0) / (math.sqrt(3) * (recommended_voltage_kv * 1000.0) * inputs.power_factor)

    # 3. Substation Bay Count Component Breakdown
    incomer_bays_required = math.ceil(i_ac_interconnection_a / inputs.bay_max_ampacity_a)
    transformer_bays = 1 if recommended_voltage_kv >= 11.0 else 0
    metering_bays = 1
    spare_bays = inputs.spare_bays_requested

    total_substation_bays = incomer_bays_required + transformer_bays + metering_bays + spare_bays

    # 4. Short-Circuit Fault Current Contribution at PCC (Ik'') per IEEE 141 / IEC 60909
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
        standards_referenced=[citations["interconnection_standard"], citations["short_circuit_methodology_standard"]]
    )

    outputs = {
        "recommended_voltage_kv": recommended_voltage_kv,
        "voltage_class": voltage_class,
        "interconnection_current_a": round(i_ac_interconnection_a, 2),
        "bay_breakdown": {
            "incomer_bays": incomer_bays_required,
            "transformer_bays": transformer_bays,
            "metering_bays": metering_bays,
            "spare_bays": spare_bays,
            "total_substation_bays": total_substation_bays
        },
        "total_substation_bays": total_substation_bays,
        "short_circuit_fault_current_ka": round(i_fault_ka, 2),
        "grid_impedance_source_policy": GRID_IMPEDANCE_SOURCE_POLICY,
        "requires_utility_data_verification": inputs.is_grid_impedance_assumed,
        "standards_citations": citations
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
