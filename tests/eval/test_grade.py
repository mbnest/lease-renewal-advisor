"""Grading arithmetic, checked on fabricated runs before any model call is paid for."""

import pytest

from lease_renewal.eval.grade import band_distance, cost_usd, grade_case, summarise


def run(**over) -> dict:
    base = {
        "home_id": "h1",
        "proposed_action": "escalate",
        "enforced_action": "escalate",
        "proposed_rent_change_pct": 1.0,
        "clamped_rent_change_pct": 1.0,
        "pre_clamp_band": "LOW",
        "band": "LOW",
        "direction": "raise",
        "flags": ["chronic_maintenance"],
        "prompt_tokens": 1000,
        "completion_tokens": 500,
    }
    base.update(over)
    return base


def key(**over) -> dict:
    base = {
        "scenario": "chronic_maintenance",
        "expected_action": "escalate",
        "expected_direction": "raise",
        "acceptable_bands": ["HOLD", "LOW"],
        "required_flags": ["chronic_maintenance"],
        "forbidden_flags": [],
    }
    base.update(over)
    return base


@pytest.mark.unit
@pytest.mark.parametrize(
    ("band", "acceptable", "expected"),
    [
        ("LOW", ["HOLD", "LOW"], 0),
        ("MODERATE", ["HOLD", "LOW"], 1),
        ("HIGH", ["HOLD", "LOW"], 2),
        ("REDUCE", ["LOW"], 2),
        (None, ["LOW"], None),
    ],
)
def test_band_distance(band, acceptable, expected):
    assert band_distance(band, acceptable) == expected


@pytest.mark.unit
def test_cost_uses_the_pinned_model_rates():
    """1M prompt tokens at $0.05 and 1M completion at $0.40."""
    assert cost_usd(1_000_000, 0) == pytest.approx(0.05)
    assert cost_usd(0, 1_000_000) == pytest.approx(0.40)


@pytest.mark.harness
def test_a_fully_correct_case_passes_every_check():
    g = grade_case(run(), key())
    assert g["action_pass"] and g["direction_pass"] and g["band_exact"]
    assert g["flags_missed"] == [] and g["flag_recall"] == 1.0
    assert not g["severe_miss"]


@pytest.mark.harness
def test_missed_escalate_flag_is_a_severe_miss():
    g = grade_case(run(flags=[], enforced_action="renew"), key())
    assert g["flags_missed"] == ["chronic_maintenance"]
    assert g["flag_recall"] == 0.0
    assert g["severe_miss"]


@pytest.mark.harness
def test_forbidden_flag_is_counted_separately_from_extra():
    g = grade_case(
        run(flags=["chronic_maintenance", "below_market"]),
        key(forbidden_flags=["below_market"]),
    )
    assert g["flags_forbidden_raised"] == ["below_market"]
    assert g["flags_extra"] == []


@pytest.mark.harness
def test_clamp_rescue_is_visible():
    """A proposal outside every band that the clamp pulls back into one."""
    g = grade_case(run(proposed_rent_change_pct=14.0, pre_clamp_band=None, band="HIGH"), key())
    assert g["pre_clamp_outside"] and g["clamp_rescued"]


@pytest.mark.harness
def test_clean_home_recall_is_none_not_zero():
    """A home with no required flags must not drag the recall average down."""
    g = grade_case(
        run(flags=[], enforced_action="renew"), key(expected_action="renew", required_flags=[])
    )
    assert g["flag_recall"] is None


@pytest.mark.harness
def test_summary_counts_named_failure_modes():
    graded = [
        grade_case(run(), key()),
        grade_case(run(flags=[], enforced_action="renew"), key()),
    ]
    s = summarise(graded)
    assert s["homes"] == 2
    assert s["action_pass"] == 1
    assert s["severe_misses"] == 1
    assert s["homes_with_missed_flags"] == 1
    assert s["mean_flag_recall"] == pytest.approx(0.5)
