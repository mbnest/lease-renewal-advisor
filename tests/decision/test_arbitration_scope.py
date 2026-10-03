"""Arbitration binds only on a real conflict (ADR-018 scope)."""

from pathlib import Path

import pytest

from lease_renewal.decision.policy import arbitrate, has_conflict, load_policy

POLICY = load_policy(Path("config/policy_spike.yaml"))


@pytest.mark.unit
@pytest.mark.parametrize(
    ("signals", "conflict"),
    [
        ({"condition": "NONE", "market": "NONE", "resident": "NONE"}, False),
        ({"condition": "ESCALATE", "market": "NONE", "resident": "NONE"}, False),
        ({"condition": "NONE", "market": "HOLD", "resident": "NONE"}, False),
        ({"condition": "NONE", "market": "HOLD", "resident": "HOLD"}, False),
        ({"condition": "ESCALATE", "market": "RAISE", "resident": "NONE"}, True),
        ({"condition": "NONE", "market": "RAISE", "resident": "HOLD"}, True),
    ],
)
def test_conflict_detection(signals, conflict):
    assert has_conflict(signals) is conflict


@pytest.mark.unit
def test_conflict_resolves_to_the_highest_precedence_specialist():
    signals = {"condition": "ESCALATE", "market": "RAISE", "resident": "NONE"}
    assert has_conflict(signals)
    assert arbitrate(POLICY, signals) == ("condition", "hold")
