"""
Compliance Layer & Refusal-to-Guess Safeguard Checker
Per Technical Specification §6.4 & Phase 1 Gate Criterion G4
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ComplianceProfile(BaseModel):
    profile_id: str
    jurisdiction: str
    max_voltage_v: Optional[int] = None
    rapid_shutdown_required: Optional[bool] = None
    busbar_120_percent_rule: Optional[bool] = None


class ComplianceCheckResult(BaseModel):
    is_approved: bool
    status_code: str
    warning_message: Optional[str] = None
    required_engineer_signoff: bool = False


def evaluate_design_compliance(profile: ComplianceProfile) -> ComplianceCheckResult:
    """
    Evaluates design against compliance profile.
    Refuses auto-approval if any required profile parameter is None/missing.
    """
    profile_dict = profile.model_dump()
    required_rules = ["max_voltage_v", "rapid_shutdown_required", "busbar_120_percent_rule"]

    for rule in required_rules:
        if profile_dict.get(rule) is None:
            return ComplianceCheckResult(
                is_approved=False,
                status_code="REFUSAL_INCOMPLETE_PROFILE",
                warning_message=f"CRITICAL: Refusal-to-Guess safeguard triggered. Required parameter '{rule}' missing in profile '{profile.profile_id}'.",
                required_engineer_signoff=True
            )

    return ComplianceCheckResult(
        is_approved=True,
        status_code="APPROVED",
        warning_message=None,
        required_engineer_signoff=False
    )
