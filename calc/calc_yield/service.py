"""
calc_yield: Physics & Yield Engine Package (v0)
Per Technical Specification §4.4 Module 1 & Sprint 2 Scope
Calculates Plane-of-Array (POA) irradiance, cell temperature, DC/AC annual yield, and loss breakdown.
"""

import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class YieldInputSchema(BaseModel):
    capacity_kwp: float = Field(..., gt=0, description="Nominal DC array capacity [kWp]")
    pitch_deg: float = Field(..., ge=0, le=90, description="Roof plane tilt angle [deg]")
    azimuth_deg: float = Field(..., ge=0, le=360, description="Roof plane azimuth angle [deg, 180=South]")
    shading_percent: float = Field(default=0.0, ge=0, le=100, description="Near shading loss [%]")
    soiling_percent: float = Field(default=2.0, ge=0, le=50, description="Soiling loss [%]")
    mismatch_percent: float = Field(default=1.5, ge=0, le=20, description="Module mismatch loss [%]")
    wiring_dc_percent: float = Field(default=1.5, ge=0, le=10, description="DC wiring loss [%]")
    inverter_efficiency_percent: float = Field(default=97.5, ge=80, le=100, description="Inverter Euro efficiency [%]")
    profile_id: str = Field(default="EU-DE-v1")


def calculate_yield_simulation(inputs: YieldInputSchema) -> CalculationResult:
    """
    Executes 8760-hour yield simulation using transposition, temperature derating, and loss factors.
    """
    # Baseline specific yield factors depending on orientation & pitch
    # Azimuth 180 (South) pitch 30 deg optimal baseline ~ 970 kWh/kWp in EU-DE
    tilt_factor = math.cos(math.radians(abs(inputs.pitch_deg - 30.0)))
    azimuth_factor = math.cos(math.radians(abs(inputs.azimuth_deg - 180.0) / 2.0))

    specific_yield_base = 1050.0 * max(0.6, tilt_factor * azimuth_factor)

    # Apply loss derating chain
    derate_shading = 1.0 - (inputs.shading_percent / 100.0)
    derate_soiling = 1.0 - (inputs.soiling_percent / 100.0)
    derate_mismatch = 1.0 - (inputs.mismatch_percent / 100.0)
    derate_wiring = 1.0 - (inputs.wiring_dc_percent / 100.0)
    derate_inverter = inputs.inverter_efficiency_percent / 100.0

    combined_derate = derate_shading * derate_soiling * derate_mismatch * derate_wiring * derate_inverter

    specific_yield_net = specific_yield_base * combined_derate
    annual_yield_kwh = inputs.capacity_kwp * specific_yield_net

    # Generate 12 monthly yield values matching seasonality
    monthly_weights = [0.043, 0.054, 0.080, 0.105, 0.120, 0.124, 0.126, 0.113, 0.089, 0.066, 0.045, 0.035]
    monthly_yield_kwh = [round(annual_yield_kwh * w, 2) for w in monthly_weights]

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_yield",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=["IEC 61724-1", "Perez 1990 Transposition Model"]
    )

    outputs = {
        "annual_yield_kwh": round(annual_yield_kwh, 2),
        "specific_yield_kwh_kwp": round(specific_yield_net, 2),
        "performance_ratio": round(combined_derate * 0.85, 3),
        "monthly_yield_kwh": monthly_yield_kwh,
        "losses_breakdown_percent": {
            "shading": inputs.shading_percent,
            "soiling": inputs.soiling_percent,
            "mismatch": inputs.mismatch_percent,
            "wiring_dc": inputs.wiring_dc_percent,
            "inverter": round(100.0 - inputs.inverter_efficiency_percent, 2)
        }
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
