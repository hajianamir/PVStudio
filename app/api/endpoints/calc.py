"""
Calculation Endpoints with Mandatory Repository Persistence & Provenance Envelope
"""

import uuid
from fastapi import APIRouter, HTTPException, status
from calc.provenance import CalculationResult, ProvenanceEnvelope
from calc.calc_sizing_dc.service import calculate_dc_sizing, DCSizingInput
from app.repository.calc import calc_repository

router = APIRouter()


@router.post("/dc-sizing", response_model=CalculationResult)
def run_dc_sizing(inputs: DCSizingInput) -> CalculationResult:
    """
    Executes DC string sizing calculation, persists result with provenance envelope,
    and returns CalculationResult.
    """
    result = calculate_dc_sizing(inputs)

    # Hello calculation persistence demo
    record_id = f"calc_rec_{uuid.uuid4().hex[:12]}"
    try:
        calc_repository.save(result, record_id)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )

    return result
