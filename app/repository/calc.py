"""
PVStudio Calculation Repository & Persistence Layer
Enforces mandatory provenance envelope storage and retrieval.
"""

import json
from typing import Dict, Any, List, Optional
from calc.provenance import CalculationResult, ProvenanceEnvelope


class CalculationRepository:
    def __init__(self):
        # In-memory persistence store for Phase 1 dev/testing (connects to Postgres in staging)
        self._db: Dict[str, Dict[str, Any]] = {}

    def save(self, result: CalculationResult, record_id: str) -> Dict[str, Any]:
        """
        Persists a calculation result. Strictly validates that the provenance envelope is present.
        Raises ValueError if provenance metadata is incomplete.
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

        # Persist record
        self._db[record_id] = result_dict
        return result_dict

    def get(self, record_id: str) -> Optional[Dict[str, Any]]:
        return self._db.get(record_id)


# Global singleton instance for repository layer
calc_repository = CalculationRepository()
