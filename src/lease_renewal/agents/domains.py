"""Split a home record into the three specialist data domains.

Each specialist sees only its own domain (ADR-002, docs/scenarios.md). The split
is enforced here rather than by prompt wording, so a specialist cannot reason
about data it should not have.
"""

SHARED = ("home_id", "bedrooms", "current_rent", "lease_end")

DOMAIN_FIELDS = {
    "condition": ("work_orders",),
    "market": ("city", "rate_tier", "demand", "comps"),
    "resident": ("payments", "complaints", "messages"),
}

DOMAIN_FLAGS = {
    "condition": ("chronic_maintenance",),
    "market": ("below_market", "soft_demand"),
    "resident": ("late_payment_pattern", "open_complaint"),
}


def slice_for(home: dict, specialist: str) -> dict:
    """The data one specialist is allowed to see."""
    fields = SHARED + DOMAIN_FIELDS[specialist]
    return {k: home[k] for k in fields if k in home}
