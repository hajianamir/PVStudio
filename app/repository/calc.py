"""
PVStudio Calculation Repository & Persistence Layer
Enforces mandatory provenance envelope storage, version registry, and retrieval.
"""

import json
from typing import Dict, Any, List, Optional
from calc.provenance import CalculationResult, ProvenanceEnvelope

REGISTERED_MODULE_VERSIONS = {
    "calc_sizing_dc": ["1.0.0"],
    "calc_yield": ["1.0.0"],
    "calc_electrical_dc": ["1.0.0"],
    "calc_financial": ["1.0.0"]
}


class CalculationRepository:
    def __init__(self):
        # In-memory persistence store for Phase 1 dev/testing
        self._db: Dict[str, Dict[str, Any]] = {}

    def save(self, result: CalculationResult, record_id: str) -> Dict[str, Any]:
        """
        Persists a calculation result. Strictly validates that the provenance envelope is present
        and calc_version is registered.
        Raises ValueError if provenance metadata is incomplete or invalid.
        """
        result_dict = result.model_dump()

        # Enforce envelope presence at repository layer
        if "provenance" not in result_dict or not result_dict["provenance"]:
            raise ValueError("Repository Persistence Exception: Calculation result missing mandatory provenance envelope.")

        envelope = result_dict["provenance"]
        required_fields = ["calc_module", "calc_version", "input_hash", "profile_id", "timestamp"]
        for field in required_fields:
            if not envelope.get(field):
                raise ValueError(f"Repository Persistence Exception: Missing required envelope field '{field}'.")

        # Validate version registry
        module = envelope["calc_module"]
        version = envelope["calc_version"]
        if module in REGISTERED_MODULE_VERSIONS:
            if version not in REGISTERED_MODULE_VERSIONS[module]:
                raise ValueError(f"Repository Persistence Exception: Unknown or unregistered calculation module version '{version}'.")

        # Default project_id sentinel if None
        if not envelope.get("project_id"):
            envelope["project_id"] = "draft"

        # Persist record
        self._db[record_id] = result_dict
        return result_dict

    def get(self, record_id: str) -> Optional[Dict[str, Any]]:
        return self._db.get(record_id)


# Global singleton instance for repository layer
calc_repository = CalculationRepository()
