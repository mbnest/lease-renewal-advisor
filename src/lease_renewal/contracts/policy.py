"""Policy config contract.

Thresholds, severity tags, arbitration precedence, bands, and the clamp live in a
versioned config file, not in code (ADR-014). Agents see it and the
generation-time validator reads it. Nothing recomputes it at runtime.

Values are not part of the contract. The shipped values and their calibration are
in `config/`, and tuning them is deferred (DD-01).
"""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

FlagType = Literal[
    "chronic_maintenance",
    "open_complaint",
    "late_payment_pattern",
    "below_market",
    "soft_demand",
]

Severity = Literal["escalate", "note"]

Action = Literal["renew", "renew_with_note", "escalate"]

BandName = Literal["REDUCE", "HOLD", "LOW", "MODERATE", "HIGH"]

Direction = Literal["reduce", "hold", "raise"]

Specialist = Literal["condition", "market", "resident"]

Percent = Annotated[float, Field(ge=-100.0, le=100.0)]


class Strict(BaseModel):
    """Reject unknown fields, so a renamed contract field fails loudly."""

    model_config = ConfigDict(extra="forbid")


class Thresholds(Strict):
    """The only values the generation-time validator evaluates (ADR-014)."""

    chronic_wo_same_system_count: int = Field(ge=1)
    chronic_window_months: int = Field(ge=1)
    chronic_cost_pct_of_annual_rent: float = Field(gt=0)
    late_payment_count: int = Field(ge=1)
    late_payment_window_months: int = Field(ge=1)
    below_market_pct: float = Field(gt=0)
    soft_demand_city_values: list[str] = Field(min_length=1)
    soft_demand_trend_values: list[str] = Field(min_length=1)
    open_complaint_days: int = Field(ge=1)


class Band(Strict):
    """One named percent range. Edges live here and nowhere else (ADR-020)."""

    lower: Percent
    upper: Percent
    lower_inclusive: bool
    upper_inclusive: bool

    @model_validator(mode="after")
    def _ordered(self) -> "Band":
        if self.lower > self.upper:
            raise ValueError(f"band lower {self.lower} above upper {self.upper}")
        return self


class Clamp(Strict):
    """The outer guardrail code applies to every rent proposal (ADR-003, ADR-020)."""

    floor_pct: Percent
    cap_pct: Percent

    @model_validator(mode="after")
    def _ordered(self) -> "Clamp":
        if self.floor_pct > self.cap_pct:
            raise ValueError(f"clamp floor {self.floor_pct} above cap {self.cap_pct}")
        return self


class PolicyConfig(Strict):
    """A versioned policy config. The version is named in every answer key header."""

    version: str = Field(min_length=1)
    thresholds: Thresholds
    severity_tags: dict[FlagType, Severity]
    combining_rule: Literal["highest_severity_wins"]
    arbitration_precedence: list[Specialist] = Field(min_length=1)
    bands: dict[BandName, Band]
    clamp: Clamp

    @model_validator(mode="after")
    def _every_flag_type_is_tagged(self) -> "PolicyConfig":
        missing = set(FlagType.__args__) - set(self.severity_tags)
        if missing:
            raise ValueError(f"flag types without a severity tag: {sorted(missing)}")
        return self

    @model_validator(mode="after")
    def _every_band_is_defined(self) -> "PolicyConfig":
        missing = set(BandName.__args__) - set(self.bands)
        if missing:
            raise ValueError(f"bands not defined: {sorted(missing)}")
        return self

    @model_validator(mode="after")
    def _precedence_lists_each_specialist_once(self) -> "PolicyConfig":
        if sorted(self.arbitration_precedence) != sorted(Specialist.__args__):
            raise ValueError(
                f"arbitration precedence must list each specialist once, got "
                f"{self.arbitration_precedence}"
            )
        return self

    @model_validator(mode="after")
    def _clamp_lies_inside_the_bands(self) -> "PolicyConfig":
        """Every clamped value must fall in some band, or grading has nowhere to put it."""
        lowest = min(b.lower for b in self.bands.values())
        highest = max(b.upper for b in self.bands.values())
        if self.clamp.floor_pct < lowest or self.clamp.cap_pct > highest:
            raise ValueError(
                f"clamp [{self.clamp.floor_pct}, {self.clamp.cap_pct}] reaches outside "
                f"the bands [{lowest}, {highest}]"
            )
        return self
