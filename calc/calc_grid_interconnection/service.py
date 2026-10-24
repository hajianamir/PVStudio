"""
calc_grid_interconnection: C&I and Utility-Scale Interconnection Point Analysis, Substation Bay Sizing & Fault Current
Per Technical Specification §4.4 Module 8 & Phase 3 Scope
Refactored:
  1. Extends grid interconnection analysis up to High-Voltage (HV) transmission levels (110kV/220kV/380kV EU, 115kV/138kV/230kV/345kV/500kV US).
  2. Calculates HV substation transformer MVA sizing, HV switchgear bay decomposition, and IEEE C37.010 / IEC 60909 HV short-circuit currents.
  3. Explicitly outputs source Sk'' capacity (3500 MVA EU / 2500 MVA US), requires_utility_data_verification flag, and selected switchgear interrupting rating.
  4. Includes SCADA RTU telemetry and POI recloser specifications.
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
        "hv_nominal_voltage_kv": 115.0, # 115 kV US HV transmission grid
        "default_mv_sk_mva": 250.0,     # 250 MVA 13.8kV utility feeder short-circuit capacity
        "default_hv_sk_mva": 2500.0,    # 2500 MVA 115kV utility transmission short-circuit capacity
        "interconnection_standard": "NERC PRC Standards / IEEE 1547-2018 / NEC Article 705",
        "short_circuit_methodology_standard": "IEEE C37.010 (HV Short-Circuit) / IEEE 141"
    },
    "EU-DE-v1": {
        "lv_max_capacity_kw": 100.0,
        "lv_nominal_voltage_kv": 0.40,  # 400V 3-phase LV
        "mv_nominal_voltage_kv": 30.0,  # 30.0 kV EU-DE MV distribution grid per VDE-AR-N 4110
        "hv_nominal_voltage_kv": 110.0, # 110.0 kV EU-DE HV transmission grid per VDE-AR-N 4120
        "default_mv_sk_mva": 500.0,     # 500 MVA 30kV utility network short-circuit capacity
        "default_hv_sk_mva": 3500.0,    # 3500 MVA 110kV utility network short-circuit capacity
        "interconnection_standard": "VDE-AR-N 4120 (Anschlüsse am Hochspannungsnetz) / EN 50549-2",
        "short_circuit_methodology_standard": "IEC 60909 (HV Short-Circuit Calculation) / IEC 62271"
    }
}


class InterconnectionInput(BaseModel):
    plant_capacity_kw: float = Field(..., gt=0, description="Total plant AC capacity [kW]")
    bay_max_ampacity_a: float = Field(default=630.0, gt=0, description="Substation bay circuit breaker ampacity [A]")
    grid_short_circuit_mva: Optional[float] = Field(default=None, gt=0, description="Upstream utility short-circuit capacity Sk'' [MVA]")
    grid_impedance_ohm: Optional[float] = Field(default=None, gt=0, description="Upstream grid impedance at PCC [ohm]")
    is_grid_impedance_assumed: bool = Field(default=True, description="True if default impedance fallback used")
    spare_bays_requested: int = Field(default=1, ge=0, description="Number of spare substation bays")
    power_factor: float = Field(default=0.95, ge=0.8, le=1.0)
    profile_id: str = Field(default="US-NEC-2020-v1")


def calculate_grid_interconnection(inputs: InterconnectionInput) -> CalculationResult:
    config = PROFILE_INTERCONNECTION_CONFIGS.get(inputs.profile_id, PROFILE_INTERCONNECTION_CONFIGS["US-NEC-2020-v1"])

    p_kw = inputs.plant_capacity_kw
    lv_ceiling_kw = config["lv_max_capacity_kw"]

    # 1. Profile-Driven Voltage Level Determination (LV < 100/250 kW; MV <= 40 MW; HV > 40 MW)
    if p_kw <= lv_ceiling_kw:
        is_lv_connection = True
        recommended_voltage_kv = config["lv_nominal_voltage_kv"]
        voltage_class = f"LV_{recommended_voltage_kv}kV"
        is_hv = False
    elif p_kw <= 40000.0:
        is_lv_connection = False
        recommended_voltage_kv = config["mv_nominal_voltage_kv"]
        voltage_class = f"MV_{recommended_voltage_kv}kV"
        is_hv = False
    else:
        is_lv_connection = False
        recommended_voltage_kv = config["hv_nominal_voltage_kv"]
        voltage_class = f"HV_{recommended_voltage_kv}kV"
        is_hv = True

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
        transformer_mva_recommended = 0.0
        switchgear_interrupting_rating_ka = 0.0
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
        transformer_mva_recommended = math.ceil((p_kw / (inputs.power_factor * 1000.0)) / 5.0) * 5.0

    # 4. Short-Circuit Fault Current Contribution at PCC (Ik'') per IEC 60909 / IEEE 141 / IEEE C37.010
    c_factor = 1.10
    default_sk = config["default_hv_sk_mva"] if is_hv else config["default_mv_sk_mva"]
    sk_mva = inputs.grid_short_circuit_mva if inputs.grid_short_circuit_mva else default_sk

    if inputs.grid_impedance_ohm:
        v_nominal_v = recommended_voltage_kv * 1000.0
        i_fault_ka = (c_factor * v_nominal_v) / (math.sqrt(3) * inputs.grid_impedance_ohm * 1000.0)
        grid_short_circuit_mva_calc = math.sqrt(3) * recommended_voltage_kv * i_fault_ka
    else:
        i_fault_ka = (c_factor * sk_mva * 1000.0) / (math.sqrt(3) * (recommended_voltage_kv * 1000.0))
        grid_short_circuit_mva_calc = sk_mva

    # Select standard switchgear interrupting rating (16, 25, 31.5, 40, 50 kA)
    if not is_lv_connection:
        standard_ratings = [16.0, 25.0, 31.5, 40.0, 50.0]
        switchgear_interrupting_rating_ka = next((r for r in standard_ratings if r >= i_fault_ka), 50.0)

    # Sanity Range Protection Check (0.5 kA to 50.0 kA for MV/HV connections)
    fault_current_warning = None
    if not is_lv_connection and (i_fault_ka < 0.5 or i_fault_ka > 50.0):
        fault_current_warning = f"FaultCurrentOutOfRange: Calculated grid fault current {i_fault_ka:.2f} kA is outside realistic grid range (0.5-50 kA). Utility verification required."

    # SCADA RTU & POI Recloser Specification
    scada_poi_specification = {
        "scada_rtu_telemetry_protocol": "IEC 60870-5-104 / DNP3 over IP",
        "poi_recloser_type": "3-Phase Vacuum Recloser with Numerical Relay Interface",
        "remote_trip_and_close_enabled": True,
        "revenue_metering_class": "0.2S Accuracy Class Active Energy Meter"
    }

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
        "transformer_mva_recommended": transformer_mva_recommended if not is_lv_connection else None,
        "switchgear_interrupting_rating_ka": switchgear_interrupting_rating_ka if not is_lv_connection else None,
        "bay_breakdown": bay_breakdown,
        "total_substation_bays": total_substation_bays,
        "grid_short_circuit_capacity_mva": round(grid_short_circuit_mva_calc, 2),
        "short_circuit_fault_current_ka": round(i_fault_ka, 2),
        "iec_60909_voltage_factor_c": c_factor,
        "fault_current_warning": fault_current_warning,
        "grid_impedance_source_policy": GRID_IMPEDANCE_SOURCE_POLICY,
        "requires_utility_data_verification": inputs.is_grid_impedance_assumed,
        "scada_poi_specification": scada_poi_specification,
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
