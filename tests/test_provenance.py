"""
Automated CI Test: Provenance Envelope Enforcement & Rejection Path Test
Per Technical Specification §1.4 & Gate Criterion G3
Asserts that repository persistence layer strictly rejects un-enveloped or malformed calculation outputs.
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
            project_id="draft",  # Explicit draft sentinel
            standards_referenced=["NEC 2020 Article 690.7"]
        ),
        inputs={"v_oc_stc": 49.5},
        outputs={"max_modules_per_string": 18}
    )
    saved = repo.save(result, "rec_001")
    assert saved["provenance"]["input_hash"] == "hash_test_12345"
    assert saved["provenance"]["calc_module"] == "calc_sizing_dc"
    assert saved["provenance"]["project_id"] == "draft"


def test_provenance_rejection_missing_module():
    repo = CalculationRepository()
    envelope = ProvenanceEnvelope(
        calc_module="",  # Invalid empty
        calc_version="1.0.0",
        input_hash="hash_123",
        profile_id="US-NEC-2020-v1"
    )
    result = CalculationResult(provenance=envelope, inputs={}, outputs={})
    with pytest.raises(ValueError, match="Missing required envelope field 'calc_module'"):
        repo.save(result, "rec_002")


def test_provenance_rejection_missing_version():
    repo = CalculationRepository()
    envelope = ProvenanceEnvelope(
        calc_module="calc_sizing_dc",
        calc_version="",  # Missing version
        input_hash="hash_123",
        profile_id="US-NEC-2020-v1"
    )
    result = CalculationResult(provenance=envelope, inputs={}, outputs={})
    with pytest.raises(ValueError, match="Missing required envelope field 'calc_version'"):
        repo.save(result, "rec_003")


def test_provenance_rejection_unknown_version():
    repo = CalculationRepository()
    envelope = ProvenanceEnvelope(
        calc_module="calc_sizing_dc",
        calc_version="99.9.9",  # Unknown version drift
        input_hash="hash_123",
        profile_id="US-NEC-2020-v1"
    )
    result = CalculationResult(provenance=envelope, inputs={}, outputs={})
    with pytest.raises(ValueError, match="Unknown or unregistered calculation module version '99.9.9'"):
        repo.save(result, "rec_004")


def test_provenance_rejection_missing_input_hash():
    repo = CalculationRepository()
    envelope = ProvenanceEnvelope(
        calc_module="calc_sizing_dc",
        calc_version="1.0.0",
        input_hash="",  # Missing hash
        profile_id="US-NEC-2020-v1"
    )
    result = CalculationResult(provenance=envelope, inputs={}, outputs={})
    with pytest.raises(ValueError, match="Missing required envelope field 'input_hash'"):
        repo.save(result, "rec_005")
