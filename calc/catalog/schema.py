"""
Equipment Catalog Schema & C&I Medium-Voltage Extension
Per Technical Specification §2.3.2, Phase 2 Sprint 1 Scope & Clarification 6
Extends catalog entity definitions to support 3-phase C&I string inverters (50-250 kW) with temperature derating curves,
LV/MV pad-mounted step-up transformers (100 kVA - 1.25 MVA), and MV switchgear.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class PVModuleCatalogEntity(BaseModel):
    id: str
    manufacturer: str
    model_name: str
    p_mp_w: float
    v_mp_v: float
    i_mp_a: float
    v_oc_v: float
    i_sc_a: float
    temp_coeff_pmp_percent: float
    temp_coeff_voc_percent: float
    temp_coeff_isc_percent: float = Field(default=0.05, description="Isc temperature coefficient [%/°C]")
    noct_c: float = 45.0
    source_url: str
    validation_timestamp: str


class InverterCatalogEntity(BaseModel):
    id: str
    manufacturer: str
    model_name: str
    inverter_type: str = Field(..., description="MICRO, STRING_LV, STRING_THREE_PHASE, CENTRAL_MV")
    p_ac_kw: float
    v_ac_nominal_v: float
    phases: int = Field(default=1, description="1 for single-phase, 3 for three-phase")
    mppt_count: int
    inputs_per_mppt: int
    v_mppt_min_v: float
    v_mppt_max_v: float
    v_dc_max_v: float
    euro_efficiency_percent: float
    derating_start_temp_c: float = Field(default=45.0, description="Ambient temperature where thermal derating begins [°C]")
    derating_slope_percent_per_c: float = Field(default=2.0, description="Power derating rate per °C above start temp [%/°C]")
    source_url: str
    validation_timestamp: str


class TransformerCatalogEntity(BaseModel):
    id: str
    manufacturer: str
    model_name: str
    rated_kva: float = Field(..., gt=0, description="Transformer rated apparent power [kVA]")
    v_primary_v: float = Field(..., gt=0, description="Primary low-voltage side [V, e.g. 800V]")
    v_secondary_kv: float = Field(..., gt=0, description="Secondary medium-voltage side [kV, e.g. 33kV]")
    impedance_percent: float = Field(default=6.0, description="Short-circuit impedance Z [%]")
    cooling_class: str = Field(default="ONAN", description="Transformer cooling class (ONAN, ONAF, Dry)")
    efficiency_percent: float = Field(default=98.8, ge=90, le=100)
    source_url: str
    validation_timestamp: str


class SwitchgearCatalogEntity(BaseModel):
    id: str
    manufacturer: str
    model_name: str
    rated_voltage_kv: float = Field(..., gt=0)
    rated_current_a: float = Field(default=630.0, gt=0)
    short_time_withstand_current_ka: float = Field(default=25.0, gt=0)
    breaking_capacity_icu_ka: float = Field(default=25.0, gt=0, description="Rated ultimate short-circuit breaking capacity [kA]")
    source_url: str
    validation_timestamp: str
