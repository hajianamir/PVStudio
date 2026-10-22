# PVStudio — Technical Executive Summary

```
Version: 1.0.0
Status: FINAL — Approved [2025-02-18]
Change Control: Frozen. Any change requires a v1.1 change request.
```

---

## 1. What PVStudio Is

**PVStudio** is an integrated, multi-segment solar PV design, engineering, procurement, grid-interconnection, and bankability platform. It serves three market segments through divergent workflows, automated layout and electrical sizing engines, rules-as-data compliance profiles, and a 10,000-iteration Monte Carlo yield engine.

---

## 2. Market Segments & Workflows Summary

| Segment | Capacity Scale | Focus Workflows & Layout Paradigm | Key Electrical Scope |
| :--- | :--- | :--- | :--- |
| **Residential** | $< 10 \text{ kW}$ | Design-around-the-sale, roof-plane geometry, obstacle avoidance, homeowner sales proposals. | String/micro-inverter matching, main panel 120% rule, battery storage core sizing. |
| **Commercial & Industrial (C&I)** | $< 1 \text{ MW}$ | Permit-ready 3D roof/ground layout, string routing, BOM/BOQ generation, RFQ procurement. | LV/MV AC collection, protection coordination, transformer sizing, C&I BESS. |
| **Utility-Scale** | $> 1 \text{ MW}$ | Terrain-following layout, central vs. string inverter auto-recommender, MV bay count auto-sizing, bankability reporting. | MV collection, HV substation design, SCADA, IEC 62305 earthing, optional grid-services BESS. |

---

## 3. Phased Roadmap & Hard Acceptance Gates

| Phase | Timeline | Primary Technical Scope | Hard Acceptance Gate Criteria |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Months 0–6 | Core Engine, Auth, Roof Layout, Residential MVP | Proposal generated in $<30$ min; engine error $\le 1.5\%$ vs. PVsyst. |
| **Phase 2** | Months 6–12 | C&I Workflows, Protection, BOM/BOQ, Procurement | Permit-ready SLD for 1 MW plant; active RFQ generated and tracked. |
| **Phase 3** | Months 12–20 | Microservices Extraction, Utility Grid, Monte Carlo | End-to-end Utility design with MV bay auto-sizing & P50/P75/P90 report. |
| **Phase 4** | Months 20–28 | Android Field Operations & AI Copilot | Android offline sync without data loss; AI flags $\ge 80\%$ design errors. |

---

## 4. Primary Technology Stack Summary

| Layer | Technical Stack Choice |
| :--- | :--- |
| **Frontend Web** | React 18, TypeScript, Tailwind CSS, shadcn/ui, CesiumJS (3D terrain), React Three Fiber (racking). |
| **Mobile App** | React Native (Android offline-first, SQLite, camera barcode scanner). |
| **Core API Gateway** | Python 3.11, FastAPI, Pydantic v2, Keycloak OIDC JWT RBAC. |
| **Calculation Engine** | Python (`calc/` modular packages), PVLib, NumPy, SciPy, Numba, Pandapower. |
| **Databases** | PostgreSQL 15+ (relational), PostGIS (geospatial), TimescaleDB (8760 hourly time-series). |
| **Task Queue & Infrastructure**| Redis, Celery workers, Docker, Kubernetes + Helm, Terraform, AWS/Azure. |

---

## 5. Regulatory Compliance Profiles Covered (v1.0.0)

* **EU-DE:** Germany / European baseline (VDE-AR-N 4105 LV, VDE-AR-N 4120 HV, EN 50549).
* **US-NEC:** United States (NEC 2020 default, NEC 2023 toggle — Art. 690, 705, 250; UL 1741 SB; IEEE 1547).
* **AU-NZ:** Australia / New Zealand (AS/NZS 4777.2, AS/NZS 5033, AS/NZS 1170).
* **MENA-GCC:** Saudi Arabia / UAE (SEC Grid Code, DEWA/ADDC interconnection standards).

---

## 6. Explicitly Out-of-Scope Items (v1.0.0 Specification Run)

* Executable code implementation (other than illustrative schema/interface stubs).
* Live database migrations or populated commercial equipment catalogs.
* CI/CD deployment execution on live cloud resources.

---

## 7. Sub-Specification Navigation Directory

* [`00_index.md`](00_index.md) — Specification navigation hub & technical glossary.
* [`01_architecture.md`](01_architecture.md) — System C4 architecture, microservices extraction, Celery orchestration, disaster recovery.
* [`02_data_model.md`](02_data_model.md) — PostgreSQL/PostGIS schemas, TimescaleDB hypertables, calculation audit ERD.
* [`03_api_groups.md`](03_api_groups.md) — REST endpoint contracts, OpenAPI 3.1 contracts, rate limits, digital signatures.
* [`04_calculation_engine.md`](04_calculation_engine.md) — Mathematical formulas, weather dataset hierarchy, Monte Carlo yield engine.
* [`05_ui_ux_spec.md`](05_ui_ux_spec.md) — Design system, transparency side-panel, report booklets, Android mobile performance budget.
* [`06_compliance_matrix.md`](06_compliance_matrix.md) — Rules-as-data YAML profiles, refusal-to-guess safeguard, AI Copilot guardrails.
* [`07_segment_workflows.md`](07_segment_workflows.md) — Segment workflows, central/string decision tree, MV collection bay auto-sizing rules.
* [`08_risk_register.md`](08_risk_register.md) — Technical, computational, and regulatory risk scoring and mitigations.
* [`09_phased_roadmap.md`](09_phased_roadmap.md) — 28-month delivery Gantt chart and hard acceptance gates.
* [`10_acceptance_tests.md`](10_acceptance_tests.md) — BDD Given/When/Then test catalogue and acceptance gate evidence templates.
