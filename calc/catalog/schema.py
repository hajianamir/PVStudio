"""
Equipment Catalog Schema & C&I Medium-Voltage Extension
Per Technical Specification §2.3.2 & Phase 2 Sprint 1 Scope
Extends catalog entity definitions to support 3-phase C&I string inverters (50-250 kW),
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
    source_url: str
    validation_timestamp: str
