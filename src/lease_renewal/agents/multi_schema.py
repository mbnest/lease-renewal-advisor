"""JSON shapes for the specialists and the supervisor. Spike only, binds nothing."""

from typing import Literal

from pydantic import BaseModel, Field

from lease_renewal.agents.schema import FlagClaim


def _strict(model: type[BaseModel]) -> dict:
    schema = model.model_json_schema()
    schema["additionalProperties"] = False
    for definition in schema.get("$defs", {}).values():
        definition["additionalProperties"] = False
    return schema


class SpecialistOutput(BaseModel):
    """One specialist's read of its own data domain."""

    flags: list[FlagClaim]
    signal: Literal["ESCALATE", "RAISE", "HOLD", "NONE"] = Field(
        description="One directional signal. ESCALATE is valid for condition only."
    )
    finding: str = Field(description="What the domain data shows, in one or two sentences")


class SupervisorOutput(BaseModel):
    """The supervisor's combined recommendation. Code enforces clamp, band, and action."""

    proposed_rent_change_pct: float
    arbitration_note: str = Field(
        description="Explain the arbitration outcome you were given. You cannot change it."
    )
    reasoning: str
    draft_message: str


def specialist_schema() -> dict:
    return _strict(SpecialistOutput)


def supervisor_schema() -> dict:
    return _strict(SupervisorOutput)
