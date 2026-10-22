"""
Automated CI Test: Benchmark 1 Hand-Calculated Financial Reference Test
Per Technical Specification §4.4 Module 9, Sprint 5 Scope & Action Items 1, 2
Verifies calc_financial output against hand-calculated mathematical reference values for B1 inputs.
"""

import pytest
from calc.calc_financial.service import FinancialInputSchema, calculate_financial_quick_mode


def test_b1_hand_calculated_financial_reference():
    """
    Hand-Calculated B1 Reference Test:
      CAPEX: €8,500.00
      OPEX: €100.00 / year
      P50 Yield: 4,850 kWh / year
      Tariff: €0.30 / kWh
      Discount Rate: 5.0%
      Lifetime: 25 Years

    Hand Calculations:
      - Year 1 Savings = (4850 * 0.30) - 100 = €1,355.00
      - Simple Payback = 8500 / 1355 = 6.27 years -> 6.3 years
      - Total RSS Sigma = sqrt(3.5^2 + 2.5^2 + 1.5^2 + 1.0^2 + 1.0^2) = sqrt(21.75) = 4.6636% -> 4.66%
      - P90 Yield = 4850 * (1 - 1.282 * 0.046636) = 4,559.1 kWh
    """
    inputs = FinancialInputSchema(
        annual_p50_yield_kwh=4850.0,
        system_capex_usd=8500.0,
        annual_opex_usd=100.0,
        electricity_rate_usd_kwh=0.30,
        discount_rate_percent=5.0,
        degradation_annual_percent=0.5,
        project_lifetime_years=25,
        currency_symbol="€",
        profile_id="EU-DE-v1"
    )

    result = calculate_financial_quick_mode(inputs)
    outputs = result.outputs

    # Hand-Calculated Reference Assertions
    assert outputs["currency_symbol"] == "€"
    assert outputs["net_capex_usd"] == 8500.0
    assert outputs["annual_p50_yield_kwh"] == 4850.0
    assert outputs["annual_savings_year_1_usd"] == 1355.0
    assert outputs["simple_payback_years"] == 6.3
    assert outputs["rss_uncertainty_total_percent"] == 4.66
    assert abs(outputs["annual_p90_yield_kwh"] - 4559.8) <= 2.0
    assert outputs["npv_usd"] > 9000.0  # Positive NPV > €9,000 over 25 years
    assert outputs["irr_percent"] > 12.0   # Robust IRR > 12.0%
    assert 0.08 <= outputs["lcoe_usd_kwh"] <= 0.12  # LCOE ~ €0.095/kWh
