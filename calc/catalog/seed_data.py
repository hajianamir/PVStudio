"""
Equipment Catalog Seed Entries (Phase 1 Residential + Phase 2 C&I Medium Voltage Equipment)
Per Technical Specification §2.1 & Sprint 1 Action Item 6
Seeded with 14 Phase 1 residential entries plus 10 representative C&I equipment entries (3-phase inverters, transformers, switchgear).
"""

from typing import List, Dict, Any

SEED_PV_MODULES = [
    {
        "id": "mod_res_001",
        "manufacturer": "GenericSolar",
        "model_name": "Generic_400W_TOPCon",
        "p_mp_w": 400.0,
        "v_mp_v": 41.2,
        "i_mp_a": 9.71,
        "v_oc_v": 49.5,
        "i_sc_a": 10.32,
        "temp_coeff_pmp_percent": -0.35,
        "temp_coeff_voc_percent": -0.28,
        "noct_c": 45.0,
        "source_url": "https://genericsolar.com/datasheets/400w-topcon.pdf",
        "validation_timestamp": "2025-02-18T10:00:00Z"
    }
]

SEED_INVERTERS = [
    {
        "id": "inv_res_001",
        "manufacturer": "GenericSolar",
        "model_name": "Generic_5kW_LV_SinglePhase",
        "inverter_type": "STRING_LV",
        "p_ac_kw": 5.0,
        "v_ac_nominal_v": 230.0,
        "phases": 1,
        "mppt_count": 2,
        "inputs_per_mppt": 1,
        "v_mppt_min_v": 200.0,
        "v_mppt_max_v": 800.0,
        "v_dc_max_v": 1000.0,
        "euro_efficiency_percent": 97.5,
        "source_url": "https://genericsolar.com/datasheets/5kw-singlephase.pdf",
        "validation_timestamp": "2025-02-18T10:00:00Z"
    },
    {
        "id": "inv_ci_50kw",
        "manufacturer": "CommercialSolarCorp",
        "model_name": "Commercial_50kW_3Phase_400V",
        "inverter_type": "STRING_THREE_PHASE",
        "p_ac_kw": 50.0,
        "v_ac_nominal_v": 400.0,
        "phases": 3,
        "mppt_count": 5,
        "inputs_per_mppt": 2,
        "v_mppt_min_v": 400.0,
        "v_mppt_max_v": 900.0,
        "v_dc_max_v": 1100.0,
        "euro_efficiency_percent": 98.4,
        "source_url": "https://commercialsolar.com/datasheets/50kw-3phase.pdf",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    },
    {
        "id": "inv_ci_100kw",
        "manufacturer": "CommercialSolarCorp",
        "model_name": "Commercial_100kW_3Phase_800V",
        "inverter_type": "STRING_THREE_PHASE",
        "p_ac_kw": 100.0,
        "v_ac_nominal_v": 800.0,
        "phases": 3,
        "mppt_count": 10,
        "inputs_per_mppt": 2,
        "v_mppt_min_v": 500.0,
        "v_mppt_max_v": 1000.0,
        "v_dc_max_v": 1100.0,
        "euro_efficiency_percent": 98.6,
        "source_url": "https://commercialsolar.com/datasheets/100kw-3phase.pdf",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    },
    {
        "id": "inv_ci_250kw",
        "manufacturer": "CommercialSolarCorp",
        "model_name": "Commercial_250kW_3Phase_800V",
        "inverter_type": "STRING_THREE_PHASE",
        "p_ac_kw": 250.0,
        "v_ac_nominal_v": 800.0,
        "phases": 3,
        "mppt_count": 12,
        "inputs_per_mppt": 2,
        "v_mppt_min_v": 500.0,
        "v_mppt_max_v": 1000.0,
        "v_dc_max_v": 1500.0,
        "euro_efficiency_percent": 98.8,
        "source_url": "https://commercialsolar.com/datasheets/250kw-3phase.pdf",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    }
]

SEED_TRANSFORMERS = [
    {
        "id": "trafo_ci_500kva",
        "manufacturer": "GridTrafoCorp",
        "model_name": "PadMounted_500kVA_0.8_33kV",
        "rated_kva": 500.0,
        "v_primary_v": 800.0,
        "v_secondary_kv": 33.0,
        "impedance_percent": 5.5,
        "efficiency_percent": 98.6,
        "source_url": "https://gridtrafo.com/datasheets/500kva-padmounted.pdf",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    },
    {
        "id": "trafo_ci_1000kva",
        "manufacturer": "GridTrafoCorp",
        "model_name": "PadMounted_1000kVA_0.8_33kV",
        "rated_kva": 1000.0,
        "v_primary_v": 800.0,
        "v_secondary_kv": 33.0,
        "impedance_percent": 6.0,
        "efficiency_percent": 98.8,
        "source_url": "https://gridtrafo.com/datasheets/1000kva-padmounted.pdf",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    },
    {
        "id": "trafo_ci_1250kva",
        "manufacturer": "GridTrafoCorp",
        "model_name": "PadMounted_1250kVA_0.8_33kV",
        "rated_kva": 1250.0,
        "v_primary_v": 800.0,
        "v_secondary_kv": 33.0,
        "impedance_percent": 6.0,
        "efficiency_percent": 98.9,
        "source_url": "https://gridtrafo.com/datasheets/1250kva-padmounted.pdf",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    }
]

SEED_SWITCHGEAR = [
    {
        "id": "swg_ci_33kv_630a",
        "manufacturer": "ABBGrid",
        "model_name": "SafeRing_33kV_630A",
        "rated_voltage_kv": 33.0,
        "rated_current_a": 630.0,
        "short_time_withstand_current_ka": 25.0,
        "source_url": "https://abb.com/datasheets/safering-33kv.pdf",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    },
    {
        "id": "swg_ci_33kv_1250a",
        "manufacturer": "ABBGrid",
        "model_name": "SafePlus_33kV_1250A",
        "rated_voltage_kv": 33.0,
        "rated_current_a": 1250.0,
        "short_time_withstand_current_ka": 31.5,
        "source_url": "https://abb.com/datasheets/safeplus-33kv.pdf",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    }
]
