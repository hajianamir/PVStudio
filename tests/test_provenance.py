"""
Automated CI Test: Provenance Envelope Enforcement & Rejection Path Test
Per Technical Specification §1.4 & Gate Criterion G3
Asserts:
  1. Rejection path on un-enveloped or malformed calculation outputs.
  2. Input hash determinism across float rounding, None values, empty structures, and multi-depth nested dictionary key sorting.
"""

import pytest
from calc.provenance import CalculationResult, ProvenanceEnvelope, compute_input_hash
from app.repository.calc import CalculationRepository


def test_input_hash_determinism_floats_and_sorting():
    dict1 = {"b": 2.00001, "a": {"z": 1.123456, "y": None}}
    dict2 = {"a": {"y": None, "z": 1.1235}, "b": 2.0}

    # Should compute identical hash due to canonical float rounding and key sorting
    hash1 = compute_input_hash(dict1)
    hash2 = compute_input_hash(dict2)
    assert hash1 == hash2


def test_input_hash_distinguishes_none_empty_list_empty_dict():
    hash_none = compute_input_hash({"val": None})
    hash_empty_list = compute_input_hash({"val": []})
    hash_empty_dict = compute_input_hash({"val": {}})

    assert hash_none != hash_empty_list
    assert hash_none != hash_empty_dict
    assert hash_empty_list != hash_empty_dict


def test_provenance_envelope_success():
    repo = CalculationRepository()
    result = CalculationResult(
        provenance=ProvenanceEnvelope(
            calc_module="calc_sizing_dc",
            calc_version="1.0.0",
            input_hash="hash_test_12345",
            profile_id="US-NEC-2020-v1",
            project_id="draft",
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
        calc_module="",
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
        calc_version="",
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
        calc_version="99.9.9",
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
        input_hash="",
        profile_id="US-NEC-2020-v1"
    )
    result = CalculationResult(provenance=envelope, inputs={}, outputs={})
    with pytest.raises(ValueError, match="Missing required envelope field 'input_hash'"):
        repo.save(result, "rec_005")
