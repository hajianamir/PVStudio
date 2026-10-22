# 06: Compliance Matrix & Rules-as-Data Model Specification

| Version | Status | Last Updated | Owner |
| :--- | :--- | :--- | :--- |
| 1.0.0 | Approved for Engineering | 2025-02-18 | Lead Regulatory & Compliance Engineer |

---

## 6.1 Overview & Rules-as-Data Architecture

Regulatory standards, grid codes, and local installation rules vary across jurisdictions. PVStudio decouples regulatory logic from core application code using a **Rules-as-Data** architecture. All regulatory rules are defined as version-controlled YAML profiles stored in `compliance/profiles/*.yaml`.

---

## 6.2 Reference Regulatory Matrix

| Domain / Jurisdiction | Standard Reference | Code Area | Rule Enforced |
| :--- | :--- | :--- | :--- |
| **Baseline International** | IEC 62548 / IEC 60364-7-712 | PV Array DC Sizing | Max system voltage limits (1000V / 1500V), DC string fusing rules. |
| **Baseline International** | IEC 62305 (Parts 1–4) | Lightning & Earthing | Risk assessment score ($N_D$), target earth resistance $R_g \le 10 \, \Omega$. |
| **Baseline International** | IEC 61724-1 | Monitoring & Yield | Performance Ratio ($PR$) calculation, loss taxonomy definitions. |
| **Germany / EU (EU-DE)** | VDE-AR-N 4105 / 4120 | Grid Interconnection | LV/HV grid code, reactive power capability ($\cos \phi(P)$ curve), FRT. |
| **United States (US-NEC)** | NEC 2020 / 2023 Art. 690, 705 | Electrical Installation | Rapid Shutdown (NEC 690.12), 120% busbar rule (NEC 705.12). |
| **Australia (AU-NZ)** | AS/NZS 5033 / 4777.2 | PV Array & Inverters | DC isolator requirements, power quality response modes (Volt-Watt / Volt-VAr). |
| **MENA-GCC** | SEC Grid Code / DEWA | Interconnection (Desert) | Ambient temp sizing up to $50^\circ\text{C}$, high soiling derating factors. |

---

## 6.3 Rules-as-Data Schema Example (`compliance/profiles/US-NEC-2020-v1.yaml`)

```yaml
profile_id: "US-NEC-2020-v1"
market: "United States"
jurisdiction: "US-NEC"
version: "1.0.0"
effective_date: "2020-01-01"

dc_system:
  max_voltage_residential_v: 600
  max_voltage_commercial_v: 1000
  max_voltage_utility_v: 1500
  temperature_correction_standard: "NEC_690_7_TABLE"
  rapid_shutdown_required: true
  rapid_shutdown_boundary_inches: 12
  rapid_shutdown_max_volts_inside_boundary: 80
  rapid_shutdown_time_limit_sec: 30

ac_interconnection:
  busbar_120_percent_rule_enabled: true
  feeder_125_percent_rule_enabled: true
  neutral_conductor_sizing: "FULL_RATED"

protection:
  dc_fuse_multiplier_min: 1.56
  dc_fuse_multiplier_max: 2.40
  spd_type_required: "TYPE_1_OR_TYPE_2"

standards_citations:
  - "NEC 2020 Article 690.7 (Voltage Correction)"
  - "NEC 2020 Article 690.12 (Rapid Shutdown)"
  - "NEC 2020 Article 705.12 (Point of Connection)"
```

---

## 6.4 Refusal-to-Guess Safeguard Mechanism (Hard Requirement)

If a user configures a project in a jurisdiction where the regulatory profile is missing, incomplete, or contains unvalidated rules:

1. **Hard Refusal:** The system strictly refuses auto-approval of the system design.
2. **UI Alert Banner:** The system displays an un-dismissable alert: `CRITICAL: Regulatory profile incomplete for this region. Automatic design sign-off is disabled.`
3. **Draft Watermarking:** Generated proposal PDFs, SLDs, and reports are watermarked with: **"REQUIRES QUALIFIED LOCAL PROFESSIONAL ENGINEER SIGN-OFF"**.

---

## 6.5 AI Copilot Strict Compliance Guardrails

When AI Copilot design review features are active (Phase 4):

1. **Zero Hallucination Guarantee:** AI Copilot must not invent equipment data, datasheets, or mathematical formulas.
2. **Human Finalization Mandatory:** AI Copilot cannot finalize or sign off on critical engineering outputs without explicit human engineer review.
3. **Mandatory Standard Citations:** Every AI Copilot optimization suggestion or error flag MUST cite the exact standard clause number (e.g., *NEC 2020 Article 690.12(B)(1)* or *IEC 62305-2 Section 4.2*). Suggestions lacking standard citations are automatically filtered out.
