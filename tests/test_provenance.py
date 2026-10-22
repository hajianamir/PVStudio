"""
Automated CI Test: Provenance Envelope Enforcement & Persistence Test
Asserts that repository layer strictly rejects calculations missing provenance metadata.
"""

import pytest
from calc.provenance import CalculationResult, ProvenanceEnvelope
from app.repository.calc import CalculationRepository


def test_provenance_envelope_success():
    repo = CalculationRepository()
    result = CalculationResult(
        provenance=ProvenanceEnvelope(
            calc_module="calc_sizing_dc",
            calc_version="1.0.0",
            input_hash="hash_test_12345",
            profile_id="US-NEC-2020-v1",
            standards_referenced=["NEC 2020 Article 690.7"]
        ),
        inputs={"v_oc_stc": 49.5},
        outputs={"max_modules_per_string": 18}
    )
    saved = repo.save(result, "rec_001")
    assert saved["provenance"]["input_hash"] == "hash_test_12345"
    assert saved["provenance"]["calc_module"] == "calc_sizing_dc"


def test_provenance_envelope_rejection_missing_fields():
    repo = CalculationRepository()
    incomplete_envelope = ProvenanceEnvelope(
        calc_module="",  # Invalid
        calc_version="1.0.0",
        input_hash="hash_123",
        profile_id="US-NEC-2020-v1"
    )
    result = CalculationResult(
        provenance=incomplete_envelope,
        inputs={},
        outputs={}
    )
    with pytest.raises(ValueError, match="Missing required envelope field 'calc_module'"):
        repo.save(result, "rec_002")
