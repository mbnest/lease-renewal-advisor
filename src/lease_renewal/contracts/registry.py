"""The committed contracts and their JSON Schema rendering.

The Pydantic models are the source of truth. `schemas/` holds generated files so
other tools can read the contracts without importing Python, and a test asserts
the two cannot drift.
"""

import json

from pydantic import BaseModel

from lease_renewal.contracts.policy import PolicyConfig

CONTRACTS: dict[str, type[BaseModel]] = {
    "policy": PolicyConfig,
}


def schema_for(model: type[BaseModel]) -> str:
    """Deterministic JSON Schema text for one contract."""
    return json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n"
