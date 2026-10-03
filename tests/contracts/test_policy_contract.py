"""The policy config contract, and the committed schema that must match it."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from lease_renewal.contracts.policy import BandName, FlagType, PolicyConfig

CONFIG = Path("config/policy_v1.yaml")


def valid() -> dict:
    """A minimal config that satisfies every contract rule."""
    return {
        "version": "policy_test",
        "thresholds": {
            "chronic_wo_same_system_count": 3,
            "chronic_window_months": 12,
            "chronic_cost_pct_of_annual_rent": 5.0,
            "late_payment_count": 3,
            "late_payment_window_months": 12,
            "below_market_pct": 8.0,
            "soft_demand_city_values": ["soft"],
            "soft_demand_trend_values": ["flat", "down"],
            "open_complaint_days": 30,
        },
        "severity_tags": {
            "chronic_maintenance": "escalate",
            "open_complaint": "escalate",
            "late_payment_pattern": "note",
            "below_market": "note",
            "soft_demand": "note",
        },
        "combining_rule": "highest_severity_wins",
        "arbitration_precedence": ["condition", "market", "resident"],
        "bands": {
            "REDUCE": {
                "lower": -5.0,
                "upper": 0.0,
                "lower_inclusive": True,
                "upper_inclusive": False,
            },
            "HOLD": {"lower": 0.0, "upper": 0.0, "lower_inclusive": True, "upper_inclusive": True},
            "LOW": {"lower": 0.0, "upper": 2.0, "lower_inclusive": False, "upper_inclusive": True},
            "MODERATE": {
                "lower": 2.0,
                "upper": 4.0,
                "lower_inclusive": False,
                "upper_inclusive": True,
            },
            "HIGH": {"lower": 4.0, "upper": 6.0, "lower_inclusive": False, "upper_inclusive": True},
        },
        "clamp": {"floor_pct": -5.0, "cap_pct": 6.0},
    }


@pytest.mark.validator
def test_a_complete_config_validates():
    assert PolicyConfig.model_validate(valid()).version == "policy_test"


@pytest.mark.validator
def test_unknown_fields_are_rejected():
    """A renamed contract field must fail loudly, not be silently ignored."""
    bad = valid() | {"unexpected": 1}
    with pytest.raises(ValidationError, match="unexpected"):
        PolicyConfig.model_validate(bad)


@pytest.mark.validator
@pytest.mark.parametrize("flag", list(FlagType.__args__))
def test_every_flag_type_needs_a_severity_tag(flag):
    bad = valid()
    del bad["severity_tags"][flag]
    with pytest.raises(ValidationError, match="severity tag"):
        PolicyConfig.model_validate(bad)


@pytest.mark.validator
@pytest.mark.parametrize("band", list(BandName.__args__))
def test_every_band_must_be_defined(band):
    bad = valid()
    del bad["bands"][band]
    with pytest.raises(ValidationError, match="bands not defined"):
        PolicyConfig.model_validate(bad)


@pytest.mark.validator
def test_precedence_must_list_each_specialist_once():
    bad = valid() | {"arbitration_precedence": ["condition", "condition", "market"]}
    with pytest.raises(ValidationError, match="each specialist once"):
        PolicyConfig.model_validate(bad)


@pytest.mark.validator
def test_precedence_may_not_omit_a_specialist():
    bad = valid() | {"arbitration_precedence": ["condition", "market"]}
    with pytest.raises(ValidationError, match="each specialist once"):
        PolicyConfig.model_validate(bad)


@pytest.mark.validator
def test_band_edges_must_be_ordered():
    bad = valid()
    bad["bands"]["LOW"] = {
        "lower": 2.0,
        "upper": 0.0,
        "lower_inclusive": False,
        "upper_inclusive": True,
    }
    with pytest.raises(ValidationError, match="above upper"):
        PolicyConfig.model_validate(bad)


@pytest.mark.validator
def test_clamp_floor_must_not_exceed_the_cap():
    bad = valid() | {"clamp": {"floor_pct": 6.0, "cap_pct": -5.0}}
    with pytest.raises(ValidationError, match="above cap"):
        PolicyConfig.model_validate(bad)


@pytest.mark.validator
def test_clamp_may_not_reach_outside_the_bands():
    """A clamped value with no band would leave grading nowhere to put it."""
    bad = valid() | {"clamp": {"floor_pct": -9.0, "cap_pct": 6.0}}
    with pytest.raises(ValidationError, match="outside"):
        PolicyConfig.model_validate(bad)


@pytest.mark.validator
def test_the_shipped_config_satisfies_the_contract():
    """The config in the repo must validate against the committed contract."""
    config = PolicyConfig.model_validate(yaml.safe_load(CONFIG.read_text()))
    assert config.clamp.floor_pct == -5.0
    assert config.clamp.cap_pct == 6.0
