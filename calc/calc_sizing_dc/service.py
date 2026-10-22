"""
calc_sizing_dc: Module-Inverter String Sizing Calculation Package
"""

import math
from typing import List
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class DCSizingInput(BaseModel):
    v_oc_stc: float = Field(..., gt=0, description="Module Voc at STC [V]")
    v_mp_stc: float = Field(..., gt=0, description="Module Vmp at STC [V]")
    temp_coeff_voc_percent: float = Field(..., lt=0, description="Voc temperature coefficient [%/°C]")
    temp_coeff_pmp_percent: float = Field(..., lt=0, description="Pmp temperature coefficient [%/°C]")
    site_temp_min_c: float = Field(..., ge=-60, le=50, description="Record minimum ambient temp [°C]")
    site_temp_max_c: float = Field(..., ge=10, le=65, description="Record maximum ambient temp [°C]")
    inverter_v_max_dc: float = Field(..., gt=0, description="Inverter max allowable DC voltage [V]")
    inverter_v_mppt_min: float = Field(..., gt=0, description="Inverter min MPPT voltage [V]")
    inverter_v_mppt_max: float = Field(..., gt=0, description="Inverter max MPPT voltage [V]")
    profile_id: str = Field(default="US-NEC-2020-v1")


def calculate_dc_sizing(inputs: DCSizingInput) -> CalculationResult:
    # 1. Temperature-adjusted Voc at minimum temperature
    delta_t_min = inputs.site_temp_min_c - 25.0
    v_oc_mod_max = inputs.v_oc_stc * (1.0 + (inputs.temp_coeff_voc_percent / 100.0) * delta_t_min)
    max_modules = int(inputs.inverter_v_max_dc // v_oc_mod_max)

    # 2. Temperature-adjusted Vmp at maximum temperature
    delta_t_max = inputs.site_temp_max_c - 25.0
    v_mp_mod_min = inputs.v_mp_stc * (1.0 + (inputs.temp_coeff_pmp_percent / 100.0) * delta_t_max)
    min_modules = math.ceil(inputs.inverter_v_mppt_min / v_mp_mod_min)

    v_oc_max_site = max_modules * v_oc_mod_max
    v_mppt_min_site = min_modules * v_mp_mod_min
    is_valid = max_modules >= min_modules and v_oc_max_site <= inputs.inverter_v_max_dc

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
        "max_modules_per_string": max_modules,
        "min_modules_per_string": min_modules,
        "v_oc_max_site_v": round(v_oc_max_site, 2),
        "v_mppt_min_site_v": round(v_mppt_min_site, 2),
        "is_compliant": is_valid
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
