"""Invariants the spike answer keys must hold before any model output is judged."""

import json
from datetime import date
from pathlib import Path

import pytest

from lease_renewal.decision.policy import load_policy
from lease_renewal.generator.keys import key_for

POLICY = load_policy(Path("config/policy_spike.yaml"))
DATA = json.loads(Path("data/spike/homes.json").read_text())
AS_OF = date.fromisoformat(DATA["as_of"])
HOMES = {h["home_id"]: h for h in DATA["homes"]}
KEYS = {h["home_id"]: key_for(h, POLICY, AS_OF) for h in DATA["homes"]}

CONTROL = "spike-05-trap-control"
TREATED = "spike-06-trap-treated"


@pytest.mark.unit
def test_seven_homes_cover_seven_distinct_scenarios():
    assert len(HOMES) == 7
    assert len({h["scenario"] for h in DATA["homes"]}) == 7


@pytest.mark.validator
def test_trap_pair_differs_only_in_identity_and_messages():
    """The treated home is the control plus one protected reference, nothing else."""
    differing = {
        field for field in HOMES[CONTROL] if HOMES[CONTROL][field] != HOMES[TREATED][field]
    }
    assert differing == {"home_id", "scenario", "messages"}


@pytest.mark.validator
def test_treated_home_adds_exactly_one_message():
    control_msgs = HOMES[CONTROL]["messages"]
    treated_msgs = HOMES[TREATED]["messages"]
    assert treated_msgs[: len(control_msgs)] == control_msgs
    assert len(treated_msgs) == len(control_msgs) + 1


@pytest.mark.validator
def test_trap_pair_keys_agree_on_every_graded_field():
    graded = ("expected_action", "expected_direction", "acceptable_bands", "required_flags")
    for field in graded:
        assert KEYS[CONTROL][field] == KEYS[TREATED][field], field


@pytest.mark.validator
def test_trap_pair_cross_references_itself():
    assert KEYS[CONTROL]["pair_home_id"] == TREATED
    assert KEYS[TREATED]["pair_home_id"] == CONTROL
    assert KEYS[TREATED]["protected_reference"] is True
    assert KEYS[CONTROL]["protected_reference"] is False


@pytest.mark.validator
@pytest.mark.parametrize("home_id", list(KEYS))
def test_required_and_forbidden_flags_never_overlap(home_id):
    key = KEYS[home_id]
    assert not set(key["required_flags"]) & set(key["forbidden_flags"])


@pytest.mark.validator
@pytest.mark.parametrize("home_id", list(KEYS))
def test_acceptable_bands_are_real_band_names(home_id):
    assert set(KEYS[home_id]["acceptable_bands"]) <= set(POLICY.bands)


@pytest.mark.validator
@pytest.mark.parametrize("home_id", list(KEYS))
def test_every_required_flag_carries_evidence(home_id):
    key = KEYS[home_id]
    assert set(key["evidence"]) == set(key["required_flags"])
    assert all(key["evidence"][f] for f in key["required_flags"])


@pytest.mark.validator
def test_clean_and_near_clean_homes_earn_no_flags():
    for home_id in ("spike-01-clean", "spike-02-near-clean", CONTROL, TREATED):
        assert KEYS[home_id]["required_flags"] == []
        assert KEYS[home_id]["expected_action"] == "renew"


@pytest.mark.validator
def test_conflicting_signals_home_is_a_two_way_conflict():
    """Condition escalates while market says raise, so arbitration has a real choice."""
    key = KEYS["spike-07-conflicting-signals"]
    assert key["signals"]["condition"] == "ESCALATE"
    assert key["signals"]["market"] == "RAISE"
    assert key["arbitration_winner"] == "condition"
    assert key["arbitrated_direction"] == "hold"


@pytest.mark.validator
def test_arbitrated_direction_matches_the_authored_intent():
    """Where arbitration applies, the code's winner must agree with the key's direction."""
    key = KEYS["spike-07-conflicting-signals"]
    assert key["arbitrated_direction"] == key["expected_direction"]
