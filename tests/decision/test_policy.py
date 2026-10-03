"""Policy resolution against the decided values in ADR-015, ADR-018, and ADR-020."""

from pathlib import Path

import pytest

from lease_renewal.decision.policy import (
    action_for,
    arbitrate,
    band_of,
    clamp,
    direction_of,
    load_policy,
)

CONFIG = Path("config/policy_spike.yaml")


@pytest.fixture(scope="module")
def policy():
    return load_policy(CONFIG)


@pytest.mark.unit
def test_loads_decided_clamp(policy):
    assert (policy.floor_pct, policy.cap_pct) == (-5.0, 6.0)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("pct", "expected"),
    [
        (-5.0, "REDUCE"),
        (-0.1, "REDUCE"),
        (0.0, "HOLD"),
        (0.1, "LOW"),
        (2.0, "LOW"),
        (2.1, "MODERATE"),
        (4.0, "MODERATE"),
        (4.1, "HIGH"),
        (6.0, "HIGH"),
        (-5.1, None),
        (6.1, None),
    ],
)
def test_band_edges(policy, pct, expected):
    assert band_of(policy, pct) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    ("pct", "expected"), [(-9.0, -5.0), (-5.0, -5.0), (3.0, 3.0), (6.0, 6.0), (9.0, 6.0)]
)
def test_clamp_holds_the_guardrail(policy, pct, expected):
    assert clamp(policy, pct) == expected


@pytest.mark.unit
def test_clamped_values_always_land_in_a_band(policy):
    for pct in (-20.0, -5.0, 0.0, 3.3, 20.0):
        assert band_of(policy, clamp(policy, pct)) is not None


@pytest.mark.unit
@pytest.mark.parametrize(("pct", "expected"), [(-1.0, "reduce"), (0.0, "hold"), (1.0, "raise")])
def test_direction(pct, expected):
    assert direction_of(pct) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    ("flags", "expected"),
    [
        ([], "renew"),
        (["below_market"], "renew_with_note"),
        (["soft_demand", "late_payment_pattern"], "renew_with_note"),
        (["chronic_maintenance"], "escalate"),
        (["below_market", "open_complaint"], "escalate"),
    ],
)
def test_highest_severity_wins(policy, flags, expected):
    assert action_for(policy, flags) == expected


@pytest.mark.unit
def test_condition_escalation_outranks_market(policy):
    signals = {"condition": "ESCALATE", "market": "RAISE", "resident": "RAISE"}
    assert arbitrate(policy, signals) == ("condition", "hold")


@pytest.mark.unit
def test_market_outranks_resident(policy):
    signals = {"condition": "NONE", "market": "HOLD", "resident": "RAISE"}
    assert arbitrate(policy, signals) == ("market", "hold")


@pytest.mark.unit
def test_condition_raise_does_not_win_arbitration(policy):
    """Only ESCALATE matches for condition (ADR-018)."""
    signals = {"condition": "RAISE", "market": "RAISE", "resident": "HOLD"}
    assert arbitrate(policy, signals) == ("market", "raise")
