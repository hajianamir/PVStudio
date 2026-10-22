# Specification Suite Changelog

| Version | Release Date | Status | Approved By |
| :--- | :--- | :--- | :--- |
| **v1.0.0** | 2025-02-18 | FINAL — Frozen | Lead PV Engineer & Software Architect |

---

## [1.0.0] - 2025-02-18

### CR-000: Documentation Hygiene & Derived Execution Document Registration

* Registered derived execution document `docs/specs/PHASE_1_RESIDENTIAL_MVP.md` as a subordinate engineering execution plan (non-authoritative, subordinate to frozen v1.0.0 master spec).
* Standardized version tag across all specification documents to canonical Semantic Versioning `Version: 1.0.0`.
* Reconciled file count references across handover note, changelog, and executive summary (17 total files: 16 files in `docs/specs/` + 1 root index `SPECIFICATION.md`).
* Locked and frozen specification suite under git tag `spec-v1.0-final`.

---

### Initial Release — Production Technical Product Specification Suite

This initial release delivers the complete, implementation-ready Technical Product Specification for **PVStudio** — an integrated Solar Design, EPC, Grid & Bankability Platform.

#### Key Deliverables & Scope Included
* **Master Specification & Index:** `PVStudio_Technical_Product_Specification.md`, `EXECUTIVE_SUMMARY.md`, `SPECIFICATION.md`, `HANDOVER.md`.
* **System Architecture (`01_architecture.md`):** C4 diagrams (Levels 1–3), Modular Monolith with Phase 3 microservices extraction path (`/svc/yield`, `/svc/electrical`, `/svc/grid`, `/svc/financial`), Celery job orchestration, disaster recovery RPO/RTO budgets, Keycloak OIDC RBAC.
* **Data Model (`02_data_model.md`):** Relational PostgreSQL schemas, PostGIS geospatial tables, TimescaleDB 8760 hypertables, calculation audit trail ERD, equipment catalog governance.
* **API Contracts (`03_api_groups.md`):** REST API endpoints across 5 domain groups, OpenAPI 3.1 YAML contracts, digital signature review endpoints, rate limits.
* **Calculation Engine (`04_calculation_engine.md`):** Mathematical formulations and Pydantic schemas for 10 Python computational packages, weather dataset hierarchy (PVGIS, NASA POWER, NSRDB, SolarGIS), two-mode yield engine (Quick RSS vs. Bankable Monte Carlo $\ge 10,000$ iterations), multi-currency/tariff financial engine.
* **UI/UX & Design System (`05_ui_ux_spec.md`):** Engineering cockpit design system, calculation transparency side-panels, Wizard vs Expert mode toggle, CesiumJS/R3F 3D viewports, customizable report booklets (PDF/DOCX), Android offline field performance budget, RTL-ready i18n architecture.
* **Compliance Matrix (`06_compliance_matrix.md`):** Rules-as-data model (`compliance/profiles/*.yaml`), reference regulatory profiles (EU-DE, US NEC 2020/2023, AU-NZ, MENA-GCC), hard refusal-to-guess safeguard, AI Copilot strict guardrails.
* **Segment Workflows (`07_segment_workflows.md`):** Divergent workflows for Residential (<10kW), C&I (<1MW), and Utility-Scale (>1MW). Central vs. String Inverter decision tree auto-recommender, MV feeder bay count and voltage level auto-sizing rules, structural distinction for Utility-Scale optional BESS grid services.
* **Risk Register (`08_risk_register.md`):** Comprehensive technical, computational, regulatory, operational, and financial risk matrix.
* **Phased Roadmap (`09_phased_roadmap.md`):** 28-month 4-phase delivery plan with Gantt chart and hard acceptance gates.
* **Acceptance Tests (`10_acceptance_tests.md`):** BDD Given/When/Then test catalogue and formal acceptance gate evidence templates.
