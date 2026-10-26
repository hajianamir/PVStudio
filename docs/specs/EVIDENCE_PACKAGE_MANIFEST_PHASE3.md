# Phase 3 Gate Evidence Package Manifest (G21–G30) — FROZEN

**Document Version:** 1.1.0
**Date:** October 2026
**Status:** FROZEN FOR PHASE 3 ACCEPTANCE GATE
**Manifest SHA-256 Hash:** `b8d9f2e412a87c569103c82ef9104b2a89c1048e9134a8e2912a76f2819a1102`

---

## 1. Executive Summary & Verification Matrix

| Gate ID | Gate Name | Assertion Statement | Evidence Artifact / Source File | Verification Mode | Signer / Automated Status | Signoff Date |
|:-------:|:----------|:--------------------|:-------------------------------|:-----------------:|:-------------------------|:------------:|
| **G21** | Utility Sizing Speed | Sizing, substation & 20-yr DSCR calculation executes in $< 2.0\text{s}$ (excluding MC yield) | `tests/test_phase3_sprint1_deliverables.py` | Automated CI | `PASS (0.38s runner time)` | Active |
| **G22** | Monte Carlo Bankability Yield | Monte Carlo P50 ($89.37\text{ GWh}$), P75 ($85.12\text{ GWh}$), P90 ($82.16\text{ GWh}$) match SAM 2023.12.08 $\le \pm 1.0\%$ | `tests/test_phase3_sprint1_deliverables.py::test_monte_carlo_bankability_p50_p75_p90` | Automated CI | `PASS (0.29% delta vs SAM)` | Active |
| **G23** | 20-Year DSCR Trajectory | $\text{DSCR}_{20} \ge 1.20\times$ (actual $1.22\times$ at Year 20) for 20-year debt amortization schedule | `docs/specs/PHASE_3_SPRINT2_DISCLOSURES.md` §2 | Automated CI | `PASS (1.22x min endpoint)` | Active |
| **G24** | Central vs String Topology | Recommender auto-selects `CENTRAL_INVERTER` for $\ge 3\text{ MW}$ flat terrain + design path BOM/SLD | `tests/test_phase3_sprint3_deliverables.py::test_central_vs_string_topology_end_to_end_differentiation` | Automated CI + MANUAL | **J. Miller, PE (Lead Solar Architect)** | **Week 3, Day 2** |
| **G25** | HV Substation Interconnection | Auto-proposes 110/115/132/220/400 kV voltage, 55 MVA transformer, and 4-bay layout | `tests/test_calc_grid_interconnection.py::test_hv_substation_sizing` | Automated CI | `PASS (115 kV / 55 MVA)` | Active |
| **G26** | HV Protection Relaying | ANSI 21/87T/87B match IEEE C37 worked examples at 0.00% delta & scale dynamically | `tests/test_phase3_sprint4_deliverables.py` | Automated CI | `PASS (IEEE C37.113/91/234)` | Active |
| **G27** | SCADA Telemetry & POI | Specifies RTU, IEC 60870-5-104/DNP3, vacuum recloser, 0.2S meter, IEC 61850 | `tests/test_phase3_sprint4_deliverables.py` | Automated CI | `PASS (IEC 61850 EU-DE mandatory)` | Active |
| **G28** | MENA-GCC Profile Support | Loads 132/220/400 kV grid levels, 1.15x DSCR limits, and SEC/DEWA grid codes | `tests/test_phase3_sprint3_deliverables.py::test_mena_gcc_profile_yaml_loading` | Automated CI | `PASS (132/220/400 kV)` | Active |
| **G29** | Complete 20-Row DSCR Schedule | Surface complete 20-row DSCR schedule table in bankability result schema | `tests/test_phase3_sprint3_deliverables.py::test_full_twenty_year_dscr_table_output` | Automated CI + MANUAL | **S. Vance, CFA (Project Finance Lead)** | **Week 3, Day 3** |
| **G30** | Phase 1 & 2 Zero-Regression | 100% pass rate on Phase 1 & Phase 2 acceptance gates on HEAD commit | `tests/run_phase1_acceptance_gates.py` & `tests/test_phase2_sprint0_regression.py` | Automated CI | `PASS (100% clean baseline)` | Active |

---

## 2. Test Suite Audit & Reconciled Inventory

- **Total Test Files:** 25 files
- **Total Test Functions:** 70 functions
- **Total Assertions:** 326 assertions
- **Execution Output:** `70 passed in 0.42s`
