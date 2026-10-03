"""Recompute flags from a home's data using the policy thresholds.

Answer keys are derived by this code, never hand-written, so a key error cannot
be mistaken for a model error. Flag definitions: docs/scenarios.md.
"""

from collections import Counter
from datetime import date

from lease_renewal.decision.policy import Policy

FLAGS = (
    "chronic_maintenance",
    "open_complaint",
    "late_payment_pattern",
    "below_market",
    "soft_demand",
)


def _within(day: str, as_of: date, months: int) -> bool:
    """True when an ISO date falls inside the window ending at as_of."""
    return (as_of - date.fromisoformat(day)).days <= months * 30.5


def chronic_maintenance(home: dict, policy: Policy, as_of: date) -> bool:
    """Repeat work orders on one system, or maintenance cost above a rent share."""
    t = policy.thresholds
    recent = [
        wo for wo in home["work_orders"] if _within(wo["date"], as_of, t["chronic_window_months"])
    ]
    by_system = Counter(wo["system"] for wo in recent)
    if by_system and max(by_system.values()) >= t["chronic_wo_same_system_count"]:
        return True
    annual_rent = home["current_rent"] * 12
    cost_share = 100 * sum(wo["cost"] for wo in recent) / annual_rent
    return cost_share > t["chronic_cost_pct_of_annual_rent"]


def open_complaint(home: dict, policy: Policy, as_of: date) -> bool:
    """A complaint still unresolved past the policy age."""
    limit = policy.thresholds["open_complaint_days"]
    return any(
        c["resolved"] is None and (as_of - date.fromisoformat(c["opened"])).days >= limit
        for c in home["complaints"]
    )


def late_payment_pattern(home: dict, policy: Policy, as_of: date) -> bool:
    """Enough late payments inside the window to count as a pattern."""
    t = policy.thresholds
    late = [
        p
        for p in home["payments"]
        if p["days_late"] > 0 and _within(p["due"], as_of, t["late_payment_window_months"])
    ]
    return len(late) >= t["late_payment_count"]


def below_market(home: dict, policy: Policy, as_of: date) -> bool:
    """Rent sitting at least the policy margin under the comp median."""
    margin = policy.thresholds["below_market_pct"]
    gap = 100 * (home["comps"]["median_rent"] - home["current_rent"]) / home["comps"]["median_rent"]
    return gap >= margin


def soft_demand(home: dict, policy: Policy, as_of: date) -> bool:
    """Soft city demand together with a flat or falling comp trend."""
    t = policy.thresholds
    return (
        home["demand"] in t["soft_demand_city_values"]
        and home["comps"]["trend"] in t["soft_demand_trend_values"]
    )


_CHECKS = {
    "chronic_maintenance": chronic_maintenance,
    "open_complaint": open_complaint,
    "late_payment_pattern": late_payment_pattern,
    "below_market": below_market,
    "soft_demand": soft_demand,
}


def flags_for(home: dict, policy: Policy, as_of: date) -> list[str]:
    """Every flag the home's data earns, in the fixed flag order."""
    return [name for name in FLAGS if _CHECKS[name](home, policy, as_of)]
