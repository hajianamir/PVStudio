"""
PVStudio Provenance Envelope Specification & Base Calculation Models
Enforces strict calculation audit metadata per Technical Specification §1.4
"""

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProvenanceEnvelope(BaseModel):
    calc_module: str = Field(..., description="Calculation package name (e.g. calc_sizing_dc)")
    calc_version: str = Field(..., description="Semantic version of calculation module")
    input_hash: str = Field(..., description="SHA-256 hash of calculation inputs")
    profile_id: str = Field(..., description="Active rules-as-data compliance profile ID")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp of calculation execution"
    )
    user_id: Optional[str] = Field(default=None, description="Requesting user ID")
    project_id: Optional[str] = Field(default=None, description="Target project UUID")
    standards_referenced: List[str] = Field(default_factory=list, description="Citations of standards enforced")


class CalculationResult(BaseModel):
    provenance: ProvenanceEnvelope
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]


def compute_input_hash(inputs_dict: Dict[str, Any]) -> str:
    """Calculates deterministic SHA-256 hash of calculation inputs."""
    serialized = json.dumps(inputs_dict, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
