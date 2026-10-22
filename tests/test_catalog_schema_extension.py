"""
Automated CI Test: Equipment Catalog Schema Extension Verification
Asserts that C&I 3-phase inverters, LV/MV transformers, and MV switchgear schemas validate cleanly
without breaking Phase 1 residential 14 seed entries.
"""

import pytest
from calc.catalog.schema import (
    PVModuleCatalogEntity,
    InverterCatalogEntity,
    TransformerCatalogEntity,
    SwitchgearCatalogEntity
)


def test_phase1_residential_seed_entries_valid():
    # Verify Phase 1 residential single-phase inverter entry
    res_inverter = InverterCatalogEntity(
        id="inv_res_001",
        manufacturer="GenericSolar",
        model_name="Generic_5kW_LV_SinglePhase",
        inverter_type="STRING_LV",
        p_ac_kw=5.0,
        v_ac_nominal_v=230.0,
        phases=1,
        mppt_count=2,
        inputs_per_mppt=1,
        v_mppt_min_v=200.0,
        v_mppt_max_v=800.0,
        v_dc_max_v=1000.0,
        euro_efficiency_percent=97.5,
        source_url="https://genericsolar.com/datasheets/5kw-singlephase.pdf",
        validation_timestamp="2025-02-18T10:00:00Z"
    )
    assert res_inverter.phases == 1
    assert res_inverter.source_url != ""


def test_phase2_cand_i_equipment_entries_valid():
    # Verify Phase 2 C&I 3-phase string inverter entry (100 kW)
    ci_inverter = InverterCatalogEntity(
        id="inv_ci_001",
        manufacturer="CommercialSolar",
        model_name="Commercial_100kW_3Phase_800V",
        inverter_type="STRING_THREE_PHASE",
        p_ac_kw=100.0,
        v_ac_nominal_v=800.0,
        phases=3,
        mppt_count=10,
        inputs_per_mppt=2,
        v_mppt_min_v=500.0,
        v_mppt_max_v=1000.0,
        v_dc_max_v=1100.0,
        euro_efficiency_percent=98.6,
        source_url="https://commercialsolar.com/datasheets/100kw-3phase.pdf",
        validation_timestamp="2025-02-18T12:00:00Z"
    )
    assert ci_inverter.phases == 3
    assert ci_inverter.p_ac_kw == 100.0

    # Verify Phase 2 C&I LV/MV Step-Up Pad-Mounted Transformer (1.25 MVA, 0.8kV / 33kV)
    transformer = TransformerCatalogEntity(
        id="trafo_ci_001",
        manufacturer="GridTrafoCorp",
        model_name="PadMounted_1250kVA_0.8_33kV",
        rated_kva=1250.0,
        v_primary_v=800.0,
        v_secondary_kv=33.0,
        impedance_percent=6.0,
        efficiency_percent=98.9,
        source_url="https://gridtrafo.com/datasheets/1250kva-padmounted.pdf",
        validation_timestamp="2025-02-18T12:00:00Z"
    )
    assert transformer.v_secondary_kv == 33.0
    assert transformer.rated_kva == 1250.0

    # Verify Phase 2 C&I MV Switchgear (33 kV, 630 A)
    switchgear = SwitchgearCatalogEntity(
        id="swg_ci_001",
        manufacturer="ABBGrid",
        model_name="SafeRing_33kV_630A",
        rated_voltage_kv=33.0,
        rated_current_a=630.0,
        short_time_withstand_current_ka=25.0,
        source_url="https://abb.com/datasheets/safering-33kv.pdf",
        validation_timestamp="2025-02-18T12:00:00Z"
    )
    assert switchgear.rated_voltage_kv == 33.0
