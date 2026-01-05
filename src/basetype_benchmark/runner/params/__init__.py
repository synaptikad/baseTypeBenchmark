"""Paradigm-specific parameter generation for benchmark queries.

This package provides parameter generators that produce idiomatic parameter
values for each database paradigm (SQL, Cypher, SPARQL). Each paradigm uses
its native syntax for pattern matching, date formatting, and other operations.

Architecture (Strategy Pattern):
    base.py      - Abstract ParamGenerator class with common logic
    sql.py       - SQLParamGenerator for P1/P2 (PostgreSQL)
    cypher.py    - CypherParamGenerator for M1/M2 (Memgraph)
    sparql.py    - SPARQLParamGenerator for O1/O2 (Oxigraph)
    registry.py  - Scenario → Generator mapping

Usage:
    from basetype_benchmark.runner.params import get_generator, get_query_variants

    # New API: paradigm-aware generation
    generator = get_generator("M1")
    variants = generator.generate_variants("Q13", "small-2d", dataset_info)

    # Legacy API: still available for backward compatibility
    variants = get_query_variants("Q13", "small-2d", dataset_info, scenario="M1")

Academic rationale:
    - Reproducibility: Each paradigm documented separately
    - Extensibility: New paradigm = one new file
    - Comparability: Paradigm differences explicit, not hidden in conditionals
    - Validation: Unit tests per paradigm

Paradigm-specific transforms:

    | Parameter   | SQL (P1/P2)      | Cypher (M1/M2)   | SPARQL (O1/O2)   |
    |-------------|------------------|------------------|------------------|
    | space_type  | office_%         | office_          | office_          |
    | date_start  | ISO 8601         | Unix timestamp   | xsd:date         |
    | date_end    | ISO 8601         | Unix timestamp   | xsd:date         |

Query patterns:

    SQL:    WHERE space_type LIKE '$SPACE_TYPE'        → LIKE 'office_%'
    Cypher: WHERE n.space_type STARTS WITH '$SPACE_TYPE' → STARTS WITH 'office_'
    SPARQL: FILTER(STRSTARTS(?x, "$SPACE_TYPE"))       → STRSTARTS("office_")
"""

# Re-export from registry for convenient access
from .registry import (
    get_generator,
    get_paradigm,
    list_scenarios,
    list_paradigms,
    GENERATOR_REGISTRY,
    PARADIGM_SCENARIOS,
)

# Re-export base class for type hints and extension
from .base import ParamGenerator

# Re-export paradigm-specific generators for direct instantiation
from .sql import SQLParamGenerator
from .cypher import CypherParamGenerator
from .sparql import SPARQLParamGenerator

# Legacy API: import from original params.py for backward compatibility
# These functions don't need paradigm-specific transforms
from ..params_core import (
    extract_params_from_query,
    get_query_params,
    extract_dataset_info,
    extract_dataset_info_from_parquet,
    extract_timeseries_range,
    extract_timeseries_range_from_parquet,
    substitute_params,
    get_nodes_csv_path,
)


def get_query_variants(
    query_id: str,
    profile: str,
    dataset_info: dict,
    seed: int = 42,
    scenario: str = "P1",
    n_variants: int = None,
    queries_dir=None,
) -> list:
    """Generate parameter variants for a query (paradigm-aware).

    This function wraps the paradigm-specific generators, providing
    backward compatibility with the original API while using the new
    Strategy Pattern implementation.

    Args:
        query_id: Query identifier (Q1, Q2, etc.)
        profile: Dataset profile (small-2d, medium-1w, etc.)
        dataset_info: Dataset information from extract_dataset_info()
        seed: Random seed for reproducibility
        scenario: Scenario code (P1, P2, M1, M2, O1, O2)
        n_variants: Number of variants (None = infer from profile)
        queries_dir: Path to queries/ directory

    Returns:
        List of parameter dicts, one per variant

    Example:
        >>> info = extract_dataset_info(nodes_csv, "M1")
        >>> variants = get_query_variants("Q13", "small-2d", info, scenario="M1")
        >>> print(variants[0]["space_type"])
        'office_'  # No % wildcard for Cypher
    """
    generator = get_generator(scenario)
    return generator.generate_variants(
        query_id=query_id,
        profile=profile,
        dataset_info=dataset_info,
        seed=seed,
        n_variants=n_variants,
        queries_dir=queries_dir,
        scenario=scenario,
    )


__all__ = [
    # Registry functions
    "get_generator",
    "get_paradigm",
    "list_scenarios",
    "list_paradigms",
    "GENERATOR_REGISTRY",
    "PARADIGM_SCENARIOS",
    # Base class
    "ParamGenerator",
    # Paradigm-specific generators
    "SQLParamGenerator",
    "CypherParamGenerator",
    "SPARQLParamGenerator",
    # Legacy API (backward compatible)
    "get_query_variants",
    "extract_params_from_query",
    "get_query_params",
    "extract_dataset_info",
    "extract_dataset_info_from_parquet",
    "extract_timeseries_range",
    "extract_timeseries_range_from_parquet",
    "substitute_params",
    "get_nodes_csv_path",
]
