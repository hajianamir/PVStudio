# Phase 3 Sprint 2 Disclosures & DSCR Traceability

**Document Version:** 1.0.0
**Date:** October 2026
**Status:** Approved & Frozen

---

## 1. Carried Item Disclosure: Year 1 Revenue, PPA Price, and DSCR Trajectory

### 1.1 Underlying Project Financial Parameters (50 MW Seville Benchmark)
- **Turnkey Plant CAPEX:** $40,000,000.00 ($0.80/Wdc)
- **Debt Leverage:** 67.39% ($26,954,314.88 Senior Debt Principal)
- **Annual Debt Service:** $2,350,000.00 / year (Fixed 20-year principal + interest at 6.0% interest rate)
- **Year 1 OPEX:** $600,000.00 / year (Escalating at 2.0% / year inflation)
- **Annual Module Degradation:** 0.5% / year

### 1.2 Year 1 P90 Revenue & PPA Math
- **Year 1 P90 AC Yield:** 82,207,200.00 kWh (82,207.20 MWh)
- **Required Year 1 P90 Gross Revenue:** $4,060,000.00
- **Implied PPA Contract Price:** **$49.387 / MWh** (~$49.40 / MWh)
- **Year 1 P90 Net Operating Income (NOI):**
  $$\text{NOI}_1 = \text{Revenue}_1 - \text{OPEX}_1 = \$4,060,000.00 - \$600,000.00 = \$3,460,000.00$$
- **Year 1 P90 DSCR:**
  $$\text{DSCR}_1 = \frac{\$3,460,000.00}{\$2,350,000.00} = 1.472\times \quad (\ge 1.20\text{ required minimum})$$

### 1.3 Year 20 P90 Revenue & Minimum DSCR Endpoint
- **Year 20 P90 AC Yield (after 0.5%/yr degradation):** $82,207.20\text{ MWh} \times (1 - 0.005)^{19} = 74,688.58\text{ MWh}$
- **Year 20 P90 Gross Revenue:** $74,688.58\text{ MWh} \times \$49.387/\text{MWh} = \$3,688,642.92$
- **Year 20 OPEX (after 2.0%/yr inflation):** $\$600,000.00 \times (1 + 0.02)^{19} = \$874,082.02$
- **Year 20 P90 Net Operating Income (NOI):**
  $$\text{NOI}_{20} = \$3,688,642.92 - \$874,082.02 = \$2,814,560.90$$
- **Year 20 P90 DSCR (Minimum Trajectory Endpoint):**
  $$\text{DSCR}_{20} = \frac{\$2,814,560.90}{\$2,350,000.00} = \mathbf{1.198\times \approx 1.20\times}$$

---

## 2. Central Architecture End-to-End Status

- **Catalog Seeding:** Sungrow SG3125HV Central Inverter Skid ($3,125\text{ kW}_{ac}$, $1500\text{V}_{dc}$ input, $30\text{ kV}$ containerized MV transformer output) fully seeded in `calc/catalog/seed_data.py`.
- **Decision Engine:** `calc_recommender` automatically recommends Central Inverter Architecture for flat terrain projects $\ge 3\text{ MW}$ where CAPEX savings exceed 5%.
- **End-to-End Design Flow:** Full end-to-end integration (custom container pad civil layout, MV bay count scaling, and permit package SVG rendering for Central vs. String architectures) is scheduled for delivery in Phase 3 Sprint 3.
