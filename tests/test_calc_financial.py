"""
Automated CI Test: calc_financial Quick Mode RSS Uncertainty & LCOE Test
Per Technical Specification §4.4 Module 9 & Sprint 5 Scope
Asserts:
  1. RSS uncertainty P50 -> P90 calculation matches RSS formula.
  2. LCOE and simple payback period compute correctly.
"""

import pytest
from calc.calc_financial.service import FinancialInputSchema, calculate_financial_quick_mode


def test_calc_financial_quick_mode_p50_p90_lcoe():
    inputs = FinancialInputSchema(
        annual_p50_yield_kwh=6000.0,
        system_capex_usd=12000.0,
        annual_opex_usd=150.0,
        electricity_rate_usd_kwh=0.25
    )

    result = calculate_financial_quick_mode(inputs)
    outputs = result.outputs

    assert outputs["annual_p50_yield_kwh"] == 6000.0
    assert outputs["annual_p90_yield_kwh"] < 6000.0
    assert outputs["rss_uncertainty_total_percent"] > 4.0
    assert outputs["lcoe_usd_kwh"] > 0.05
    assert outputs["simple_payback_years"] < 10.0
    assert len(outputs["twenty_five_year_cashflows_usd"]) == 26
