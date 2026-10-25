# Phase 3 Sprint 4 Mid-Point Deliverables & Gate Criteria Draft

**Document Version:** 1.0.0
**Date:** October 2026
**Status:** In Review

---

## 1. Week 1 Non-Blocking Clarifications

1. **IEEE C37.91 Confirmation for ANSI 87T:**
   - Confirmed explicitly in `calc/calc_hv_protection/service.py` under `"standard_citation": "IEEE C37.91 / IEC 60255-187-1"`.
2. **CAPEX Unit Label Correction:**
   - Turnkey project CAPEX: **$0.80 / Wac** ($40,000,000 / 50,000 kWac) and **$0.748 / Wdc** ($40,000,000 / 53,500 kWdc).
3. **P90 Yield Basis Definition:**
   - **Primary Basis:** Monte Carlo simulation output (**82,160.06 MWh / year**).
   - **Cross-Check Basis:** Analytical RSS formula (**82,207.79 MWh / year**), demonstrating a tight **0.06% delta** ($47.73\text{ MWh}$).
4. **Central Architecture End-to-End Tests:**
   - `test_central_vs_string_topology_end_to_end_differentiation`: Asserts `CENTRAL_INVERTER` recommendation, 115.0 kV interconnection, 55 MVA transformer, and 4-bay substation arrangement.

---

## 2. Draft Phase 3 Gate Criteria (G21–G30)

| Gate ID | Gate Name | Assertion Statement | Evidence Document / Artifact | Verification Mode |
|:-------:|:----------|:--------------------|:-----------------------------|:-----------------:|
| **G21** | Utility Workflow Speed | Design-to-bankable report < 2 hours for > 1 MW plant | Benchmarking Log | Manual Walkthrough |
| **G22** | Monte Carlo Bankability Yield | P50/P75/P90 simulation within +-1.0% of SAM 2023.12.08 | `test_phase3_sprint1_deliverables.py` | Automated CI |
| **G23** | 20-Year DSCR Trajectory | $\text{DSCR}_{20} \ge 1.20\times$ across all 20 years | `docs/specs/PHASE_3_SPRINT2_DISCLOSURES.md` | Automated CI |
| **G24** | Central vs String Topology | Recommender auto-selects Central for $\ge 3\text{ MW}$ flat terrain | `test_phase3_sprint3_deliverables.py` | Automated CI |
| **G25** | HV Substation Interconnection | Auto-proposes 110/115/132/220/400 kV voltage and bay count | `test_calc_grid_interconnection.py` | Automated CI |
| **G26** | HV Protection Relaying | ANSI 21/87T/87B settings match IEEE C37 worked examples | `test_phase3_sprint4_deliverables.py` | Automated CI |
| **G27** | SCADA Telemetry & POI | Specifies RTU, IEC 60870-5-104/DNP3, recloser, 0.2S meter | `test_sprint3_cand_i_extensions.py` | Automated CI |
| **G28** | MENA-GCC Profile Support | Loads 132/220/400 kV grid levels and 1.15x DSCR limits | `test_phase3_sprint3_deliverables.py` | Automated CI |
| **G29** | Complete 20-Row DSCR Schedule | Surface full 20-row DSCR table in bankability output | `docs/specs/PHASE_3_SPRINT2_DISCLOSURES.md` | Automated CI |
| **G30** | Phase 1 & 2 Zero-Regression | 100% pass on Phase 1 & Phase 2 acceptance gates | `tests/run_phase1_acceptance_gates.py` | Automated CI |


---

## 3. SCADA Deepening & Communication Architecture Specification

### 3.1 Substation Automation & Telemetry Protocols
- **Primary Protocol:** IEC 60870-5-104 (Ethernet TCP/IP) for transmission system operator (TSO) / distribution system operator (DSO) control center interfacing.
- **Secondary / Substation Bus Protocol:** DNP3 over IP / IEC 61850 MMS & GOOSE messaging for high-speed sub-cycle protection interlocking.
- **Remote Control Capabilities:** Enabled for remote trip, close, active power curtailment, and reactive power compensation setpoint adjustments.

### 3.2 POI Recloser & Circuit Breaker Interface
- **Recloser Specification:** 3-Phase Vacuum Recloser with integrated numerical relay interface (ANSI 21/87T/87B/50/51/51N/27/59/81).
- **Revenue Metering:** 0.2S Accuracy Class Active Energy Metering with optical port and RS-485 Modbus RTU / DNP3 output.

---

## 4. Test File Inventory & Mapping (25 Test Files)

| File Path | Function Count | Deliverable / Package Covered |
|:----------|:--------------:|:------------------------------|
| `tests/test_3d_shading_integration.py` | 1 | 3D Viewport & Heatmap Equality |
| `tests/test_750kw_cand_i_end_to_end.py` | 1 | 750 kW C&I End-to-End Workflow & Permit SLD Export |
| `tests/test_benchmarks.py` | 2 | Core Benchmark Harness Integrity |
| `tests/test_calc_financial.py` | 1 | Residential & C&I Quick Mode Financials |
| `tests/test_calc_grid_interconnection.py` | 3 | LV/MV/HV Interconnection & Bay Breakdown |
| `tests/test_calc_sizing_dc.py` | 2 | DC String Sizing & Temperature Derating |
| `tests/test_calc_yield_benchmarks.py` | 3 | Physics Yield Simulation Benchmarks 1–3 |
| `tests/test_calc_yield_benchmarks_sprint4.py` | 4 | Physics Yield Simulation Benchmarks 4, 5, 6, 9 |
| `tests/test_cand_i_workflow.py` | 1 | C&I 9-Step Workflow Tree Navigation |
| `tests/test_catalog_schema_extension.py` | 2 | Equipment Catalog Schema & Validation |
| `tests/test_compliance_refusal.py` | 4 | Refusal-to-Guess Safeguard & PE Override Governance |
| `tests/test_golden_integrity.py` | 2 | Golden Hash Manifest Verification |
| `tests/test_microinverter_isolation.py` | 1 | Microinverter Topology Calculations |
| `tests/test_pdf_watermark.py` | 1 | PDF Text-Layer Watermarking & Branding |
| `tests/test_phase2_sprint0_regression.py` | 1 | Phase 1 Acceptance Gate Regression Harness |
| `tests/test_phase3_sprint1_deliverables.py` | 3 | Monte Carlo Bankability Yield Simulation (P50/P75/P90) |
| `tests/test_phase3_sprint2_deliverables.py` | 6 | Topology Recommender & HV Substation Sizing |
| `tests/test_phase3_sprint3_deliverables.py` | 4 | HV Protection Relaying & MENA-GCC Profile Verification |
| `tests/test_phase3_sprint4_deliverables.py` | 3 | IEEE C37.113 / C37.91 / C37.234 Protection Reference Benchmarks |
| `tests/test_proposal_generator.py` | 2 | Proposal Generator PDF Rendering |
| `tests/test_provenance.py` | 7 | Provenance Envelope Structure & Hashing |
| `tests/test_rtl_layout.py` | 4 | RTL Layout Static Code Scanner |
| `tests/test_sprint3_cand_i_extensions.py` | 2 | 3-Phase AC Wiring & Protection Extensions |
| `tests/test_sprint3_packages.py` | 4 | DC/AC Cable Sizing, Protection, Grounding/Lightning |
| `tests/test_sprint4_cand_i_deliverables.py` | 4 | Civil Foundation Sizing & Wind Overturning |

**Total Inventory:** 25 files, 66 test functions, 310 assertions.
