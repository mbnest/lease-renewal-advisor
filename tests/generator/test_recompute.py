"""Flag recompute against the thresholds in docs/scenarios.md, including near misses."""

from datetime import date
from pathlib import Path

import pytest

from lease_renewal.decision.policy import load_policy
from lease_renewal.generator.recompute import flags_for

AS_OF = date(2026, 10, 1)


@pytest.fixture(scope="module")
def policy():
    return load_policy(Path("config/policy_spike.yaml"))


def home(**over) -> dict:
    """A home that earns no flags, overridable one field at a time."""
    base = {
        "current_rent": 2000,
        "demand": "high",
        "work_orders": [],
        "comps": {"median_rent": 2050, "trend": "up"},
        "payments": [{"due": f"2026-{m:02d}-01", "days_late": 0} for m in range(1, 10)],
        "complaints": [],
    }
    base.update(over)
    return base


@pytest.mark.unit
def test_clean_home_earns_nothing(policy):
    assert flags_for(home(), policy, AS_OF) == []


@pytest.mark.unit
def test_three_work_orders_on_one_system_is_chronic(policy):
    wos = [{"date": f"2026-{m:02d}-10", "system": "hvac", "cost": 100} for m in (4, 6, 8)]
    assert "chronic_maintenance" in flags_for(home(work_orders=wos), policy, AS_OF)


@pytest.mark.unit
def test_two_work_orders_on_one_system_is_a_decoy(policy):
    wos = [{"date": f"2026-{m:02d}-10", "system": "hvac", "cost": 100} for m in (4, 8)]
    assert flags_for(home(work_orders=wos), policy, AS_OF) == []


@pytest.mark.unit
def test_three_work_orders_on_different_systems_is_a_decoy(policy):
    wos = [
        {"date": "2026-04-10", "system": "hvac", "cost": 100},
        {"date": "2026-06-10", "system": "plumbing", "cost": 100},
        {"date": "2026-08-10", "system": "roof", "cost": 100},
    ]
    assert flags_for(home(work_orders=wos), policy, AS_OF) == []


@pytest.mark.unit
def test_maintenance_cost_above_the_rent_share_is_chronic(policy):
    """One expensive order: 1500 is above 5 percent of 24000 annual rent."""
    wos = [{"date": "2026-05-10", "system": "roof", "cost": 1500}]
    assert "chronic_maintenance" in flags_for(home(work_orders=wos), policy, AS_OF)


@pytest.mark.unit
def test_old_work_orders_fall_outside_the_window(policy):
    wos = [{"date": f"2024-{m:02d}-10", "system": "hvac", "cost": 100} for m in (4, 6, 8)]
    assert flags_for(home(work_orders=wos), policy, AS_OF) == []


@pytest.mark.unit
def test_complaint_unresolved_past_the_limit(policy):
    c = [{"opened": "2026-08-01", "resolved": None, "topic": "noise"}]
    assert "open_complaint" in flags_for(home(complaints=c), policy, AS_OF)


@pytest.mark.unit
def test_recent_complaint_is_a_decoy(policy):
    c = [{"opened": "2026-09-25", "resolved": None, "topic": "noise"}]
    assert flags_for(home(complaints=c), policy, AS_OF) == []


@pytest.mark.unit
def test_resolved_complaint_is_a_decoy(policy):
    c = [{"opened": "2026-02-01", "resolved": "2026-02-20", "topic": "noise"}]
    assert flags_for(home(complaints=c), policy, AS_OF) == []


@pytest.mark.unit
def test_three_late_payments_is_a_pattern(policy):
    pays = [{"due": f"2026-{m:02d}-01", "days_late": 6} for m in (3, 5, 7)]
    assert "late_payment_pattern" in flags_for(home(payments=pays), policy, AS_OF)


@pytest.mark.unit
def test_two_late_payments_is_a_decoy(policy):
    pays = [{"due": f"2026-{m:02d}-01", "days_late": 6} for m in (3, 7)]
    assert flags_for(home(payments=pays), policy, AS_OF) == []


@pytest.mark.unit
def test_rent_eight_percent_under_the_median_is_below_market(policy):
    """2392 against a 2600 median is an 8.0 percent gap, exactly at the threshold."""
    flags = flags_for(
        home(current_rent=2392, comps={"median_rent": 2600, "trend": "up"}), policy, AS_OF
    )
    assert "below_market" in flags


@pytest.mark.unit
def test_rent_just_under_the_margin_is_a_decoy(policy):
    """2400 against a 2600 median is a 7.7 percent gap, under the threshold."""
    flags = flags_for(
        home(current_rent=2400, comps={"median_rent": 2600, "trend": "up"}), policy, AS_OF
    )
    assert flags == []


@pytest.mark.unit
def test_soft_city_and_flat_trend_is_soft_demand(policy):
    flags = flags_for(
        home(demand="soft", comps={"median_rent": 2050, "trend": "flat"}), policy, AS_OF
    )
    assert "soft_demand" in flags


@pytest.mark.unit
def test_flat_trend_in_a_strong_city_is_a_decoy(policy):
    flags = flags_for(
        home(demand="high", comps={"median_rent": 2050, "trend": "flat"}), policy, AS_OF
    )
    assert flags == []


@pytest.mark.unit
def test_soft_city_with_a_rising_trend_is_a_decoy(policy):
    flags = flags_for(
        home(demand="soft", comps={"median_rent": 2050, "trend": "up"}), policy, AS_OF
    )
    assert flags == []
