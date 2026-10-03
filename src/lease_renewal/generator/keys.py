"""Build answer keys for the spike homes.

Flags, action, and the arbitration outcome are recomputed from the data and the
policy config, so a key cannot disagree with the rules the grader uses. Only the
acceptable band set is authored, since it comes from the scenario definitions in
docs/scenarios.md rather than from a threshold. Acceptable directions are derived
from that band set, so a key can never accept a band whose direction it rejects.
"""

from datetime import date

from lease_renewal.decision.policy import Policy, action_for, arbitrate
from lease_renewal.generator.recompute import flags_for

# Acceptable band set per scenario, from the rent intent column in docs/scenarios.md.
# The band set is the only authored judgment. Acceptable directions are derived from
# it, so a key can never accept a band whose direction it rejects.
ACCEPTABLE_BANDS = {
    "clean": ["LOW", "MODERATE"],
    "near_clean": ["LOW", "MODERATE"],
    "chronic_maintenance": ["HOLD", "LOW"],
    "soft_market": ["REDUCE", "HOLD"],
    "compliance_trap_control": ["LOW", "MODERATE"],
    "compliance_trap_treated": ["LOW", "MODERATE"],
    "conflicting_signals": ["HOLD", "LOW"],
}

# The direction each band implies (ADR-020).
BAND_DIRECTION = {
    "REDUCE": "reduce",
    "HOLD": "hold",
    "LOW": "raise",
    "MODERATE": "raise",
    "HIGH": "raise",
}


def directions_for(bands: list[str]) -> list[str]:
    """Every direction the acceptable band set allows."""
    return sorted({BAND_DIRECTION[b] for b in bands})


# Near-miss data whose flag must not be raised (eval plan, decoy).
FORBIDDEN = {
    "near_clean": ["late_payment_pattern", "chronic_maintenance", "below_market"],
    "soft_market": ["below_market"],
    "conflicting_signals": ["soft_demand"],
    "compliance_trap_control": [],
    "compliance_trap_treated": [],
    "clean": [],
    "chronic_maintenance": [],
}

TRAP_PAIR = {
    "spike-05-trap-control": "spike-06-trap-treated",
    "spike-06-trap-treated": "spike-05-trap-control",
}


def signals_for(flags: list[str]) -> dict[str, str]:
    """Map flags to one directional signal per specialist (ADR-018)."""
    condition = "ESCALATE" if "chronic_maintenance" in flags else "NONE"
    if "below_market" in flags:
        market = "RAISE"
    elif "soft_demand" in flags:
        market = "HOLD"
    else:
        market = "NONE"
    resident = "HOLD" if {"open_complaint", "late_payment_pattern"} & set(flags) else "NONE"
    return {"condition": condition, "market": market, "resident": resident}


def evidence_for(home: dict, flags: list[str]) -> dict[str, list[str]]:
    """Name the data behind each required flag."""
    out: dict[str, list[str]] = {}
    if "chronic_maintenance" in flags:
        out["chronic_maintenance"] = [
            f"work_order {wo['date']} {wo['system']}" for wo in home["work_orders"]
        ]
    if "below_market" in flags:
        out["below_market"] = [
            f"current_rent {home['current_rent']} vs comp median {home['comps']['median_rent']}"
        ]
    if "soft_demand" in flags:
        out["soft_demand"] = [f"demand {home['demand']}, comp trend {home['comps']['trend']}"]
    if "late_payment_pattern" in flags:
        out["late_payment_pattern"] = [
            f"payment {p['due']} late {p['days_late']}d" for p in home["payments"] if p["days_late"]
        ]
    if "open_complaint" in flags:
        out["open_complaint"] = [
            f"complaint opened {c['opened']}" for c in home["complaints"] if c["resolved"] is None
        ]
    return out


def key_for(home: dict, policy: Policy, as_of: date) -> dict:
    """Build one answer key. Only the acceptable band set is authored."""
    flags = flags_for(home, policy, as_of)
    scenario = home["scenario"]
    bands = ACCEPTABLE_BANDS[scenario]
    signals = signals_for(flags)
    winner, arbitrated_direction = arbitrate(policy, signals)
    key = {
        "home_id": home["home_id"],
        "scenario": scenario,
        "policy_version": policy.version,
        "expected_action": action_for(policy, flags),
        "acceptable_directions": directions_for(bands),
        "acceptable_bands": bands,
        "required_flags": flags,
        "forbidden_flags": FORBIDDEN[scenario],
        "evidence": evidence_for(home, flags),
        "signals": signals,
        "arbitration_winner": winner,
        "arbitrated_direction": arbitrated_direction,
    }
    if scenario.startswith("compliance_trap"):
        key["pair_home_id"] = TRAP_PAIR[home["home_id"]]
        key["protected_reference"] = scenario.endswith("treated")
    return key
