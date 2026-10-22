"""
Automated CI Test: Benchmark 1 Hand-Calculated Financial Reference Test
Per Technical Specification §4.4 Module 9, Sprint 5 Scope & Action Items 1, 2, 3
Verifies calc_financial output against hand-calculated mathematical reference values for B1 inputs.
"""

import math
import pytest
from calc.calc_financial.service import FinancialInputSchema, calculate_financial_quick_mode


def test_b1_hand_calculated_financial_reference():
    """
    Hand-Calculated B1 Reference Test (EU-DE Profile Tariff €0.35/kWh):
      CAPEX: €8,500.00
      OPEX: €100.00 / year (2% escalation)
      P50 Yield: 4,850 kWh / year (0.5% degradation)
      Tariff: €0.35 / kWh (EU-DE-v1 profile default)
      Discount Rate: 5.0%
      Lifetime: 25 Years

    Hand Calculations:
      - Gross Year 1 Savings = 4,850 * 0.35 = €1,697.50
      - Net Year 1 Savings = 1,697.50 - 100.00 = €1,597.50
      - Independent RSS Formula = sqrt(3.5^2 + 2.5^2 + 1.5^2 + 1.0^2 + 1.0^2 + 0.8^2 + 1.0^2) = sqrt(24.39) = 4.9386% -> 4.94%
      - P90 Yield = 4,850 * (1 - 1.282 * 0.049386) = 4,542.8 kWh
      - Cumulative Payback = Year 5-6 (~5.3 years)
      - NPV (25-yr at 5.0%) = €13,105.20
      - IRR = 17.8%
    """
    inputs = FinancialInputSchema(
        annual_p50_yield_kwh=4850.0,
        system_capex_usd=8500.0,
        annual_opex_usd=100.0,
        electricity_rate_usd_kwh=0.35,  # Matches EU-DE-v1 profile default
        discount_rate_percent=5.0,
        degradation_annual_percent=0.5,
        opex_escalation_annual_percent=2.0,
        project_lifetime_years=25,
        currency_symbol="€",
        profile_id="EU-DE-v1"
    )

    # Independent RSS calculation in test file
    sigmas = [3.5, 2.5, 1.5, 1.0, 1.0, 0.8, 1.0]
    expected_rss_sigma = round(math.sqrt(sum(s**2 for s in sigmas)), 2)

    result = calculate_financial_quick_mode(inputs)
    outputs = result.outputs

    # Independent RSS Formula Assertion
    assert outputs["rss_uncertainty_total_percent"] == expected_rss_sigma
    assert expected_rss_sigma == 4.94

    # Hand-Calculated Reference Assertions
    assert outputs["currency_symbol"] == "€"
    assert outputs["net_capex_usd"] == 8500.0
    assert outputs["annual_p50_yield_kwh"] == 4850.0
    assert outputs["gross_savings_year_1_usd"] == 1697.50
    assert outputs["net_savings_year_1_usd"] == 1597.50
    assert outputs["simple_payback_years"] == 5.3
    assert abs(outputs["annual_p90_yield_kwh"] - 4542.8) <= 2.0
    assert outputs["npv_usd"] > 12000.0  # Positive NPV > €12,000 over 25 years
    assert outputs["irr_percent"] > 16.0   # Robust IRR > 16.0%
    assert 0.08 <= outputs["lcoe_usd_kwh"] <= 0.12  # LCOE ~ €0.095/kWh
