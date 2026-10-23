"""
calc_civil: C&I Substation Pad, Civil Foundation & Cable Trench Engineering Package
Per Technical Specification §4.4 Module 6 & Sprint 4 Scope
Calculates transformer pad dimensions, concrete volume, wind overturning moments (ASCE 7-16 / Eurocode 1),
soil bearing capacity checks, and cable trench burial depths per NEC 300.5 / IEC 60364-5-52.
Supports explicit geotech and site-specific wind data verification flags.
"""

import math
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class CivilInputSchema(BaseModel):
    equipment_weight_kg: float = Field(default=3500.0, gt=0, description="Equipment dry weight (transformer/switchgear) [kg]")
    equipment_height_m: float = Field(default=2.2, gt=0, description="Equipment total height above pad [m]")
    equipment_width_m: float = Field(default=1.8, gt=0, description="Equipment width [m]")
    equipment_length_m: float = Field(default=2.5, gt=0, description="Equipment length [m]")
    basic_wind_speed_m_s: float = Field(default=35.0, gt=0, description="3-second gust basic wind speed [m/s]")
    is_wind_speed_assumed: bool = Field(default=True, description="True if regional default wind speed used")
    allowable_soil_bearing_capacity_kpa: float = Field(default=150.0, gt=0, description="Allowable soil bearing pressure [kPa]")
    is_soil_bearing_assumed: bool = Field(default=True, description="True if regional default soil bearing pressure used")
    profile_id: str = Field(default="US-NEC-2020-v1")


PROFILE_CIVIL_CITATIONS = {
    "US-NEC-2020-v1": {
        "wind_structural_standard": "ASCE 7-16 / IBC 2021",
        "concrete_standard": "ACI 318-19 (Building Code Requirements for Structural Concrete)",
        "trench_burial_standard": "NEC 2020 Article 300.5 (Table 300.5 Minimum Cover Requirements)"
    },
    "EU-DE-v1": {
        "wind_structural_standard": "Eurocode 1 (EN 1991-1-4 Wind Actions)",
        "concrete_standard": "Eurocode 2 (EN 1992 Design of Concrete Structures)",
        "trench_burial_standard": "IEC 60364-5-52 / DIN VDE 0100-520 (Kabel und Leitungsanlagen)"
    }
}


def calculate_civil_foundations(inputs: CivilInputSchema) -> CalculationResult:
    citations = PROFILE_CIVIL_CITATIONS.get(inputs.profile_id, PROFILE_CIVIL_CITATIONS["US-NEC-2020-v1"])

    # 1. Pad Dimensions Sizing (0.5m clearance margin on length and width)
    pad_length_m = round(inputs.equipment_length_m + 1.0, 2)
    pad_width_m = round(inputs.equipment_width_m + 1.0, 2)
    pad_thickness_m = 0.35  # Standard 350mm reinforced concrete slab

    concrete_volume_m3 = round(pad_length_m * pad_width_m * pad_thickness_m, 2)
    concrete_density_kg_m3 = 2400.0  # Reinforced concrete weight
    pad_weight_kg = concrete_volume_m3 * concrete_density_kg_m3

    total_dead_weight_kg = inputs.equipment_weight_kg + pad_weight_kg
    total_dead_weight_kn = (total_dead_weight_kg * 9.81) / 1000.0

    # 2. Wind Load & Overturning Moment
    air_density = 1.225
    wind_pressure_kpa = (0.5 * air_density * (inputs.basic_wind_speed_m_s ** 2)) / 1000.0
    wind_area_m2 = inputs.equipment_height_m * inputs.equipment_length_m
    total_wind_force_kn = wind_pressure_kpa * wind_area_m2
    overturning_moment_knm = total_wind_force_kn * (inputs.equipment_height_m / 2.0 + pad_thickness_m)

    # 3. Resisting Moment & Safety Factor against Overturning
    resisting_moment_knm = total_dead_weight_kn * (pad_width_m / 2.0)
    overturning_safety_factor = resisting_moment_knm / overturning_moment_knm if overturning_moment_knm > 0 else 99.0

    # 4. Soil Bearing Pressure Check
    pad_area_m2 = pad_length_m * pad_width_m
    applied_soil_pressure_kpa = (total_dead_weight_kn / pad_area_m2) + (6.0 * overturning_moment_knm / (pad_length_m * (pad_width_m ** 2)))
    bearing_capacity_compliant = applied_soil_pressure_kpa <= inputs.allowable_soil_bearing_capacity_kpa

    # 5. Cable Trench Sizing (0.8m depth for LV, 1.0m depth for MV under roads/pads)
    recommended_trench_depth_m = 1.0 if "MV" in inputs.profile_id or "EU" in inputs.profile_id else 0.8
    recommended_trench_width_m = 0.6  # Standard 600mm trench width

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_civil",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=[citations["wind_structural_standard"], citations["concrete_standard"], citations["trench_burial_standard"]]
    )

    outputs = {
        "pad_dimensions_m": {
            "length": pad_length_m,
            "width": pad_width_m,
            "thickness": pad_thickness_m
        },
        "concrete_volume_m3": concrete_volume_m3,
        "pad_weight_kg": round(pad_weight_kg, 1),
        "total_dead_weight_kn": round(total_dead_weight_kn, 2),
        "wind_pressure_kpa": round(wind_pressure_kpa, 3),
        "overturning_moment_knm": round(overturning_moment_knm, 2),
        "resisting_moment_knm": round(resisting_moment_knm, 2),
        "overturning_safety_factor": round(overturning_safety_factor, 2),
        "applied_soil_pressure_kpa": round(applied_soil_pressure_kpa, 2),
        "is_bearing_capacity_compliant": bearing_capacity_compliant,
        "is_overturning_safe": overturning_safety_factor >= 1.5,
        "requires_geotech_verification": inputs.is_soil_bearing_assumed,
        "requires_site_specific_wind_data": inputs.is_wind_speed_assumed,
        "cable_trench_recommendations": {
            "depth_m": recommended_trench_depth_m,
            "width_m": recommended_trench_width_m,
            "warning_tape_depth_m": 0.3
        },
        "standards_citations": citations
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
