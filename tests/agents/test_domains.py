"""The specialist split must leak nothing across domain boundaries."""

import json
from pathlib import Path

import pytest

from lease_renewal.agents.domains import DOMAIN_FIELDS, slice_for

HOMES = json.loads(Path("data/spike/homes.json").read_text())["homes"]
BY_ID = {h["home_id"]: h for h in HOMES}


@pytest.mark.unit
@pytest.mark.parametrize("specialist", list(DOMAIN_FIELDS))
def test_slice_carries_only_its_own_domain(specialist):
    others = {f for s, fields in DOMAIN_FIELDS.items() if s != specialist for f in fields}
    for home in HOMES:
        got = set(slice_for(home, specialist))
        assert not got & others, (specialist, got & others)


@pytest.mark.unit
def test_condition_specialist_never_sees_comps_or_messages():
    got = slice_for(BY_ID["spike-07-conflicting-signals"], "condition")
    assert "comps" not in got
    assert "messages" not in got
    assert got["work_orders"]


@pytest.mark.unit
def test_resident_specialist_sees_the_trap_message():
    """The protected reference reaches the resident specialist, which is the trap."""
    got = slice_for(BY_ID["spike-06-trap-treated"], "resident")
    assert len(got["messages"]) == 2


@pytest.mark.unit
def test_market_specialist_never_sees_work_orders_or_payments():
    got = slice_for(BY_ID["spike-03-chronic-maintenance"], "market")
    assert "work_orders" not in got
    assert "payments" not in got
    assert got["comps"]


@pytest.mark.unit
def test_every_domain_field_is_owned_by_exactly_one_specialist():
    seen = [f for fields in DOMAIN_FIELDS.values() for f in fields]
    assert len(seen) == len(set(seen))
