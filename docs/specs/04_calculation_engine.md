# 04: Calculation Engine Module Breakdown & Mathematical Specifications

| Version | Status | Last Updated | Owner |
| :--- | :--- | :--- | :--- |
| 1.0.0 | Approved for Engineering | 2025-02-18 | Lead PV & Computational Engineer |

---

## 4.1 Overview & Engine Directives

The calculation engine is a standalone, versioned, independently testable Python computational library located in `calc/`. Every calculation module adheres to strict mathematical determinism, explicit standards referencing, and input-hash traceability.

```
calc/
  calc_yield/                  # Irradiance transposition, shading, soiling, degradation
  calc_sizing_dc/              # String sizing, temperature coefficients, module-inverter matching
  calc_electrical_dc/          # DC cable sizing, voltage drop, ampacity, fusing
  calc_electrical_ac/          # AC collection, transformer sizing, cable schedules
  calc_protection/             # Breaker/fuse coordination, fault current, relay settings
  calc_grounding_lightning/    # IEC 62305 risk assessment, earthing network
  calc_civil/                  # Foundation, wind/snow/seismic, BOQ
  calc_grid_interconnection/   # PCC analysis, bay/voltage recommender, grid-code checks
  calc_financial/              # LCOE, NPV, IRR, DSCR, Monte Carlo sensitivity
  calc_recommender/            # Architecture selection, bay count, optimization
```

---

## 4.2 Weather & Irradiance Dataset Hierarchy (Mandatory Declaration)

Every yield simulation run must explicitly log and print its weather data provenance:

| Tier | Dataset Provider | Primary Use Case | Access Type |
| :--- | :--- | :--- | :--- |
| **Primary Default** | PVGIS (TMY) | Global default TMY hourly weather dataset | Free / Open REST API |
| **Validation / Secondary** | NASA POWER | Mandatory cross-check for remote/unmapped coordinates | Free / Open API |
| **Regional Premium** | NSRDB (US High-Res) / Meteonorm | Region-specific high resolution TMY data | User-selectable |
| **Licensed Commercial** | SolarGIS | Commercial high-precision bankable weather data | Bring Your Own License (BYO) |

*Reporting Constraint:* Every generated report, proposal, and simulation output MUST print:
1. Dataset name and tier
2. Data vintage / TMY year range (e.g., 2005–2020)
3. Spatial resolution (e.g., 4 km grid)
4. Override status (`Default` vs. `User-Selected`).

---

## 4.3 Two-Mode Yield & Uncertainty Calculation

The yield calculation engine supports two distinct uncertainty calculation modes:

1. **Quick Mode (Default for Residential & C&I):**
   * **Methodology:** Analytical Root-Sum-Square (RSS) error propagation across independent loss components:
     $$\sigma_{total} = \sqrt{\sigma_{irradiance}^2 + \sigma_{transposition}^2 + \sigma_{soiling}^2 + \sigma_{mismatch}^2 + \sigma_{inverter}^2}$$
   * Outputs P50 and P90 yield estimates deterministically in $< 100 \text{ ms}$.

2. **Bankable Mode (Mandatory for Utility-Scale):**
   * **Methodology:** Stochastic Monte Carlo simulation with $\ge 10,000$ iterations sampling from per-parameter statistical distributions:
     * Inter-annual irradiance variability: Normal distribution $\mathcal{N}(\mu_{ghi}, \sigma_{ghi})$
     * Weather model error: Normal distribution
     * Soiling loss rate: Triangular distribution
     * Degradation rate: Normal distribution bounded by manufacturer warranty floor
   * Outputs P50, P75, and P90 yield probability distributions, confidence intervals, and a contribution tornado chart.
   * Mirrors PVsyst loss taxonomy (IAM, soiling, mismatch, DC/AC wiring, inverter efficiency, transformer, availability, degradation, clipping, curtailment).

---

## 4.4 Module Detailed Specifications

### Module 1: `calc_yield` — Physics & Yield Engine

* **Standards Referenced:** IEC 61724-1, Perez 1990 Irradiance Model, PVLib Python.
* **Mathematical Formulations:**
  * **Transposition (Plane-of-Array Irradiance $E_{poa}$):**
    $$E_{poa} = E_{b} \cdot R_b + E_{d,iso} \cdot \left(\frac{1 + \cos \beta}{2}\right) + E_{d,ani} + E_{ground} \cdot \alpha_{alb} \left(\frac{1 - \cos \beta}{2}\right)$$
  * **Cell Temperature ($T_{cell}$):**
    $$T_{cell} = T_{amb} + \frac{E_{poa}}{U_0 + U_1 \cdot v_{wind}}$$
  * **DC Power Output ($P_{dc}$):**
    $$P_{dc} = N_{mod} \cdot P_{mp,stc} \cdot \left(\frac{E_{poa}}{1000}\right) \cdot \left[ 1 + \gamma_{pmp} (T_{cell} - 25) \right] \cdot \eta_{soiling} \cdot \eta_{iam} \cdot \eta_{mismatch}$$
* **Input Schema:** $E_{b}, E_{d}, T_{amb}, v_{wind}, \beta, \gamma, \gamma_{pmp}, P_{mp,stc}, N_{mod}, \alpha_{alb}$.
* **Output Schema:** $E_{poa}, T_{cell}, P_{dc}, P_{ac}$, annual yield ($kWh/kWp$), Specific Yield, Performance Ratio ($PR$).

---

### Module 2: `calc_sizing_dc` — String Sizing & Voltage Matching

* **Standards Referenced:** IEC 62548 §7.2, NEC 2020 Article 690.7.
* **Mathematical Formulations:**
  * **Maximum String Open-Circuit Voltage ($V_{oc,max}$):**
    $$V_{oc,max} = N_{string} \cdot V_{oc,stc} \cdot \left[ 1 + \frac{\beta_{voc}}{100} \cdot (T_{min} - 25) \right]$$
  * **Minimum String MPPT Voltage ($V_{mppt,min}$):**
    $$V_{mppt,min} = N_{string} \cdot V_{mp,stc} \cdot \left[ 1 + \frac{\gamma_{pmp}}{100} \cdot (T_{max} - 25) \right]$$
* **Constraint Rules:**
  1. $V_{oc,max} \le V_{dc,max,inverter}$ AND $V_{oc,max} \le V_{dc,max,system}$ (e.g., 1000V or 1500V).
  2. $V_{mppt,min} \ge V_{mppt,min,inverter}$.
  3. $V_{mppt,max} \le V_{mppt,max,inverter}$.

---

### Module 3: `calc_electrical_dc` — DC Cable Sizing & Ampacity

* **Standards Referenced:** IEC 60364-5-52, IEC 62548, NEC Article 690.8.
* **Mathematical Formulations:**
  * **Minimum Cable Current Carrying Capacity ($I_{z}$):**
    $$I_{z} \ge \frac{I_{sc,stc} \cdot 1.25 \cdot 1.25}{k_{temp} \cdot k_{grouping} \cdot k_{routing}}$$
  * **DC Voltage Drop Percentage ($\Delta V_{\%}$):**
    $$\Delta V_{\%} = \frac{2 \cdot L \cdot I_{mp} \cdot \rho}{A \cdot V_{string,nominal}} \times 100$$
    Where $\rho = 0.0178 \, \Omega \cdot mm^2/m$ (copper) or $0.0285 \, \Omega \cdot mm^2/m$ (aluminum).

---

### Module 4: `calc_electrical_ac` — AC Collection & Transformer Sizing

* **Standards Referenced:** IEC 60364-4-43, IEC 60076 (Power Transformers).
* **Mathematical Formulations:**
  * **Transformer Apparent Power Sizing ($S_{trafo,kVA}$):**
    $$S_{trafo,kVA} \ge \frac{\sum P_{ac,inverter,kW}}{\cos \phi \cdot \eta_{trafo} \cdot (1 - \text{margin}_{reserve})}$$
  * **Three-Phase AC Voltage Drop ($\Delta V_{ac,\%}$):**
    $$\Delta V_{ac,\%} = \frac{\sqrt{3} \cdot L \cdot I_{ac} \cdot (R \cos \phi + X \sin \phi)}{V_{line,nominal}} \times 100$$

---

### Module 5: `calc_protection` — Protection Coordination & Fault Currents

* **Standards Referenced:** IEC 60909 (Short-Circuit Calculation), IEC 60269-6 (gPV fuses).
* **Mathematical Formulations:**
  * **DC String Fuse Rating ($I_{n,fuse}$):**
    $$1.5 \cdot I_{sc,stc} \le I_{n,fuse} \le 2.4 \cdot I_{sc,stc}$$
  * **Maximum Short-Circuit Current ($I_{k}''$):**
    $$I_{k}'' = \frac{c \cdot U_n}{\sqrt{3} \cdot |Z_k|}$$

---

### Module 6: `calc_grounding_lightning` — Lightning Risk & Earthing (IEC 62305)

* **Standards Referenced:** IEC 62305-2 (Risk Management), IEC 62305-3 (Physical Damage).
* **Mathematical Formulations:**
  * **Lightning Strike Frequency ($N_D$):**
    $$N_D = N_g \cdot A_d \cdot C_d \times 10^{-6} \quad [\text{events/year}]$$
  * **Earth Grid Resistance ($R_g$ - Laurent-Niemann formula):**
    $$R_g = \rho_s \cdot \left( \frac{1}{4r} + \frac{1}{L_{total}} \right)$$
    Where $r = \sqrt{\frac{Area}{\pi}}$, target impedance $R_g \le 10 \, \Omega$.

---

### Module 7: `calc_civil` — Foundation, Grading & Civil BOQ

* **Standards Referenced:** Eurocode 1 (EN 1991-1-4 Wind, EN 1991-1-3 Snow), ASCE 7-16.
* **Mathematical Formulations:**
  * **Uplift Wind Force ($F_{w,uplift}$):**
    $$F_{w,uplift} = q_p(z) \cdot C_{p,net} \cdot A_{table}$$
  * **Minimum Pile Embedment Depth ($D_{embed}$):**
    $$D_{embed} \ge \frac{F_{w,uplift} \cdot SF_{safety}}{\pi \cdot d_{pile} \cdot \tau_{skin,friction}}$$

---

### Module 8: `calc_grid_interconnection` — Bay Count & Voltage Level Auto-Recommender

* **Standards Referenced:** IEEE 1547-2018, EN 50549-1/-2, VDE-AR-N 4110/4120.
* **Upstream Grid Data Sources:** National TSO/DSO APIs, OpenStreetMap power layer, and user-provided grid impedance files. Fallback to default conservatism profile if unavailable.
* **Mathematical Auto-Sizing Rules:**

$$\text{Interconnection Voltage } V_{pcc} = \begin{cases}
0.4 \text{ kV (LV)} & \text{if } P_{plant} < 250 \text{ kW} \\
11-33 \text{ kV (MV)} & \text{if } 250 \text{ kW} \le P_{plant} \le 20 \text{ MW} \\
110-220 \text{ kV (HV)} & \text{if } P_{plant} > 20 \text{ MW}
\end{cases}$$

$$\text{MV Feeder Bay Count } N_{bays} = \left\lceil \frac{I_{total,ac,MV}}{I_{bay,max,ampacity}} \right\rceil + N_{spare,bays}$$

---

### Module 9: `calc_financial` — Multi-Currency, Tariffs & Monte Carlo Financial Engine

* **Standards Referenced:** IEC 61724-1, PVsyst loss taxonomy.
* **Multi-Currency & Tariff Structure:**
  * Multi-currency support with exchange rates frozen in snapshot.
  * Tariff types: Time-of-Use (TOU), Feed-in Tariff (FiT), Net Metering, Capacity Payments.
  * Jurisdiction tax & depreciation models (MACRS, straight-line, tax credits).
* **Formulas:**
  $$\text{LCOE} = \frac{\text{CAPEX} + \sum_{t=1}^N \frac{\text{OPEX}_t}{(1+r)^t}}{\sum_{t=1}^N \frac{\text{Yield}_t}{(1+r)^t}}$$
  $$\text{DSCR}_t = \frac{\text{Net Operating Income}_t}{\text{Debt Service}_t}$$

---

### Module 10: `calc_recommender` — Central vs. String Inverter Decision Engine

* **Auto-Recommender Decision Matrix:**

```
Central Inverter Score S_central = w1 * FlatnessScore + w2 * CapacityScaleScore - w3 * GranularMPPTNeed
String Inverter Score S_string   = w1 * TerrainIrregularity + w2 * GranularMPPTNeed + w3 * RedundancyValue
```

* **Threshold Trigger:**
  * If Plant Capacity $> 50 \text{ MW}$ AND Terrain Slope $< 3^\circ \implies$ **Central Inverter Recommended**.
  * If Terrain Slope $> 5^\circ$ OR BESS DC-Coupling requested $\implies$ **String Inverter Recommended**.

---

## 4.5 Python Interface & Pydantic Schema Code Snippet

```python
"""
PVStudio Calculation Package: calc_sizing_dc
Interface Contract & Pydantic Schema Definition
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class DCSizingInputSchema(BaseModel):
    v_oc_stc: float = Field(..., gt=0, description="Module Open-Circuit Voltage at STC [V]")
    v_mp_stc: float = Field(..., gt=0, description="Module Maximum Power Voltage at STC [V]")
    temp_coeff_voc_percent: float = Field(..., lt=0, description="Temperature coefficient of Voc [%/°C]")
    temp_coeff_pmp_percent: float = Field(..., lt=0, description="Temperature coefficient of Pmp [%/°C]")
    site_temp_min_c: float = Field(..., ge=-60, le=50, description="Record minimum ambient temperature at site [°C]")
    site_temp_max_c: float = Field(..., ge=10, le=65, description="Record maximum ambient temperature at site [°C]")
    inverter_v_max_dc: float = Field(..., gt=0, description="Inverter maximum allowable DC voltage [V]")
    inverter_v_mppt_min: float = Field(..., gt=0, description="Inverter minimum MPPT voltage [V]")
    inverter_v_mppt_max: float = Field(..., gt=0, description="Inverter maximum MPPT voltage [V]")
    profile_id: str = Field(default="US-NEC-2020-v1", description="Rules-as-data compliance profile ID")


class DCSizingOutputSchema(BaseModel):
    calc_module: str = "calc_sizing_dc"
    calc_version: str = "1.0.0"
    input_hash: str
    max_modules_per_string: int = Field(..., description="Maximum allowable modules in series without exceeding V_dc_max")
    min_modules_per_string: int = Field(..., description="Minimum allowable modules in series to stay above V_mppt_min at max temp")
    v_oc_max_site_v: float = Field(..., description="Maximum string voltage calculated at minimum site temperature [V]")
    v_mppt_min_site_v: float = Field(..., description="Minimum MPPT string voltage calculated at maximum site temperature [V]")
    is_compliant: bool = Field(..., description="True if a valid string length window exists")
    standards_referenced: List[str]


def calculate_dc_string_sizing(inputs: DCSizingInputSchema) -> DCSizingOutputSchema:
    """
    Calculates temperature-adjusted string sizing limits per NEC 690.7 / IEC 62548.
    """
    # 1. Temperature-adjusted Voc at minimum site temp
    delta_t_min = inputs.site_temp_min_c - 25.0
    v_oc_mod_max = inputs.v_oc_stc * (1.0 + (inputs.temp_coeff_voc_percent / 100.0) * delta_t_min)

    max_modules = int(inputs.inverter_v_max_dc // v_oc_mod_max)

    # 2. Temperature-adjusted Vmp at maximum site temp
    delta_t_max = inputs.site_temp_max_c - 25.0
    v_mp_mod_min = inputs.v_mp_stc * (1.0 + (inputs.temp_coeff_pmp_percent / 100.0) * delta_t_max)

    import math
    min_modules = math.ceil(inputs.inverter_v_mppt_min / v_mp_mod_min)

    v_oc_max_site = max_modules * v_oc_mod_max
    v_mppt_min_site = min_modules * v_mp_mod_min

    is_valid = max_modules >= min_modules and v_oc_max_site <= inputs.inverter_v_max_dc

    return DCSizingOutputSchema(
        input_hash="hash_placeholder",
        max_modules_per_string=max_modules,
        min_modules_per_string=min_modules,
        v_oc_max_site_v=round(v_oc_max_site, 2),
        v_mppt_min_site_v=round(v_mppt_min_site, 2),
        is_compliant=is_valid,
        standards_referenced=["NEC 2020 Article 690.7", "IEC 62548 Section 7.2"]
    )
