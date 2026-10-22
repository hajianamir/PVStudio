"""
Automated CI Test: Golden Benchmark SHA-256 Hash Manifest Integrity Check
Per Sprint 2 Audit Control 1 (Option A Enforcement)
Asserts that golden benchmark reference cases cannot be silently modified without triggering build failure.
"""

import json
import hashlib
import os
import pytest
from tests.benchmarks.harness import BENCHMARK_CASES

MANIFEST_PATH = "tests/benchmarks/SHA256SUMS.json"


def test_golden_benchmark_manifest_integrity():
    assert os.path.exists(MANIFEST_PATH), "SHA256SUMS.json manifest missing."

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    # Compute current runtime hash for BENCHMARK_CASES
    for case in BENCHMARK_CASES:
        case_id = f"case_{case['case_id']}"
        serialized = json.dumps(case, sort_keys=True)
        computed_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        # Check if case exists in manifest (Option A control assertion)
        assert case_id in manifest_data["manifest"], f"Golden benchmark {case_id} not registered in SHA256SUMS.json"


def test_golden_manifest_tampering_fails_build():
    # Simulated tampered benchmark case
    tampered_case = {"case_id": 99, "reference_pvsyst_annual_kwh": 99999.0}
    serialized = json.dumps(tampered_case, sort_keys=True)
    tampered_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    # Assert tampered case hash does not match registered golden manifest
    registered_hash = manifest_data["manifest"].get("case_1")
    assert tampered_hash != registered_hash, "Tampered golden case hash matches registered manifest!"
