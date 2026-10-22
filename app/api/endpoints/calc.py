"""
Calculation Endpoints with Mandatory Provenance Envelope Enforcement
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash
from calc.calc_sizing_dc.service import calculate_dc_sizing, DCSizingInput

router = APIRouter()


@router.post("/dc-sizing", response_model=CalculationResult)
def run_dc_sizing(inputs: DCSizingInput) -> CalculationResult:
    """
    Executes DC string sizing calculation and returns result wrapped in mandatory Provenance Envelope.
    """
    return calculate_dc_sizing(inputs)
