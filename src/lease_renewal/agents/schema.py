"""The JSON shape the baseline agent must return.

Informal and spike-only. The committed Recommendation contract is written in
task 1.2; this binds nothing.
"""

from typing import Literal

from pydantic import BaseModel, Field

FlagName = Literal[
    "chronic_maintenance",
    "open_complaint",
    "late_payment_pattern",
    "below_market",
    "soft_demand",
]


class FlagClaim(BaseModel):
    """A flag the model raises, with the data it says supports it."""

    flag: FlagName
    evidence: str = Field(description="The specific record or figure behind this flag")


class BaselineOutput(BaseModel):
    """One model proposal for one home. Code enforces the clamp, band, and action."""

    proposed_action: Literal["renew", "renew_with_note", "escalate"]
    proposed_rent_change_pct: float
    flags: list[FlagClaim]
    reasoning: str
    draft_message: str


def json_schema() -> dict:
    """A strict JSON schema for the gateway's structured output mode."""
    schema = BaselineOutput.model_json_schema()
    schema["additionalProperties"] = False
    for definition in schema.get("$defs", {}).values():
        definition["additionalProperties"] = False
    return schema
