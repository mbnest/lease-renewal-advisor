"""Policy config loading and the rules code enforces: bands, clamp, action, arbitration.

Values live in the config, never in this module (ADR-014). The model proposes a
rent change; this code decides the band, the clamped value, and the action (ADR-003).
"""

from dataclasses import dataclass
from pathlib import Path

import yaml

ESCALATE = "escalate"
RENEW_WITH_NOTE = "renew_with_note"
RENEW = "renew"


@dataclass(frozen=True)
class Policy:
    """A loaded policy config."""

    version: str
    thresholds: dict
    severity_tags: dict
    arbitration_precedence: list[str]
    bands: dict
    floor_pct: float
    cap_pct: float


def load_policy(path: Path) -> Policy:
    """Read a policy config YAML file."""
    raw = yaml.safe_load(path.read_text())
    return Policy(
        version=raw["version"],
        thresholds=raw["thresholds"],
        severity_tags=raw["severity_tags"],
        arbitration_precedence=raw["arbitration_precedence"],
        bands=raw["bands"],
        floor_pct=raw["clamp"]["floor_pct"],
        cap_pct=raw["clamp"]["cap_pct"],
    )


def clamp(policy: Policy, pct: float) -> float:
    """Hold a proposed percent change inside the policy floor and cap."""
    return max(policy.floor_pct, min(policy.cap_pct, pct))


def band_of(policy: Policy, pct: float) -> str | None:
    """Name the band a percent change falls in, or None when it falls outside every band."""
    for name, edges in policy.bands.items():
        above_lower = pct >= edges["lower"] if edges["lower_inclusive"] else pct > edges["lower"]
        below_upper = pct <= edges["upper"] if edges["upper_inclusive"] else pct < edges["upper"]
        if above_lower and below_upper:
            return name
    return None


def direction_of(pct: float) -> str:
    """Reduce, hold, or raise."""
    if pct < 0:
        return "reduce"
    if pct > 0:
        return "raise"
    return "hold"


def action_for(policy: Policy, flags: list[str]) -> str:
    """Resolve the action from flag severity tags. Highest severity wins (ADR-015)."""
    tags = {policy.severity_tags[f] for f in flags}
    if ESCALATE in tags:
        return ESCALATE
    if "note" in tags:
        return RENEW_WITH_NOTE
    return RENEW


def arbitrate(policy: Policy, signals: dict[str, str]) -> tuple[str, str]:
    """Pick the winning specialist and its direction by fixed precedence (ADR-018).

    Signals map a specialist name to its directional signal. Only ESCALATE matches
    for condition. Returns the winner and the rent direction it implies.
    """
    for specialist in policy.arbitration_precedence:
        signal = signals.get(specialist, "NONE")
        if specialist == "condition" and signal == "ESCALATE":
            return specialist, "hold"
        if specialist != "condition" and signal in ("RAISE", "HOLD"):
            return specialist, "raise" if signal == "RAISE" else "hold"
    return "none", "hold"


SIGNAL_DIRECTION = {
    ("condition", "ESCALATE"): "hold",
    ("market", "RAISE"): "raise",
    ("market", "HOLD"): "hold",
    ("resident", "RAISE"): "raise",
    ("resident", "HOLD"): "hold",
}


def implied_directions(signals: dict[str, str]) -> set[str]:
    """The directions the active specialist signals point to."""
    return {
        SIGNAL_DIRECTION[(name, signal)]
        for name, signal in signals.items()
        if (name, signal) in SIGNAL_DIRECTION
    }


def has_conflict(signals: dict[str, str]) -> bool:
    """True when active signals point different ways, which is when arbitration binds.

    Arbitration decides rent direction only, and only on a conflict (ADR-018).
    With one signal or none, the direction is left to the agents.
    """
    return len(implied_directions(signals)) > 1
