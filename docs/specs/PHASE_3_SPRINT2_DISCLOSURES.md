# Phase 3 Sprint 2 & 3 Disclosures, DSCR Schedule & Policy Rationales

**Document Version:** 1.1.0
**Date:** October 2026
**Status:** Approved & Frozen

---

## 1. DSCR Traceability & PPA Price Math

### 1.1 Project Sizing & Financial Parameters (50 MW Seville Benchmark)
- **Turnkey Plant CAPEX:** $40,000,000.00 ($0.80/Wdc)
- **Debt Leverage:** 67.39% ($26,954,314.88 Senior Debt Principal)
- **Annual Debt Service:** $2,350,000.00 / year (Fixed 20-year principal + interest at 6.0% interest rate)
- **Year 1 OPEX:** $600,000.00 / year (Escalating at 2.0% / year inflation)
- **Annual Module Degradation:** 0.5% / year
- **P90 AC Yield Basis:** **82,160,060.39 kWh** (82,160.06 MWh)
- **PPA Contract Price:** **$50.00 / MWh** ($0.050 / kWh)

### 1.2 Year 1 P90 Revenue & NOI Math
- **Year 1 Gross P90 Revenue:** $82,160.06\text{ MWh} \times \$50.00/\text{MWh} = \$4,108,003.02$
- **Year 1 Net Operating Income (NOI):**
  $$\text{NOI}_1 = \$4,108,003.02 - \$600,000.00 = \$3,508,003.02$$
- **Year 1 P90 DSCR:**
  $$\text{DSCR}_1 = \frac{\$3,508,003.02}{\$2,350,000.00} = \mathbf{1.4928\times \approx 1.49\times}$$

### 1.3 Debt Conservatism Rationale (1.22x vs 1.20x Minimum Endpoint)
- **Year 20 Gross P90 Revenue (0.5%/yr degradation):** $74,696.33\text{ MWh} \times \$50.00/\text{MWh} = \$3,734,816.67$
- **Year 20 OPEX (2.0%/yr inflation):** $\$600,000.00 \times (1.02)^{19} = \$874,086.70$
- **Year 20 Net Operating Income (NOI):**
  $$\text{NOI}_{20} = \$3,734,816.67 - \$874,086.70 = \$2,860,729.97$$
- **Year 20 P90 DSCR:**
  $$\text{DSCR}_{20} = \frac{\$2,860,729.97}{\$2,350,000.00} = \mathbf{1.2173\times \approx 1.22\times}$$
- **Rationale:** Debt principal is conservatively sized at $26.95M ($2.35M/yr debt service) rather than maxing out leverage at $27.36M to maintain a safety buffer ($\text{DSCR}_{20} = 1.22\times \ge 1.20\times$).

---

## 2. Complete 20-Year P90 DSCR Trajectory Table

Generated directly by `calc_bankability` Monte Carlo engine:

| Year | P90 Yield (kWh) | Gross Rev P90 ($) | OPEX ($) | Debt Service ($) | NOI P90 ($) | DSCR P90 |
|:----:|:---------------:|:-----------------:|:--------:|:----------------:|:-----------:|:--------:|
| 1 | 82,160,060.39 | $4,108,003.02 | $600,000.00 | $2,350,000.00 | $3,508,003.02 | 1.49x |
| 2 | 81,749,260.09 | $4,087,463.00 | $612,000.00 | $2,350,000.00 | $3,475,463.00 | 1.48x |
| 3 | 81,340,513.79 | $4,067,025.69 | $624,240.00 | $2,350,000.00 | $3,442,785.69 | 1.47x |
| 4 | 80,933,811.22 | $4,046,690.56 | $636,724.80 | $2,350,000.00 | $3,409,965.76 | 1.45x |
| 5 | 80,529,142.16 | $4,026,457.11 | $649,459.30 | $2,350,000.00 | $3,376,997.81 | 1.44x |
| 6 | 80,126,496.45 | $4,006,324.82 | $662,448.48 | $2,350,000.00 | $3,343,876.34 | 1.42x |
| 7 | 79,725,863.97 | $3,986,293.20 | $675,697.45 | $2,350,000.00 | $3,310,595.75 | 1.41x |
| 8 | 79,327,234.65 | $3,966,361.73 | $689,211.40 | $2,350,000.00 | $3,277,150.33 | 1.39x |
| 9 | 78,930,598.48 | $3,946,529.92 | $702,995.63 | $2,350,000.00 | $3,243,534.30 | 1.38x |
| 10 | 78,535,945.49 | $3,926,797.27 | $717,055.54 | $2,350,000.00 | $3,209,741.73 | 1.37x |
| 11 | 78,143,265.76 | $3,907,163.29 | $731,396.65 | $2,350,000.00 | $3,175,766.64 | 1.35x |
| 12 | 77,752,549.43 | $3,887,627.47 | $746,024.59 | $2,350,000.00 | $3,141,602.89 | 1.34x |
| 13 | 77,363,786.68 | $3,868,189.33 | $760,945.08 | $2,350,000.00 | $3,107,244.26 | 1.32x |
| 14 | 76,976,967.75 | $3,848,848.39 | $776,163.98 | $2,350,000.00 | $3,072,684.41 | 1.31x |
| 15 | 76,592,082.91 | $3,829,604.15 | $791,687.26 | $2,350,000.00 | $3,037,916.89 | 1.29x |
| 16 | 76,209,122.49 | $3,810,456.12 | $807,521.00 | $2,350,000.00 | $3,002,935.12 | 1.28x |
| 17 | 75,828,076.88 | $3,791,403.84 | $823,671.42 | $2,350,000.00 | $2,967,732.42 | 1.26x |
| 18 | 75,448,936.50 | $3,772,446.82 | $840,144.85 | $2,350,000.00 | $2,932,301.97 | 1.25x |
| 19 | 75,071,691.82 | $3,753,584.59 | $856,947.75 | $2,350,000.00 | $2,896,636.84 | 1.23x |
| 20 | 74,696,333.36 | $3,734,816.67 | $874,086.70 | $2,350,000.00 | $2,860,729.96 | 1.22x |

---

## 3. MENA-GCC Profile Policy & Regional Rationale

- **Grid Voltage Levels:** `[132, 220, 400]` kV transmission levels.
- **Minimum DSCR Rationale:** Set to **1.15x** based on GCC sovereign wealth and regional development bank financing terms (e.g. ACWA Power, Masdar project finance frameworks where long-term sovereign off-taker PPAs justify lower debt service coverage thresholds than merchant EU/US markets).
- **Cited Regional Grid Codes:** SEC Grid Code (Saudi Electricity Company) & DEWA Green Hydrogen / Solar Grid Code (Dubai Electricity and Water Authority).
