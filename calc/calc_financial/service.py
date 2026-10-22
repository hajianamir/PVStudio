"""
calc_financial: Quick Mode Financial & RSS Yield Uncertainty Engine
Per Technical Specification §4.4 Module 9, §4.2 RSS Uncertainty Terms & Sprint 5 Fixes
Calculates Quick mode P50/P90 yields via full 7-term RSS uncertainty propagation, LCOE, payback period, NPV, IRR, and 25-year cash flows.
"""

import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash


class FinancialInputSchema(BaseModel):
    annual_p50_yield_kwh: float = Field(default=4850.0, gt=0, description="P50 annual yield from calc_yield [kWh]")
    system_capex_usd: float = Field(default=8500.0, gt=0, description="Total turnkey system CAPEX [EUR/USD]")
    annual_opex_usd: float = Field(default=100.0, ge=0, description="Annual O&M OPEX [EUR/USD]")
    electricity_rate_usd_kwh: float = Field(default=0.35, gt=0, description="Retail electricity tariff [$/kWh or €/kWh]")
    tax_credit_incentive_usd: float = Field(default=0.0, ge=0, description="Upfront tax credit / incentive deduction")
    discount_rate_percent: float = Field(default=5.0, ge=0, le=25, description="Discount rate [%]")
    degradation_annual_percent: float = Field(default=0.5, ge=0, le=5.0, description="Annual PV degradation [%]")
    opex_escalation_annual_percent: float = Field(default=2.0, ge=0, le=10.0, description="Annual OPEX inflation escalation [%]")
    project_lifetime_years: int = Field(default=25, ge=5, le=35)
    currency_symbol: str = Field(default="€", description="Currency symbol (€ or $)")

    # RSS Uncertainty Standard Deviations [%] (All 7 Spec §4.2 Terms Included)
    sigma_interannual_percent: float = Field(default=3.5, description="Inter-annual weather variability (NSRDB/PVGIS)")
    sigma_model_percent: float = Field(default=2.5, description="Transposition & transposition model error")
    sigma_soiling_percent: float = Field(default=1.5, description="Soiling & snow derate uncertainty")
    sigma_mismatch_percent: float = Field(default=1.0, description="Module mismatch & manufacturing tolerance")
    sigma_wiring_percent: float = Field(default=1.0, description="DC/AC wiring & connection uncertainty")
    sigma_degradation_percent: float = Field(default=0.8, description="Annual degradation uncertainty")
    sigma_availability_percent: float = Field(default=1.0, description="Inverter & grid availability uncertainty")

    profile_id: str = Field(default="EU-DE-v1")


def calculate_financial_quick_mode(inputs: FinancialInputSchema) -> CalculationResult:
    # Net Initial Outlay after Tax Credit / Upfront Incentives
    net_capex = max(0.0, inputs.system_capex_usd - inputs.tax_credit_incentive_usd)

    # 1. Full 7-Term RSS Uncertainty Propagation (Spec §4.2)
    # sigma_total = sqrt(3.5^2 + 2.5^2 + 1.5^2 + 1.0^2 + 1.0^2 + 0.8^2 + 1.0^2) = sqrt(24.39) = 4.9386% -> 4.94%
    sigma_total_percent = math.sqrt(
        inputs.sigma_interannual_percent**2 +
        inputs.sigma_model_percent**2 +
        inputs.sigma_soiling_percent**2 +
        inputs.sigma_mismatch_percent**2 +
        inputs.sigma_wiring_percent**2 +
        inputs.sigma_degradation_percent**2 +
        inputs.sigma_availability_percent**2
    )

    # P90 = P50 - 1.282 * sigma (assuming normal distribution for 90% exceedance)
    p50_kwh = inputs.annual_p50_yield_kwh
    p90_kwh = p50_kwh * (1.0 - (1.282 * sigma_total_percent / 100.0))

    # 2. Year-1 Savings Definitions
    gross_savings_year_1 = p50_kwh * inputs.electricity_rate_usd_kwh
    net_savings_year_1 = gross_savings_year_1 - inputs.annual_opex_usd

    # 3. 25-Year Cashflow Simulation & NPV Calculation
    cashflows: List[float] = [-net_capex]
    discounted_yield_sum = 0.0
    discounted_cost_sum = net_capex
    npv = -net_capex

    cumulative_undiscounted_cash = -net_capex
    simple_payback_years = 99.0
    payback_found = False

    for year in range(1, inputs.project_lifetime_years + 1):
        deg_factor = (1.0 - (inputs.degradation_annual_percent / 100.0)) ** (year - 1)
        opex_esc_factor = (1.0 + (inputs.opex_escalation_annual_percent / 100.0)) ** (year - 1)

        yield_year = p50_kwh * deg_factor
        opex_year = inputs.annual_opex_usd * opex_esc_factor
        savings_year = yield_year * inputs.electricity_rate_usd_kwh
        net_cash_year = savings_year - opex_year

        cashflows.append(round(net_cash_year, 2))

        # Check cumulative payback with degradation & OPEX escalation
        prev_cum = cumulative_undiscounted_cash
        cumulative_undiscounted_cash += net_cash_year
        if not payback_found and cumulative_undiscounted_cash >= 0:
            fractional_year = abs(prev_cum) / net_cash_year
            simple_payback_years = (year - 1) + fractional_year
            payback_found = True

        discount_factor = (1.0 + (inputs.discount_rate_percent / 100.0)) ** year
        discounted_yield_sum += yield_year / discount_factor
        discounted_cost_sum += opex_year / discount_factor
        npv += net_cash_year / discount_factor

    # LCOE ($/kWh) = Total Discounted Lifetime Costs / Total Discounted Lifetime Yield (NREL Formulation)
    lcoe_usd_kwh = discounted_cost_sum / discounted_yield_sum if discounted_yield_sum > 0 else 0.0

    # IRR calculation using bisection search
    irr_percent = 0.0
    low, high = -0.5, 1.0
    for _ in range(50):
        mid = (low + high) / 2.0
        npv_mid = sum(cf / ((1.0 + mid) ** t) for t, cf in enumerate(cashflows))
        if npv_mid > 0:
            low = mid
        else:
            high = mid
    irr_percent = mid * 100.0

    inputs_dict = inputs.model_dump()
    input_hash = compute_input_hash(inputs_dict)

    provenance = ProvenanceEnvelope(
        calc_module="calc_financial",
        calc_version="1.0.0",
        input_hash=input_hash,
        profile_id=inputs.profile_id,
        standards_referenced=["IEC 61724-1 RSS Uncertainty Model", "NREL LCOE Formulation", "ASTM E2230 Standard Practice for Financial Evaluation"]
    )

    outputs = {
        "financial_parameters_declared": {
            "discount_rate_percent": inputs.discount_rate_percent,
            "degradation_annual_percent": inputs.degradation_annual_percent,
            "opex_escalation_annual_percent": inputs.opex_escalation_annual_percent,
            "lcoe_definition": "DISCOUNTED_LIFETIME_COST_DIVIDED_BY_DISCOUNTED_LIFETIME_YIELD",
            "savings_definition": "GROSS_SAVINGS = YIELD * TARIFF; NET_SAVINGS = GROSS_SAVINGS - OPEX",
            "payback_basis": "CUMULATIVE_UNDISCOUNTED_CASHFLOW_WITH_DEGRADATION"
        },
        "currency_symbol": inputs.currency_symbol,
        "net_capex_usd": round(net_capex, 2),
        "annual_p50_yield_kwh": round(p50_kwh, 2),
        "annual_p90_yield_kwh": round(p90_kwh, 2),
        "p90_p50_ratio": round(p90_kwh / p50_kwh, 3),
        "rss_uncertainty_total_percent": round(sigma_total_percent, 2),
        "rss_sigma_breakdown_percent": {
            "interannual": inputs.sigma_interannual_percent,
            "transposition_model": inputs.sigma_model_percent,
            "soiling": inputs.sigma_soiling_percent,
            "mismatch": inputs.sigma_mismatch_percent,
            "wiring": inputs.sigma_wiring_percent,
            "degradation": inputs.sigma_degradation_percent,
            "availability": inputs.sigma_availability_percent
        },
        "lcoe_usd_kwh": round(lcoe_usd_kwh, 4),
        "simple_payback_years": round(simple_payback_years, 1),
        "npv_usd": round(npv, 2),
        "irr_percent": round(irr_percent, 1),
        "gross_savings_year_1_usd": round(gross_savings_year_1, 2),
        "net_savings_year_1_usd": round(net_savings_year_1, 2),
        "annual_savings_year_25_usd": round(cashflows[-1], 2),
        "twenty_five_year_cashflows_usd": cashflows
    }

    return CalculationResult(
        provenance=provenance,
        inputs=inputs_dict,
        outputs=outputs
    )
