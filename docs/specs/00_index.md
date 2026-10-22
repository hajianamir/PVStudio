# 00: Specification Index, Glossary & Navigation Hub

| Version | Status | Last Updated | Owner |
| :--- | :--- | :--- | :--- |
| 1.0.0 | Approved for Engineering | 2025-02-18 | Principal Software Architect & Lead PV Engineer |

---

## 1. Document Suite Navigation Directory

| File | Document Title | Primary Scope |
| :--- | :--- | :--- |
| [`PHASE_1_RESIDENTIAL_MVP.md`](PHASE_1_RESIDENTIAL_MVP.md) | **Phase 1 Residential MVP Execution Plan** | Phase 1 Scope, Technical Foundations, 10 Benchmarks, 6-Sprint Plan, Gate Criteria |
| [`PVStudio_Technical_Product_Specification.md`](PVStudio_Technical_Product_Specification.md) | **Master Product Specification** | Executive Mandate, Architecture Summary, Cross-Segment Matrix & Master TOC |
| [`01_architecture.md`](01_architecture.md) | **System Architecture Specification** | C4 Diagrams, Modular Monolith to Microservices Roadmap, Infrastructure, Security |
| [`02_data_model.md`](02_data_model.md) | **Data Model & Database Schema** | Entity Relationship Diagrams (ERD), PostGIS/TimescaleDB Schemas, Catalog Governance |
| [`03_api_groups.md`](03_api_groups.md) | **API Groups & Endpoint Contracts** | REST Endpoint Contracts, Method/Path Tables, Request/Response Payload Specifications |
| [`04_calculation_engine.md`](04_calculation_engine.md) | **Calculation Engine & Physics Modules** | 10 Calculation Packages, Formulas, Standards References, Monte Carlo P50/P75/P90 |
| [`05_ui_ux_spec.md`](05_ui_ux_spec.md) | **UI/UX & Design System** | Design Tokens, Screen Flow Diagrams, Wizard vs Expert Mode, CesiumJS/R3F 3D Viewports |
| [`06_compliance_matrix.md`](06_compliance_matrix.md) | **Compliance Matrix & Rules Engine** | Rules-as-Data YAML Profile Schema, Regulatory Lookup Matrix (IEC/NEC/VDE/AS-NZS) |
| [`07_segment_workflows.md`](07_segment_workflows.md) | **Segment Workflows & Recommenders** | Residential, C&I, Utility Workflows, Central/String & MV Bay Auto-Recommenders |
| [`08_risk_register.md`](08_risk_register.md) | **Technical Risk Register** | Risk Severity, Impact, Mitigations, and Component Ownership |
| [`09_phased_roadmap.md`](09_phased_roadmap.md) | **Phased Delivery Plan** | Phase 1–4 Milestones, Dependency Graph, Hard Acceptance Gates |
| [`10_acceptance_tests.md`](10_acceptance_tests.md) | **Acceptance Test Catalogue** | BDD Given/When/Then Test Cases for Engine, Compliance, Workflows, and Mobile Sync |

---

## 2. Shared Technical Terms Glossary (C4)

| Term / Abbreviation | Full Technical Definition |
| :--- | :--- |
| **BESS** | Battery Energy Storage System (chemically containerized lithium-ion or flow batteries for grid/energy backup). |
| **BOM / BOQ** | Bill of Materials / Bill of Quantities (itemized list of engineering equipment, hardware, and cables). |
| **DSCR** | Debt Service Coverage Ratio ($\text{Net Operating Income} / \text{Debt Service}$). Key bankability metric. |
| **LCOE** | Levelized Cost of Electricity ($\text{Total Lifetime Cost} / \text{Total Lifetime Energy Generation}$). |
| **MPPT** | Maximum Power Point Tracking (DC-DC power optimizer algorithm in inverters). |
| **P50 / P75 / P90** | Probabilistic yield production metrics representing 50%, 75%, and 90% exceedance probability levels. |
| **PCC / POI** | Point of Common Coupling / Point of Interconnection (physical grid boundary interface). |
| **SLD** | Single-Line Diagram (schematic representation of three-phase power systems). |
| **TMY** | Typical Meteorological Year (hourly solar irradiance and weather data synthesized over multi-decade periods). |
