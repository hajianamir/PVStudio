"""
calc_electrical_ac: LV/MV AC Collection Cable Sizing, Transformer Sizing & Voltage Drop Package
Per Technical Specification §4.4 Module 4 & Sprint 3 Scope
Calculates LV AC cable sizing, 3-phase MV collection cables, transformer kVA sizing, and AC voltage drop.
"""

import math
from typing import Optional
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class ACElectricalInput(BaseModel):
    p_ac_kw: float = Field(..., gt=0, description="Inverter or collector rated AC power [kW]")
    v_ac_nominal_v: float = Field(default=230.0, gt=0, description="Nominal AC line voltage [V or kV if voltage_class=MV]")
    cable_length_m: float = Field(..., gt=0, description="AC cable run length [m]")
    phases: int = Field(default=1, description="1 for single-phase, 3 for three-phase")
    power_factor: float = Field(default=0.95, ge=0.8, le=1.0)
    voltage_class: str = Field(default="LV", description="LV (<1kV) or MV (>=1kV up to 35kV)")
    profile_id: str = Field(default="US-NEC-2020-v1")


def calculate_ac_electrical(inputs: ACElectricalInput) -> CalculationResult:
    # 1. Determine voltage in Volts
    v_volts = inputs.v_ac_nominal_v if inputs.v_ac_nominal_v >= 100.0 else inputs.v_ac_nominal_v * 1000.0

    # 2. Current calculation
    if inputs.phases == 3:
        i_ac_a = (inputs.p_ac_kw * 1000.0) / (math.sqrt(3) * v_volts * inputs.power_factor)
    else:
        i_ac_a = (inputs.p_ac_kw * 1000.0) / (v_volts * inputs.power_factor)

    # 3. Required ampacity (1.25 continuous load multiplier per NEC/IEC)
    required_ampacity_a = i_ac_a * 1.25

    # 4. Cable section selection
    if inputs.voltage_class.upper() == "MV":
        # Standard MV XLPE 3-core copper cable sizes [mm2]
        mv_cable_table = [(70, 220.0), (95, 260.0), (120, 300.0), (150, 340.0), (185, 390.0), (240, 460.0), (300, 520.0), (400, 600.0)]
        selected_mm2 = next((size for size, amp in mv_cable_table if amp >= required_ampacity_a), 400.0)
        transformer_kva_recommended = math.ceil((inputs.p_ac_kw / inputs.power_factor) / 50.0) * 50.0
        rho = 0.0178  # Copper resistivity
    else:
        standard_lv_sizes = [(1.5, 16.0), (2.5, 25.0), (4.0, 32.0), (6.0, 40.0), (10.0, 55.0), (16.0, 75.0), (25.0, 100.0), (35.0, 125.0), (50.0, 155.0), (70.0, 195.0), (95.0, 240.0), (120.0, 280.0), (150.0, 320.0), (185.0, 365.0), (240.0, 430.0)]
        selected_mm2 = next((size for size, amp in standard_lv_sizes if amp >= required_ampacity_a), 240.0)
        transformer_kva_recommended = 0.0
        rho = 0.0178

    multiplier = 2.0 if inputs.phases == 1 else math.sqrt(3)
    v_drop_volts = (multiplier * inputs.cable_length_m * i_ac_a * rho) / selected_mm2
    v_drop_percent = (v_drop_volts / v_volts) * 100.0

    standards = ["IEEE 141 (AC Feeder Sizing)", "NEC Article 705 / IEC 60364-5-52"] if inputs.voltage_class.upper() == "MV" else ["NEC 2020 Article 705.12", "IEC 60364-4-43"]

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_electrical_ac",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=standards
    )

    outputs = {
        "i_ac_nominal_a": round(i_ac_a, 2),
        "required_ampacity_a": round(required_ampacity_a, 2),
        "selected_cable_mm2": selected_mm2,
        "voltage_class": inputs.voltage_class.upper(),
        "transformer_kva_recommended": transformer_kva_recommended,
        "voltage_drop_volts": round(v_drop_volts, 2),
        "voltage_drop_percent": round(v_drop_percent, 2),
        "is_compliant": v_drop_percent <= 1.5
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
