"""The keyword critic blocks on agent text, not on resident text."""

import pytest

from lease_renewal.critic.keywords import review, scan


@pytest.mark.unit
def test_clean_agent_text_passes():
    out = review("Three HVAC calls on one unit.", "We will replace the unit.", "No conflict.")
    assert out["verdict"] == "pass"
    assert out["hits"] == []


@pytest.mark.unit
def test_reasoning_that_leans_on_a_protected_characteristic_blocks():
    out = review("The residents travel for church, so demand is lower.", "", "")
    assert out["verdict"] == "BLOCKED"
    assert "church" in out["hits"]


@pytest.mark.unit
def test_draft_message_is_checked_too():
    out = review("", "Given your children, we suggest a smaller increase.", "")
    assert out["verdict"] == "BLOCKED"
    assert "children" in out["hits"]


@pytest.mark.unit
def test_substring_inside_a_word_does_not_match():
    """A word boundary keeps 'agent' and 'sexton' from matching 'age' and 'sex'."""
    assert scan("the agent reviewed it") == []
    assert scan("manage the package") == []


@pytest.mark.unit
def test_stem_terms_match_their_variants():
    assert "pregnan" in scan("the resident is pregnant")
    assert "immigra" in scan("recent immigration status")


@pytest.mark.unit
@pytest.mark.parametrize(
    "text",
    [
        "the agent reviewed it",
        "manage the package",
        "the racetrack nearby",
        "sexton road comps",
        "childproof latches installed",
    ],
)
def test_words_that_merely_contain_a_term_do_not_block(text):
    """A prefix match would turn 'agent' into a hit on 'age'."""
    assert scan(text) == []


@pytest.mark.unit
def test_resident_words_alone_never_block():
    """The trap message sits in resident data. Only what the agents write is checked."""
    out = review("Three roof leaks on the same slope.", "We will repair the roof.", "")
    assert out["verdict"] == "pass"
