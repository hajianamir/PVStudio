"""HV Substation Protection Relaying Service (IEEE C37.113 / IEC 60255).

Calculates protection settings for high-voltage transmission interconnects:
- ANSI 21: Distance Protection (Zone 1, Zone 2, Zone 3 impedance reach)
- ANSI 87T: Transformer Differential Protection (Pickup current, Slope 1, Slope 2)
- ANSI 87B: Busbar Differential Protection (High-impedance or low-impedance percentage pickup)
"""

import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash

MODULE_NAME = "calc_hv_protection"
MODULE_VERSION = "1.0.0"

class HVProtectionInputSchema(BaseModel):
    system_voltage_kv: float = Field(default=110.0, description="HV nominal line-to-line voltage in kV (e.g. 110.0, 115.0, 220.0, 400.0)")
    line_length_km: float = Field(default=15.0, description="Transmission line length in km")
    line_impedance_ohm_per_km: float = Field(default=0.38, description="Positive-sequence line impedance in ohms/km")
    ct_primary_ratio: float = Field(default=1200.0, description="Primary rating of CT (e.g. 1200:5 or 1200:1)")
    ct_secondary_ratio: float = Field(default=5.0, description="Secondary rating of CT (5A or 1A)")
    vt_primary_kv: float = Field(default=110.0, description="Primary rating of VT in kV")
    vt_secondary_v: float = Field(default=110.0, description="Secondary rating of VT in Volts")
    transformer_mva: float = Field(default=55.0, description="HV Transformer rating in MVA")
    transformer_impedance_percent: float = Field(default=11.5, description="Transformer short-circuit impedance in %")
    compliance_profile_id: str = Field(default="EU-DE-v1", description="Active compliance profile")

    @field_validator("system_voltage_kv")
    def validate_voltage(cls, v):
        if v <= 0:
            raise ValueError("system_voltage_kv must be > 0")
        return v

def calculate_hv_protection(inputs: HVProtectionInputSchema) -> CalculationResult:
    """Calculates HV Distance (21), Transformer Differential (87T), and Busbar Differential (87B) protection settings."""
    inputs_dict = inputs.model_dump()

    # CT & VT Ratio factors
    ct_ratio = inputs.ct_primary_ratio / inputs.ct_secondary_ratio
    vt_ratio = (inputs.vt_primary_kv * 1000.0) / inputs.vt_secondary_v
    impedance_conversion_factor = ct_ratio / vt_ratio

    # Line Total Primary Impedance
    z_line_primary = inputs.line_length_km * inputs.line_impedance_ohm_per_km
    z_line_secondary = z_line_primary * impedance_conversion_factor

    # ANSI 21: Distance Protection Reaches (IEEE C37.113)
    # Zone 1: Instantaneous 80% of line length
    z1_primary_ohms = 0.80 * z_line_primary
    z1_secondary_ohms = z1_primary_ohms * impedance_conversion_factor
    z1_time_delay_sec = 0.00  # Instantaneous

    # Zone 2: 120% of line length (Time delayed)
    z2_primary_ohms = 1.20 * z_line_primary
    z2_secondary_ohms = z2_primary_ohms * impedance_conversion_factor
    z2_time_delay_sec = 0.30  # 300 ms delay

    # Zone 3: 150% of line length (Reverse or remote backup)
    z3_primary_ohms = 1.50 * z_line_primary
    z3_secondary_ohms = z3_primary_ohms * impedance_conversion_factor
    z3_time_delay_sec = 0.80  # 800 ms delay

    # ANSI 87T: Transformer Differential Protection (IEC 60255)
    i_nom_primary = (inputs.transformer_mva * 1000.0) / (1.73205 * inputs.system_voltage_kv)
    pickup_differential_a = 0.20 * (i_nom_primary / ct_ratio) * inputs.ct_secondary_ratio
    slope_1_percent = 25.0  # Normal operation slope (25%)
    slope_2_percent = 60.0  # High fault current CT saturation slope (60%)
    unrestrained_pickup_multiplier = 8.0  # 8x Inom instantaneous trip

    # ANSI 87B: Busbar Differential Protection
    busbar_pickup_a = 0.50 * inputs.ct_secondary_ratio  # 50% CT secondary nominal
    busbar_operation_time_ms = 15.0  # High-speed sub-cycle trip (15 ms)

    outputs = {
        "ct_ratio": ct_ratio,
        "vt_ratio": vt_ratio,
        "impedance_conversion_factor": round(impedance_conversion_factor, 6),
        "z_line_primary_ohms": round(z_line_primary, 3),
        "z_line_secondary_ohms": round(z_line_secondary, 3),
        "ansi_21_distance": {
            "zone_1": {
                "reach_primary_ohms": round(z1_primary_ohms, 3),
                "reach_secondary_ohms": round(z1_secondary_ohms, 3),
                "time_delay_sec": z1_time_delay_sec,
                "reach_percent_line": 80.0
            },
            "zone_2": {
                "reach_primary_ohms": round(z2_primary_ohms, 3),
                "reach_secondary_ohms": round(z2_secondary_ohms, 3),
                "time_delay_sec": z2_time_delay_sec,
                "reach_percent_line": 120.0
            },
            "zone_3": {
                "reach_primary_ohms": round(z3_primary_ohms, 3),
                "reach_secondary_ohms": round(z3_secondary_ohms, 3),
                "time_delay_sec": z3_time_delay_sec,
                "reach_percent_line": 150.0
            }
        },
        "ansi_87t_transformer_differential": {
            "pickup_differential_a": round(pickup_differential_a, 3),
            "slope_1_percent": slope_1_percent,
            "slope_2_percent": slope_2_percent,
            "unrestrained_pickup_a": round(unrestrained_pickup_multiplier * (i_nom_primary / ct_ratio) * inputs.ct_secondary_ratio, 3),
            "standard_citation": "IEC 60255-187-1"
        },
        "ansi_87b_busbar_differential": {
            "pickup_current_a": round(busbar_pickup_a, 3),
            "operation_time_ms": busbar_operation_time_ms,
            "standard_citation": "IEEE C37.234"
        }
    }

    provenance = ProvenanceEnvelope(
        calc_module=MODULE_NAME,
        calc_version=MODULE_VERSION,
        input_hash=compute_input_hash(inputs_dict),
        profile_id=inputs.compliance_profile_id,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
