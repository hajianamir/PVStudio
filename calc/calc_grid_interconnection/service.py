"""
calc_grid_interconnection: C&I Interconnection Point Analysis, Substation Bay Sizing & Short-Circuit Fault Current
Per Technical Specification §4.4 Module 8 & Phase 2 Sprint 2 Fixes
Refactored:
  1. Voltage selection threshold is profile-driven (e.g. 250 kW LV ceiling for US, 100 kW for EU-DE).
  2. For sub-threshold LV connections (e.g. 750 kW C&I at 400V or 208V/480V LV), returns is_lv_connection=True,
     panelboard breaker rating, and bay count = 0 / N/A.
  3. For MV connections (>= MV ceiling), computes component bay breakdown: incomer_bays + transformer_bays + metering_bays + spare_bays.
  4. Standard citations split into Interconnection Requirements (IEEE 1547 / VDE 4110) and Short-Circuit Calculation Methodology (IEEE 141 / IEC 60909).
"""

import math
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash

GRID_IMPEDANCE_SOURCE_POLICY = "USER_UTILITY_INPUT_WITH_DEFAULT_FALLBACK"

PROFILE_INTERCONNECTION_CONFIGS = {
    "US-NEC-2020-v1": {
        "lv_max_capacity_kw": 250.0,
        "lv_nominal_voltage_kv": 0.48,  # 480V 3-phase LV
        "mv_nominal_voltage_kv": 13.8,  # 13.8 kV US MV distribution
        "interconnection_standard": "IEEE 1547-2018 / UL 1741 SB / NEC Article 705",
        "short_circuit_methodology_standard": "IEEE 141 (Red Book) / IEEE 242 (Buff Book)"
    },
    "EU-DE-v1": {
        "lv_max_capacity_kw": 100.0,
        "lv_nominal_voltage_kv": 0.40,  # 400V 3-phase LV
        "mv_nominal_voltage_kv": 33.0,  # 33 kV EU MV grid
        "interconnection_standard": "VDE-AR-N 4110 (MV) / VDE-AR-N 4120 (HV) / EN 50549-2",
        "short_circuit_methodology_standard": "IEC 60909 (Short-Circuit Calculation) / IEC 60947"
    }
}


class InterconnectionInput(BaseModel):
    plant_capacity_kw: float = Field(..., gt=0, description="Total plant AC capacity [kW]")
    bay_max_ampacity_a: float = Field(default=630.0, gt=0, description="Substation bay circuit breaker ampacity [A]")
    grid_impedance_ohm: float = Field(default=0.15, gt=0, description="Upstream grid impedance at PCC [ohm]")
    is_grid_impedance_assumed: bool = Field(default=True, description="True if default impedance fallback used")
    spare_bays_requested: int = Field(default=1, ge=0, description="Number of spare substation bays")
    power_factor: float = Field(default=0.95, ge=0.8, le=1.0)
    profile_id: str = Field(default="US-NEC-2020-v1")


def calculate_grid_interconnection(inputs: InterconnectionInput) -> CalculationResult:
    config = PROFILE_INTERCONNECTION_CONFIGS.get(inputs.profile_id, PROFILE_INTERCONNECTION_CONFIGS["US-NEC-2020-v1"])

    p_kw = inputs.plant_capacity_kw
    lv_ceiling_kw = config["lv_max_capacity_kw"]

    # 1. Profile-Driven Voltage Level Determination
    if p_kw <= lv_ceiling_kw:
        is_lv_connection = True
        recommended_voltage_kv = config["lv_nominal_voltage_kv"]
        voltage_class = f"LV_{recommended_voltage_kv}kV"
    elif p_kw <= 20000.0:
        is_lv_connection = False
        recommended_voltage_kv = config["mv_nominal_voltage_kv"]
        voltage_class = f"MV_{recommended_voltage_kv}kV"
    else:
        is_lv_connection = False
        recommended_voltage_kv = 110.0
        voltage_class = "HV_110kV"

    # 2. Total AC Current at Interconnection Voltage
    i_ac_interconnection_a = (p_kw * 1000.0) / (math.sqrt(3) * (recommended_voltage_kv * 1000.0) * inputs.power_factor)

    # 3. Substation Bay Count vs LV Panelboard Sizing
    if is_lv_connection:
        bay_breakdown = {
            "incomer_bays": 0,
            "transformer_bays": 0,
            "metering_bays": 0,
            "spare_bays": 0,
            "total_substation_bays": 0,
            "note": "LV Connection: Substation bays N/A. Sized via LV main breaker and panelboard."
        }
        total_substation_bays = 0
        lv_main_breaker_rating_a = math.ceil(i_ac_interconnection_a * 1.25)
    else:
        incomer_bays_required = math.ceil(i_ac_interconnection_a / inputs.bay_max_ampacity_a)
        transformer_bays = 1 if recommended_voltage_kv >= 11.0 else 0
        metering_bays = 1
        spare_bays = inputs.spare_bays_requested
        total_substation_bays = incomer_bays_required + transformer_bays + metering_bays + spare_bays
        bay_breakdown = {
            "incomer_bays": incomer_bays_required,
            "transformer_bays": transformer_bays,
            "metering_bays": metering_bays,
            "spare_bays": spare_bays,
            "total_substation_bays": total_substation_bays
        }
        lv_main_breaker_rating_a = 0

    # 4. Short-Circuit Fault Current Contribution at PCC (Ik'')
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
        standards_referenced=[config["interconnection_standard"], config["short_circuit_methodology_standard"]]
    )

    outputs = {
        "is_lv_connection": is_lv_connection,
        "recommended_voltage_kv": recommended_voltage_kv,
        "voltage_class": voltage_class,
        "interconnection_current_a": round(i_ac_interconnection_a, 2),
        "lv_main_breaker_rating_a": lv_main_breaker_rating_a if is_lv_connection else None,
        "bay_breakdown": bay_breakdown,
        "total_substation_bays": total_substation_bays,
        "short_circuit_fault_current_ka": round(i_fault_ka, 2),
        "grid_impedance_source_policy": GRID_IMPEDANCE_SOURCE_POLICY,
        "requires_utility_data_verification": inputs.is_grid_impedance_assumed,
        "standards_citations": {
            "interconnection_standard": config["interconnection_standard"],
            "short_circuit_methodology_standard": config["short_circuit_methodology_standard"]
        }
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
