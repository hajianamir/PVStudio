# Phase 1 Specification: Residential MVP (Months 0–6)

```
Document Class: Derived Execution Document (non-authoritative)
Subordinate To: PVStudio_Technical_Product_Specification.md v1.0.0 (FROZEN)
Governance: Engineering-owned; may evolve in minor versions (1.0.x)
Conflict Rule: If this document contradicts the frozen suite, the frozen suite prevails and a CR is required.
Version: 1.0.0
Status: APPROVED — Execution Phase
Roadmap Reference: §9 of 09_phased_roadmap.md
Acceptance Gate Reference: §10.3 of 10_acceptance_tests.md
```

| Version | Status | Last Updated | Owner |
| :--- | :--- | :--- | :--- |
| 1.0.0 | Approved for Execution | 2025-02-18 | Technical Lead & Lead PV Engineer |

---

## 1. Phase 1 Objective

Deliver a production-grade, single-segment platform that takes a residential site — typically $< 10 \text{ kW}$ per rooftop, on-grid or off-grid/hybrid — from address input to a signed-ready proposal with a verified bill of materials (BOM) in under 30 minutes of user working time.

Phase 1 is the physics-and-proof phase. The calculation engine, the weather data abstraction layer, the provenance envelope, and the compliance safeguard must be built correctly here, because every later phase (C&I, Utility-Scale, Mobile, AI Copilot) depends on these foundations. UI, financial modeling, and reporting are scoped to what is necessary to prove the physics and the proposal pipeline end-to-end — not more.

Phase 1 deliberately excludes C&I and Utility-Scale workflows, all MV/HV/grid-interconnection analysis, AI Copilot, procurement/ERP integrations, and multi-currency. See §14 for the explicit exclusion list.

---

## 2. In-Scope / Out-of-Scope Breakdown

### 2.1 In Scope

| Domain | Phase 1 Scope |
| :--- | :--- |
| **Segments** | Residential only ($< 10 \text{ kW}$ typical; hard cap $30 \text{ kW}$). |
| **Topologies** | On-grid, off-grid, hybrid. |
| **Architecture** | Modular monolith (FastAPI) — no microservice extraction yet. |
| **Calculation Packages** | `calc_yield`, `calc_sizing_dc`, `calc_electrical_dc`, `calc_electrical_ac` (LV only), `calc_protection` (basic), `calc_grounding_lightning` (residential subset), `calc_financial` (Quick mode only). |
| **Weather Data** | PVGIS (default) + NASA POWER (cross-validation). |
| **Uncertainty** | Quick mode only (RSS propagation $\rightarrow$ P50 / P90). |
| **Compliance Profiles** | US-NEC-2020 and EU-DE — residential-relevant clauses only. |
| **UI Application** | Web/PC: Wizard mode + Expert mode, 2D map, roof-plane 3D. |
| **Mobile Scope** | Read-only Android companion for site capture (photos, roof measurements, GPS) — no offline design. |
| **Reporting** | Residential proposal template (PDF + DOCX), section toggles, white-label branding. |
| **Authentication** | Keycloak OIDC, role-based access (Owner, Designer, Reviewer). |
| **Deployment** | Docker Compose for dev/staging; single-node Kubernetes (Helm chart) for staging-like env. |
| **Language** | English only, but RTL-ready layout architecture verified with a test toggle. |

### 2.2 Out of Scope (Deferred)

* C&I and Utility-Scale workflows, menus, equipment libraries.
* MV/HV collection design, substation, upstream grid analysis, bay/voltage auto-recommender.
* Central inverter architecture, MV transformers, SCADA, protection relay settings.
* Bankable Monte Carlo uncertainty (deferred to Phase 3).
* SolarGIS, NSRDB, Meteonorm adapters (interface defined, adapters deferred).
* Procurement, RFQ, purchase orders, logistics, inventory.
* AI Copilot (Phase 4).
* Multi-currency, multi-jurisdiction tariff libraries beyond US/EU-DE residential defaults.
* Full Android offline design; commissioning and IV-curve test capture.
* CRM/ERP/BIM integrations.
* Digital signature workflow beyond a single-reviewer approval stub.
* BESS grid-services modeling (Utility-Scale only).

---

## 3. Technical Foundation (Non-Negotiable at Sprint 1)

These four items must exist before the first residential feature is built:

### 3.1 Provenance Envelope on Every Result

Every persisted calculation result carries:
`calc_module, calc_version, input_hash, profile_id, timestamp, user_id, project_id`

The envelope is enforced at the repository layer, not the API layer, so no code path can persist a bare number. A CI test rejects any calculation endpoint returning a result object missing the envelope. The CI test is committed in the same commit that introduces the first calculation endpoint.

### 3.2 Weather Data Abstraction Layer

All weather access flows through a single `WeatherProvider` interface:
* `get_irradiance(lat, lon, start, end, resolution) -> IrradianceSeries`
* `get_temperature(lat, lon, start, end) -> TemperatureSeries`
* `get_metadata() -> DatasetMetadata` (source name, vintage/TMY year range, spatial resolution, override status)

Phase 1 implements two adapters: PVGIS (primary) and NASA POWER (cross-validation). Cross-validation comparison is surfaced in the UI as a data-quality indicator. Metadata is stored with the project and printed in every report.

### 3.3 Refusal-to-Guess Safeguard (Residential Subset)

Wired into the compliance layer from Sprint 1. When a compliance profile is incomplete for a specific design parameter:
* The system blocks auto-approval.
* Emits an explicit warning: `Requires local engineer sign-off: <parameter>`.
* Records the override in the audit trail with user identity and timestamp.

### 3.4 RTL-Ready Layout Architecture

All UI components use logical CSS properties (`margin-inline-start`, `padding-inline-end`, `inset-inline`), not hardcoded left/right. A test toggle switches the app to `dir="rtl"` and a snapshot test verifies no layout break.

---

## 4. Calculation Engine Scope & 10 Physics Benchmarks

### 4.1 Modules Built in Phase 1

| Package | Phase 1 Responsibility | Phase 1 Exclusions |
| :--- | :--- | :--- |
| `calc_yield` | Irradiance transposition (Perez / Hay-Davies), IAM, soiling, temperature derating, 8760 simulation, roof-plane shading loss. | Terrain shading, snow loss model. |
| `calc_sizing_dc` | String voltage window (temperature coefficients), module-inverter matching, string count. | Multi-MPPT optimization across large arrays. |
| `calc_electrical_dc` | DC cable sizing, voltage drop, ampacity, DC fusing. | — |
| `calc_electrical_ac` | LV AC cable sizing, voltage drop, single/three-phase loads. | MV collection, transformer sizing. |
| `calc_protection` | Breaker and fuse selection, basic coordination, SPD selection. | MV relay coordination, MV fault-current studies. |
| `calc_grounding_lightning` | IEC 62305 residential risk assessment, earthing electrode sizing. | Full earth-termination network design. |
| `calc_financial` | Quick mode: P50/P90 via RSS, LCOE, payback, monthly savings, cash flow. | Monte Carlo bankable mode, DSCR. |
| `calc_recommender` | Inverter and battery recommendation with explanation. | Central/string architecture decision, bay auto-sizing. |

### 4.2 Quick-Mode Uncertainty (RSS)

$$\sigma_{total} = \sqrt{\sigma_{inter-annual}^2 + \sigma_{model}^2 + \sigma_{soiling}^2 + \sigma_{mismatch}^2 + \sigma_{wiring}^2 + \sigma_{degradation}^2 + \sigma_{availability}^2}$$

$$P50 = \text{expected\_annual\_yield}$$
$$P90 = P50 - 1.282 \times \sigma_{total}$$

### 4.3 Ten Benchmark Cases — The Physics Gate

The engine must reproduce the following 10 reference cases within **$\pm 3\%$ on annual yield (P50)** and **$\pm 5\%$ on monthly yield** vs. PVsyst/SAM (unless a case deviation is explicitly justified by a CR):

| Case | Purpose |
| :--- | :--- |
| **1** | $5 \text{ kW}$ rooftop, flat, south-facing, EU-DE Baseline on-grid |
| **2** | $8 \text{ kW}$ rooftop, pitched $30^\circ$, azimuth $180^\circ$, US Baseline on-grid |
| **3** | $4 \text{ kW}$ rooftop, azimuth $90^\circ$ (east) orientation sensitivity |
| **4** | $6 \text{ kW}$ with $15\%$ near-shading from a chimney (shading model validation) |
| **5** | $5 \text{ kW}$ with $2\%$ soiling increase (soiling model) |
| **6** | $5 \text{ kW}$ in a high-temperature climate (US Southwest derating) |
| **7** | $3 \text{ kW}$ off-grid with $10 \text{ kWh}$ battery (off-grid sizing path) |
| **8** | $6 \text{ kW}$ hybrid with $5 \text{ kWh}$ battery (hybrid path) |
| **9** | $5 \text{ kW}$ with micro-inverters (architecture sensitivity) |
| **10** | $5 \text{ kW}$ with $-10^\circ\text{C}$ to $+40^\circ\text{C}$ ambient range (string voltage window) |

*Sprint 1 Benchmark Harness Directive:* The benchmark harness scaffold (input fixtures for all 10 cases, PVsyst/SAM reference outputs, tolerance checker) is built in Sprint 1 before `calc_yield` code lands.

---

## 5. Residential Workflow — Menu Tree

```
1. Site Capture (Address/GPS, Satellite MapLibre GL, Roof polygon, Obstacles, Android photos)
2. Roof Layout (Pitch/azimuth plane, Module placement, Row spacing, Shading, String routing)
3. System Size (Load profile, Inverter/Battery sizing, String config, DC/AC summary, Protection)
4. Financial & Proposal (Quick-mode P50/P90, Tariffs/incentives, LCOE/payback, Proposal template, White-label)
5. Permitting Package (Residential LV SLD, Layout drawing PDF, BOM/BOQ, Compliance checklist, Export PDF/DOCX)
```

---

## 6. Six-Sprint Delivery Plan (4 Weeks Each)

| Sprint | Focus Area | Exit Criteria |
| :--- | :--- | :--- |
| **S1** | Foundation: Repo structure, FastAPI skeleton, Docker Compose, Postgres+PostGIS+Timescale, Keycloak, Provenance envelope (CI enforced), WeatherProvider interface, Benchmark harness scaffold with 10 case fixtures, CI pipeline. | Hello calculation endpoint persists result with valid provenance envelope; CI enforces it; benchmark scaffold live with 10 reference cases loaded. |
| **S2** | Weather abstraction + PVGIS + NASA POWER; `calc_yield` v0; Benchmarks 1–3 execution. | Benchmarks 1–3 within tolerance ($\pm 3\%$ annual, $\pm 5\%$ monthly); weather metadata stored/printed. |
| **S3** | `calc_sizing_dc` + `calc_electrical_dc`; 2D roof polygon capture; obstacle tagging; Benchmarks 4–6 execution. | Benchmarks 4–6 pass within tolerance; 2D roof capture usable end-to-end. |
| **S4** | 3D roof view (R3F), module placement, shading, string routing; `calc_electrical_ac` + `calc_protection` + `calc_grounding_lightning`; Benchmarks 7–10 execution. | All 10 benchmarks pass within tolerance; shading model validated. |
| **S5** | `calc_financial` (Quick mode RSS), tariffs, US-NEC-2020 / EU-DE compliance, refusal-to-guess, proposal generator (PDF/DOCX). | Proposal generated end-to-end; refusal-to-guess CI test passes. |
| **S6** | Expert mode parity, Android site-capture companion, full acceptance run, evidence package assembly, gate review. | Phase 1 acceptance gate evidence submitted; all gate criteria green. |

---

## 7. Team Composition (Phase 1 — 10.0 FTE)

| Role | FTE | Mandatory Status & Core Responsibility |
| :--- | :--- | :--- |
| **Technical Lead / Architect** | 1.0 | Architectural boundary enforcement & system integrity. |
| **Backend Python Engineers** | 2.0 | FastAPI services, repository envelope enforcement, database integration. |
| **Frontend React/TS Engineers** | 2.0 | Cockpit UI, Wizard/Expert parity, MapLibre 2D viewport, proposal generator. |
| **3D / Geospatial Engineer** | 1.0 | R3F roof-plane geometry, shading mesh calculation, PostGIS spatial queries. |
| **PV / Computational Engineer** | 1.0 | **NON-OPTIONAL:** Physics engine math, PVLib models, benchmark tuning. |
| **Regulatory / Compliance Engineer** | 0.5 | US-NEC-2020 and EU-DE residential YAML rule profile validation. |
| **QA / Test Automation Engineer** | 1.0 | **NON-OPTIONAL:** Benchmark CI harness, BDD test suite, gate evidence automation. |
| **UX Designer** | 0.5 | Design system theme tokens, accessibility, proposal layout templates. |
| **Product Owner** | 1.0 | Sprint backlog prioritization, acceptance gate review coordination. |

---

## 8. Phase 1 Technical Risk Register

| Risk ID | Category & Description | Likelihood | Impact | Score | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1-R1** | **Benchmark Tolerance Divergence:** Physics engine fails $\pm 3\%$ annual / $\pm 5\%$ monthly tolerance on edge cases. | Medium | High | **12 (High)** | Build benchmark scaffold in Sprint 1; run cases incrementally S2–S4; allow model substitution (Perez ↔ Hay-Davies) via formal CR. |
| **P1-R2** | **Weather Data Rate Limits:** PVGIS API rate limiting or temporary downtime during bulk batch runs. | Low | Medium | **6 (Med)** | WeatherProvider abstraction caches responses in Redis/Postgres; implement exponential retry with local TMY fallback. |
| **P1-R3** | **Provenance Envelope Regression:** API endpoint bypasses repository layer and returns un-enveloped results. | Low | High | **10 (High)** | CI test enforces envelope presence on $100\%$ of calculation endpoints from Sprint 1 commit onward. |
| **P1-R4** | **Refusal Safeguard Silent Degradation:** Incomplete profile allows auto-approval under delivery pressure. | Medium | High | **12 (High)** | CI test asserts no code path can return `APPROVED` status when required profile field is null; Gate Criterion G4. |
| **P1-R5** | **Fabricated Catalog Data Ingestion:** Unverified module/inverter datasheets enter database catalog. | Low | High | **10 (High)** | Ingest pipeline strictly rejects any catalog entry missing source URL or validation timestamp; Gate Criterion G9. |

---

## 9. Acceptance Gate Criteria (G1–G10)

| Gate ID | Criterion Name | Specific Acceptance Threshold & Verification Evidence |
| :--- | :--- | :--- |
| **G1** | **Workflow Speed** | A residential sales user completes address entry $\rightarrow$ signed-ready proposal in $< 30 \text{ min}$ working time. *Evidence: Recorded walkthrough + timed test script.* |
| **G2** | **10 Physics Benchmarks** | All 10 benchmark cases pass within $\pm 3\%$ on annual yield (P50) and $\pm 5\%$ on monthly yield vs. PVsyst/SAM. *Evidence: Benchmark report with per-case deltas.* |
| **G3** | **Provenance Envelope** | Provenance envelope present on $100\%$ of persisted calculation results. *Evidence: CI test output + DB audit query.* |
| **G4** | **Refusal Safeguard** | Refusal-to-guess blocks auto-approval when any required profile field is null. *Evidence: BDD test output.* |
| **G5** | **Weather Metadata** | Weather metadata (**source name, vintage/TMY year range, spatial resolution, override status**) printed in every report. *Evidence: Sample PDF/DOCX reports.* |
| **G6** | **Report White-Labeling** | Section toggles and white-label branding fully functional in proposal output. *Evidence: Sample exports with toggles on/off and custom logos.* |
| **G7** | **RTL Architecture** | RTL-ready layout verified via `dir="rtl"` snapshot test without broken components. *Evidence: Automated snapshot test output.* |
| **G8** | **Marketing Language Audit** | A9 marketing-language audit clean across all new codebase files and report templates. *Evidence: Audit script output (0 hits).* |
| **G9** | **Catalog Data Integrity** | No fabricated equipment data — every catalog entry has a verified source URL and timestamp. *Evidence: Catalog ingest log.* |
| **G10** | **Topology Completeness** | Off-grid and hybrid paths produce valid string + battery sizing and proposals. *Evidence: End-to-end test runs for off-grid & hybrid sites.* |

---

## 10. Definition of Done (Phase 1)

1. All 10 acceptance gate criteria (G1–G10) are evidenced and signed off in the gate review meeting.
2. The specification suite v1.0.0 has not been modified outside the CR protocol.
3. A user can complete a residential on-grid, off-grid, and hybrid project end-to-end.
4. The calculation engine is frozen at a versioned release (`calc-v1.0.0`) and benchmark harness runs in CI on every commit.
5. Staging environment is deployable via Helm chart from clean checkout.
6. A Phase 2 readiness memo is produced listing C&I-specific deltas for Phase 2 kickoff.

---

## 11. Explicit Exclusions (Restated for the Record)

Phase 1 explicitly excludes: C&I workflows, Utility-Scale workflows, MV/HV collection design, substation design, upstream grid analysis, bay/voltage auto-recommenders, central inverter architecture, MV transformers, SCADA, protection relay settings, bankable Monte Carlo uncertainty, SolarGIS/NSRDB/Meteonorm adapters, procurement/RFQ/logistics, AI Copilot, multi-currency, full Android offline design, commissioning and IV-curve testing, CRM/ERP/BIM integrations, and full digital signature workflows.
