"""
Equipment Catalog Seed Entries (Phase 1 Residential + Phase 2 C&I Medium Voltage Equipment)
Per Technical Specification §2.1 & Phase 2 Sprint 2 Scope
Seeded with real manufacturer C&I equipment entries (Jinko, Trina, Canadian Solar, Fronius, SMA, Huawei, Sungrow, Schneider, ABB).
"""

from typing import List, Dict, Any

SEED_PV_MODULES = [
    {
        "id": "mod_res_001",
        "manufacturer": "Jinko Solar",
        "model_name": "Tiger Neo N-type 54HL4-V 400W",
        "p_mp_w": 400.0,
        "v_mp_v": 31.52,
        "i_mp_a": 12.69,
        "v_oc_v": 37.08,
        "i_sc_a": 13.41,
        "temp_coeff_pmp_percent": -0.30,
        "temp_coeff_voc_percent": -0.25,
        "temp_coeff_isc_percent": 0.045,
        "noct_c": 45.0,
        "source_url": "https://www.jinkosolar.com/uploads/Tiger_Neo_54HL4-(V)-400M.pdf",
        "validation_timestamp": "2025-02-18T10:00:00Z"
    },
    {
        "id": "mod_ci_trina_405w",
        "manufacturer": "Trina Solar",
        "model_name": "Vertex S TSM-DE09R.08 405W",
        "p_mp_w": 405.0,
        "v_mp_v": 34.2,
        "i_mp_a": 11.85,
        "v_oc_v": 41.3,
        "i_sc_a": 12.55,
        "temp_coeff_pmp_percent": -0.34,
        "temp_coeff_voc_percent": -0.25,
        "temp_coeff_isc_percent": 0.04,
        "noct_c": 43.0,
        "source_url": "https://www.trinasolar.com/en-glb/resources/downloads/vertex-s-de09r08",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    },
    {
        "id": "mod_ci_csi_450w",
        "manufacturer": "Canadian Solar",
        "model_name": "HiKu6 CS6L-450MS 450W",
        "p_mp_w": 450.0,
        "v_mp_v": 34.7,
        "i_mp_a": 12.97,
        "v_oc_v": 41.3,
        "i_sc_a": 13.72,
        "temp_coeff_pmp_percent": -0.34,
        "temp_coeff_voc_percent": -0.26,
        "temp_coeff_isc_percent": 0.05,
        "noct_c": 42.0,
        "source_url": "https://www.canadiansolar.com/downloads/datasheets/CS6L-MS_450W.pdf",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    }
]

SEED_INVERTERS = [
    {
        "id": "inv_res_001",
        "manufacturer": "Fronius",
        "model_name": "Primo 5.0-1 208-240",
        "inverter_type": "STRING_LV",
        "p_ac_kw": 5.0,
        "v_ac_nominal_v": 230.0,
        "phases": 1,
        "mppt_count": 2,
        "inputs_per_mppt": 2,
        "v_mppt_min_v": 80.0,
        "v_mppt_max_v": 600.0,
        "v_dc_max_v": 1000.0,
        "euro_efficiency_percent": 97.9,
        "derating_start_temp_c": 45.0,
        "derating_slope_percent_per_c": 2.0,
        "source_url": "https://www.fronius.com/en/solar-energy/products/primo-5-0-1",
        "validation_timestamp": "2025-02-18T10:00:00Z"
    },
    {
        "id": "inv_ci_sma_110kw",
        "manufacturer": "SMA Solar Technology",
        "model_name": "Sunny Tripower CORE2 110kW",
        "inverter_type": "STRING_THREE_PHASE",
        "p_ac_kw": 110.0,
        "v_ac_nominal_v": 400.0,
        "phases": 3,
        "mppt_count": 12,
        "inputs_per_mppt": 2,
        "v_mppt_min_v": 500.0,
        "v_mppt_max_v": 980.0,
        "v_dc_max_v": 1100.0,
        "euro_efficiency_percent": 98.6,
        "derating_start_temp_c": 45.0,
        "derating_slope_percent_per_c": 2.5,
        "source_url": "https://www.sma.de/en/products/solarinverters/sunny-tripower-core2",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    },
    {
        "id": "inv_ci_huawei_100kw",
        "manufacturer": "Huawei FusionSolar",
        "model_name": "SUN2000-100KTL-M2",
        "inverter_type": "STRING_THREE_PHASE",
        "p_ac_kw": 100.0,
        "v_ac_nominal_v": 400.0,
        "phases": 3,
        "mppt_count": 10,
        "inputs_per_mppt": 2,
        "v_mppt_min_v": 200.0,
        "v_mppt_max_v": 1000.0,
        "v_dc_max_v": 1100.0,
        "euro_efficiency_percent": 98.8,
        "derating_start_temp_c": 50.0,
        "derating_slope_percent_per_c": 2.0,
        "source_url": "https://solar.huawei.com/en/products/SUN2000-100KTL-M2",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    },
    {
        "id": "inv_ci_sungrow_250kw",
        "manufacturer": "Sungrow Power Supply",
        "model_name": "SG250HX 1500V String Inverter",
        "inverter_type": "STRING_THREE_PHASE",
        "p_ac_kw": 250.0,
        "v_ac_nominal_v": 800.0,
        "phases": 3,
        "mppt_count": 12,
        "inputs_per_mppt": 2,
        "v_mppt_min_v": 860.0,
        "v_mppt_max_v": 1300.0,
        "v_dc_max_v": 1500.0,
        "euro_efficiency_percent": 99.0,
        "derating_start_temp_c": 50.0,
        "derating_slope_percent_per_c": 2.0,
        "source_url": "https://us.sungrowpower.com/product/SG250HX",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    }
]

SEED_TRANSFORMERS = [
    {
        "id": "trafo_schneider_1000kva",
        "manufacturer": "Schneider Electric",
        "model_name": "Trihal Cast Resin Transformer 1000kVA 0.8/33kV",
        "rated_kva": 1000.0,
        "v_primary_v": 800.0,
        "v_secondary_kv": 33.0,
        "impedance_percent": 6.0,
        "cooling_class": "ONAN",
        "efficiency_percent": 99.1,
        "source_url": "https://www.se.com/en/product-range/1025-trihal/",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    }
]

SEED_SWITCHGEAR = [
    {
        "id": "swg_abb_safering_33kv",
        "manufacturer": "ABB Grid Solutions",
        "model_name": "SafeRing 36kV 630A CCV Ring Main Unit",
        "rated_voltage_kv": 33.0,
        "rated_current_a": 630.0,
        "short_time_withstand_current_ka": 20.0,
        "breaking_capacity_icu_ka": 20.0,
        "source_url": "https://new.abb.com/medium-voltage/switchgear/gas-insulated-switchgear/safering",
        "validation_timestamp": "2025-02-18T12:00:00Z"
    }
]
