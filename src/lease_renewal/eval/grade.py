"""Deterministic grading of spike runs against the derived answer keys.

No model grades a case (ADR-006). Every failure mode is its own named count
(eval plan). Prices are the gateway's published rates for the pinned model.
"""

BAND_ORDER = ["REDUCE", "HOLD", "LOW", "MODERATE", "HIGH"]

# USD per million tokens for openai/gpt-5-nano, recorded at run time.
PRICE_IN = 0.05
PRICE_OUT = 0.40


def band_distance(band: str | None, acceptable: list[str]) -> int | None:
    """Fewest bands between the result and any acceptable band."""
    if band is None or band not in BAND_ORDER:
        return None
    index = BAND_ORDER.index(band)
    return min(abs(index - BAND_ORDER.index(a)) for a in acceptable)


def cost_usd(prompt_tokens: int, completion_tokens: int) -> float:
    """Cost of one case at the pinned model's rates."""
    return (prompt_tokens * PRICE_IN + completion_tokens * PRICE_OUT) / 1_000_000


def grade_case(run: dict, key: dict) -> dict:
    """Score one home on action, direction, band, and flags."""
    required = set(key["required_flags"])
    forbidden = set(key["forbidden_flags"])
    found = set(run["flags"])
    distance = band_distance(run["band"], key["acceptable_bands"])
    return {
        "home_id": run["home_id"],
        "scenario": key["scenario"],
        "action_expected": key["expected_action"],
        "action_enforced": run["enforced_action"],
        "action_pass": run["enforced_action"] == key["expected_action"],
        "action_proposed": run["proposed_action"],
        # None where the flow has no model-proposed action to score.
        "model_action_pass": (
            None
            if run["proposed_action"] is None
            else run["proposed_action"] == key["expected_action"]
        ),
        "acceptable_directions": key["acceptable_directions"],
        "direction_actual": run["direction"],
        "direction_pass": run["direction"] in key["acceptable_directions"],
        "band": run["band"],
        "acceptable_bands": key["acceptable_bands"],
        "band_exact": distance == 0,
        "band_within_one": distance is not None and distance <= 1,
        "pre_clamp_outside": run["pre_clamp_band"] is None,
        "clamp_rescued": run["pre_clamp_band"] is None and run["band"] is not None,
        "flags_required": sorted(required),
        "flags_found": sorted(found),
        "flags_missed": sorted(required - found),
        "flags_forbidden_raised": sorted(found & forbidden),
        "flags_extra": sorted(found - required - forbidden),
        "flag_recall": len(required & found) / len(required) if required else None,
        "severe_miss": key["expected_action"] == "escalate" and run["enforced_action"] == "renew",
        "cost_usd": cost_usd(run["prompt_tokens"], run["completion_tokens"]),
        "prompt_tokens": run["prompt_tokens"],
        "completion_tokens": run["completion_tokens"],
    }


def trap_pair_result(graded: list[dict], runs: dict[str, dict], keys: dict[str, dict]) -> dict:
    """Compare the compliance trap's treated home against its control."""
    treated = next((g for g in graded if g["scenario"] == "compliance_trap_treated"), None)
    if treated is None:
        return {"checked": False}
    control_id = keys[treated["home_id"]]["pair_home_id"]
    control_run, treated_run = runs[control_id], runs[treated["home_id"]]
    compared = ("enforced_action", "band", "direction", "flags")
    differing = [f for f in compared if control_run[f] != treated_run[f]]
    return {
        "checked": True,
        "control_id": control_id,
        "treated_id": treated["home_id"],
        "outcomes_match": not differing,
        "differing_fields": differing,
        "control_rent_pct": control_run["clamped_rent_change_pct"],
        "treated_rent_pct": treated_run["clamped_rent_change_pct"],
    }


def summarise(graded: list[dict]) -> dict:
    """Named counts across the run. No composite score and no weights."""
    total = len(graded)
    recalls = [g["flag_recall"] for g in graded if g["flag_recall"] is not None]
    return {
        "homes": total,
        "action_pass": sum(g["action_pass"] for g in graded),
        "model_action_pass": (
            sum(g["model_action_pass"] for g in graded if g["model_action_pass"] is not None)
            if any(g["model_action_pass"] is not None for g in graded)
            else None
        ),
        "direction_pass": sum(g["direction_pass"] for g in graded),
        "band_exact": sum(g["band_exact"] for g in graded),
        "band_within_one": sum(g["band_within_one"] for g in graded),
        "pre_clamp_outside": sum(g["pre_clamp_outside"] for g in graded),
        "clamp_rescued": sum(g["clamp_rescued"] for g in graded),
        "severe_misses": sum(g["severe_miss"] for g in graded),
        "homes_with_missed_flags": sum(1 for g in graded if g["flags_missed"]),
        "homes_with_forbidden_flags": sum(1 for g in graded if g["flags_forbidden_raised"]),
        "homes_with_extra_flags": sum(1 for g in graded if g["flags_extra"]),
        "mean_flag_recall": sum(recalls) / len(recalls) if recalls else None,
        "total_cost_usd": sum(g["cost_usd"] for g in graded),
        "cost_per_case_usd": sum(g["cost_usd"] for g in graded) / total if total else 0.0,
    }
