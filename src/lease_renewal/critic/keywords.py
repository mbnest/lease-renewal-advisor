"""Minimal keyword critic for the spike.

Code checks only. A hit blocks the case, which ends it in BLOCKED for manual
review and keeps the recommendation as the pre-block proposal (ADR-016). The
real critic adds a compliance classifier (ADR-004); keyword rules alone are
known to be a weak proxy and are here to exercise the BLOCKED path.
"""

import re

# Terms that reference a protected characteristic. Whole words are matched on both
# boundaries, since a prefix match turns "age" into a hit on "agent". Stems are
# matched on the leading boundary only, so one entry covers a word's variants.
WORD_TERMS = (
    "race",
    "religion",
    "religious",
    "church",
    "mosque",
    "synagogue",
    "national origin",
    "ethnicity",
    "ethnic",
    "disability",
    "disabled",
    "familial status",
    "children",
    "child",
    "marital status",
    "married",
    "sex",
    "gender",
    "age",
    "nationality",
)

STEM_TERMS = (
    "pregnan",
    "immigra",
)

BLOCKED = "BLOCKED"


def scan(text: str) -> list[str]:
    """Protected-characteristic terms present in the text."""
    lowered = text.lower()
    hits = [t for t in WORD_TERMS if re.search(rf"\b{re.escape(t)}\b", lowered)]
    hits += [t for t in STEM_TERMS if re.search(rf"\b{re.escape(t)}", lowered)]
    return hits


def review(reasoning: str, draft_message: str, arbitration_note: str) -> dict:
    """Check what the agents wrote. The resident's own words are not checked."""
    hits = sorted(
        {t for field in (reasoning, draft_message, arbitration_note) for t in scan(field)}
    )
    return {"verdict": BLOCKED if hits else "pass", "hits": hits}
