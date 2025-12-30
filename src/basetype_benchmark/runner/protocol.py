"""Benchmark protocol configuration.

Defines warmup, runs, and variants per profile scale.
Based on papier.md Section 3.4.
"""

from dataclasses import dataclass
from typing import Dict

# Profile scale -> protocol config
# Larger profiles get more runs to reflect real-world usage patterns
PROTOCOL_BY_SCALE = {
    "small": {"n_warmup": 3, "n_runs": 10, "n_variants": 3},    # 30 total/query
    "medium": {"n_warmup": 3, "n_runs": 30, "n_variants": 5},   # 150 total/query
    "large": {"n_warmup": 3, "n_runs": 100, "n_variants": 10},  # 1000 total/query
}

# Queries by scenario
QUERIES = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13"]

# Query types for hybrid scenarios (M2, O2)
QUERY_TYPE = {
    "Q1": "graph_only",
    "Q2": "graph_only",
    "Q3": "graph_only",
    "Q4": "graph_only",
    "Q5": "graph_only",
    "Q6": "ts_direct",      # Direct TimescaleDB, point_id as parameter
    "Q7": "hybrid",         # Graph selection -> TS aggregation
    "Q8": "hybrid",
    "Q9": "hybrid",
    "Q10": "hybrid",
    "Q11": "hybrid",
    "Q12": "hybrid",
    "Q13": "hybrid",
}


@dataclass
class Protocol:
    """Benchmark protocol configuration."""
    n_warmup: int
    n_runs: int
    n_variants: int

    @property
    def total_per_query(self) -> int:
        return self.n_runs * self.n_variants


def get_protocol(profile: str) -> Protocol:
    """Get protocol config for a profile.

    Args:
        profile: Profile name (e.g., 'small-2d', 'medium-1w')

    Returns:
        Protocol configuration
    """
    # Extract scale from profile name
    scale = profile.split("-")[0] if "-" in profile else profile

    config = PROTOCOL_BY_SCALE.get(scale, PROTOCOL_BY_SCALE["small"])
    return Protocol(**config)


def get_scale(profile: str) -> str:
    """Extract scale from profile name."""
    return profile.split("-")[0] if "-" in profile else profile
