# 10: Acceptance Test Catalogue & Phase Gate Criteria (BDD Specifications)

| Version | Status | Last Updated | Owner |
| :--- | :--- | :--- | :--- |
| 1.0.0 | Approved for Engineering | 2025-02-18 | Lead QA & Test Engineer |

---

## 10.1 Overview & Testing Strategy

This test catalogue specifies Behavior-Driven Development (BDD) acceptance tests using the **Given / When / Then** syntax. These tests validate calculation engine precision, segment workflows, compliance safeguards, and mobile sync integrity.

---

## 10.2 BDD Acceptance Test Suite

### Scenario 1: Temperature-Adjusted String Sizing Compliance (NEC 690.7 / IEC 62548)

```gherkin
Feature: DC String Sizing Calculation Engine

  Scenario: Validating maximum string length under extreme cold conditions
    Given a PV module with Voc = 49.5 V, temp coefficient of Voc = -0.28 %/°C
    And an inverter with maximum DC voltage limit = 1000 V
    And a project site record minimum ambient temperature = -10 °C
    When the design engineer runs the calc_sizing_dc calculation engine
    Then the engine computes cell temperature adjustment delta = -35 °C
    And computes max module Voc at minimum temperature = 54.35 V
    And calculates maximum allowable modules per string = 18
    And verifies total string Voc = 978.3 V <= 1000 V
    And returns is_compliant = true with standards cited ["NEC 2020 Article 690.7"]
```

---

### Scenario 2: Central vs. String Inverter Auto-Recommender (Utility-Scale)

```gherkin
Feature: Utility-Scale Inverter Architecture Auto-Recommender

  Scenario: Recommending string inverters for high-slope terrain
    Given a utility-scale plant capacity = 25 MW
    And a site terrain slope variance = 8.5 degrees (> 5.0 degree threshold)
    And grid interconnection voltage = 33 kV
    When the user requests architecture recommendation via POST /api/v1/designs/{id}/recommend-architecture
    Then the system recommends STRING_INVERTER architecture
    And returns confidence_score >= 0.90
    And provides justification notes highlighting "Steep terrain slope favors decentralized MPPT tracking"
    And displays the manual engineer override toggle in the UI
```

---

### Scenario 3: Refusal-to-Guess Compliance Safeguard

```gherkin
Feature: Rules-as-Data Regulatory Compliance Engine

  Scenario: Refusing auto-approval when jurisdiction profile is missing
    Given a project location in a region with no active compliance YAML profile
    When the user clicks "Approve System Design"
    Then the system blocks auto-approval
    And emits a CRITICAL compliance alert banner "Regulatory profile incomplete for this region"
    And attaches a "REQUIRES QUALIFIED LOCAL PROFESSIONAL ENGINEER SIGN-OFF" watermark to generated PDFs
```

---

### Scenario 4: Offline Android Barcode Sync & Conflict Resolution

```gherkin
Feature: Mobile Field Operations Offline Synchronization

  Scenario: Syncing scanned equipment barcodes without overwriting design state
    Given an installer using the Android app in offline mode
    And the installer scans 120 module barcodes associated with String Array 4
    When the installer restores internet connectivity and triggers POST /api/v1/field-sync/barcodes
    Then the system appends barcode serial records as immutable audit event logs
    And associates serials with String Array 4 layout nodes
    And preserves existing cloud design parameters without table overwrites
```

---

### Scenario 5: Monte Carlo Yield Simulation Uncertainty Convergence

```gherkin
Feature: Bankability Yield Engine (P50/P75/P90)

  Scenario: Running 10,000 Monte Carlo iterations for utility bankability report
    Given a 50 MW utility-scale system design
    And weather dataset PVGIS TMY
    When the user triggers POST /api/v1/calc/bankability-monte-carlo with iterations = 10000
    Then the Celery worker executes 10,000 stochastic yield runs
    And computes P50 yield, P75 yield, and P90 yield
    And verifies P50 > P75 > P90
    And logs loss taxonomy categories matching PVsyst standards (soiling, IAM, wiring, clipping, degradation)
```

---

## 10.3 Phase 2 Acceptance Gate Criteria (G11–G20 Specification Table)

For Phase 2 (C&I Expansion & Procurement), the engineering team must satisfy all 10 acceptance gate criteria (G11–G20):

| Gate ID | Gate Title | Assertion Statement (What Must Be True) | Evidence Source Artifact | Verification Mode | Coverage Mapping |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **G11** | **C&I 9-Step Menu Tree** | Selecting C&I segment dynamically loads a distinct 9-step workflow tree ending in Step 9 Permit Package. | `app/ui/cand_i_workflow.py` | Automated CI (`test_cand_i_workflow.py`) | C&I Navigation Architecture |
| **G12** | **Symmetric Voltage & DC Constraint Guard** | Voltage selection applies profile ceilings (250 kW US, 100 kW EU) and `DCSizingConstraintViolation` fires on cold $V_{oc} > V_{max,dc}$ window collapse. | `calc_grid_interconnection` & `calc_sizing_dc` | Automated CI (`test_calc_sizing_dc.py`) | Grid Selection & DC Safety Guard |
| **G13** | **Substation Bay Breakdown** | MV connections automatically decompose into incomer, transformer, metering, and spare bays ($N_{total} = N_{inc} + N_{trafo} + N_{met} + N_{spare}$). | `calc_grid_interconnection` | Automated CI (`test_calc_grid_interconnection.py`) | Substation Design |
| **G14** | **MV Protection & Relaying** | MV breakers, CT primary ratios, and ANSI 50/51/51N numerical relay functions are sized per IEEE C37.2 / IEC 60255. | `calc_protection` | Automated CI (`test_sprint3_cand_i_extensions.py`) | Protection Coordination |
| **G15** | **IEC 60909 Short-Circuit Fault Current** | Short-circuit current $I_k''$ is calculated per IEC 60909 with voltage factor $c=1.10$ and $0.5\text{--}30\text{ kA}$ sanity range warnings. | `calc_grid_interconnection` | Automated CI (`test_750kw_cand_i_end_to_end.py`) | Fault Current Analysis |
| **G16** | **Civil Pad Design & Diagnostic Banners** | Transformer pad dimensions, concrete volume, wind overturning ($S.F. \ge 1.5$), and trench depth render visible geotech/wind warnings on SVG title block and brief. | `calc_civil` & `PermitPackageGeneratorService` | Automated CI (`test_sprint4_cand_i_deliverables.py`) | Substation Civil Scope & Banner Rendering |
| **G17** | **Procurement BOQ & RFQ** | Line-item BOQ export contains unit costs, extended costs, equipment quantities, category rollups, and text-layer RFQ generation. | `app/services/rfq_service.py` | Automated CI (`test_sprint4_cand_i_deliverables.py`) | Equipment Procurement |
| **G18** | **Dual Proposal Booklet** | Proposal engine renders distinct Client Executive Proposal and AHJ Permit Package sections with visible diagnostic warning banners. | `app/services/cand_i_proposal_generator.py` | Automated CI (`test_sprint4_cand_i_deliverables.py`) | Reporting & Proposal Export |
| **G19** | **2-Stage PE Governance** | Design overrides require two distinct users (`proposer != approver_pe`), active status, license expiry checks, and ISO 3166-2 jurisdiction match. | `calc/compliance/checker.py` | Automated CI (`test_compliance_refusal.py`) | Regulatory Governance |
| **G20** | **750 kW End-to-End Export** | Complete 750 kW C&I design run passes all 9 steps, Phase 1 regressions, and produces a vector SVG SLD diagram with equipment node assertions. | `tests/test_750kw_cand_i_end_to_end.py` | Automated CI & Manual Audit | Full C&I Pipeline |

---

## 10.4 Acceptance Gate Evidence Templates (B6)

To pass each phase acceptance gate, the engineering team must submit the corresponding formal evidence package:

| Phase Gate | Evidence Artifact Required | Validation Threshold / Criterion |
| :--- | :--- | :--- |
| **Phase 1 Gate** | Benchmark Comparison Report | 10 reference cases executed against PVsyst/SAM with relative yield error $\le 1.5\%$. |
| **Phase 2 Gate** | C&I Permit Package Audit | Permit-ready SLD, three-line diagram, and complete BOM generated for a 1 MW plant (G11–G20). |
| **Phase 3 Gate** | Bankability Audit Booklet | End-to-end Utility-Scale plant output containing Monte Carlo P50/P75/P90 and DSCR model. |
| **Phase 4 Gate** | AI Copilot Error Suite Audit | AI Copilot detects $\ge 80\%$ of 50 intentionally introduced design errors with exact standard citations. |
