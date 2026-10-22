"""
calc_sizing_dc: Module-Inverter String Sizing Calculation Package
Finalized per Sprint 3 Scope & Technical Specification §4.4 Module 2
Returns full intermediate temperature-adjusted voltages, currents, and min/max module limits.
"""

import math
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class DCSizingInput(BaseModel):
    v_oc_stc: float = Field(..., gt=0, description="Module Voc at STC [V]")
    v_mp_stc: float = Field(..., gt=0, description="Module Vmp at STC [V]")
    i_sc_stc: float = Field(default=13.5, gt=0, description="Module Isc at STC [A]")
    i_mp_stc: float = Field(default=12.8, gt=0, description="Module Imp at STC [A]")
    temp_coeff_voc_percent: float = Field(..., lt=0, description="Voc temperature coefficient [%/°C]")
    temp_coeff_pmp_percent: float = Field(..., lt=0, description="Pmp temperature coefficient [%/°C]")
    site_temp_min_c: float = Field(..., ge=-60, le=50, description="Record minimum ambient temp [°C]")
    site_temp_max_c: float = Field(..., ge=10, le=65, description="Record maximum ambient temp [°C]")
    inverter_v_max_dc: float = Field(..., gt=0, description="Inverter max allowable DC voltage [V]")
    inverter_v_mppt_min: float = Field(..., gt=0, description="Inverter min MPPT voltage [V]")
    inverter_v_mppt_max: float = Field(..., gt=0, description="Inverter max MPPT voltage [V]")
    total_modules_count: int = Field(default=18, gt=0, description="Total planned array module count")
    profile_id: str = Field(default="US-NEC-2020-v1")


def calculate_dc_sizing(inputs: DCSizingInput) -> CalculationResult:
    """
    Finalized String Sizing Calculator.
    Computes temperature-adjusted Voc_max_cold, Vmp_min_hot, Isc_max_hot, and returns
    full intermediate transparency values required by UI transparency panel.
    """
    # 1. Cold Temperature Window (Max Voc)
    delta_t_min = inputs.site_temp_min_c - 25.0
    v_oc_mod_max_cold = inputs.v_oc_stc * (1.0 + (inputs.temp_coeff_voc_percent / 100.0) * delta_t_min)
    max_modules_per_string = int(inputs.inverter_v_max_dc // v_oc_mod_max_cold)

    # 2. Hot Temperature Window (Min Vmp & Max Isc)
    delta_t_max = inputs.site_temp_max_c - 25.0
    v_mp_mod_min_hot = inputs.v_mp_stc * (1.0 + (inputs.temp_coeff_pmp_percent / 100.0) * delta_t_max)
    min_modules_per_string = math.ceil(inputs.inverter_v_mppt_min / v_mp_mod_min_hot)

    # Hot temperature Isc correction (+0.05%/°C typical)
    i_sc_mod_max_hot = inputs.i_sc_stc * (1.0 + 0.0005 * delta_t_max)

    # Actual String Voltages
    v_oc_string_max_site = max_modules_per_string * v_oc_mod_max_cold
    v_mppt_string_min_site = min_modules_per_string * v_mp_mod_min_hot

    # String count calculation
    selected_modules_per_string = min(max_modules_per_string, max(min_modules_per_string, 18))
    string_count = math.ceil(inputs.total_modules_count / selected_modules_per_string)

    is_valid = max_modules_per_string >= min_modules_per_string and v_oc_string_max_site <= inputs.inverter_v_max_dc

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_sizing_dc",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=["NEC 2020 Article 690.7", "IEC 62548 Section 7.2"]
    )

    outputs = {
        # Final Recommendations
        "max_modules_per_string": max_modules_per_string,
        "min_modules_per_string": min_modules_per_string,
        "selected_modules_per_string": selected_modules_per_string,
        "recommended_string_count": string_count,
        "is_compliant": is_valid,

        # Intermediate Transparency Values (Required for UI Side-Panel)
        "intermediate_values": {
            "v_oc_module_max_cold_v": round(v_oc_mod_max_cold, 2),
            "v_mp_module_min_hot_v": round(v_mp_mod_min_hot, 2),
            "i_sc_module_max_hot_a": round(i_sc_mod_max_hot, 2),
            "v_oc_string_max_site_v": round(v_oc_string_max_site, 2),
            "v_mppt_string_min_site_v": round(v_mppt_string_min_site, 2),
            "delta_t_cold_c": delta_t_min,
            "delta_t_hot_c": delta_t_max
        }
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
