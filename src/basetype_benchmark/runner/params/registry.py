"""Registry for paradigm-specific parameter generators.

This module provides a central registry that maps scenarios to their
appropriate parameter generator. This allows the benchmark runner to
obtain the correct generator without knowing paradigm details.

Usage:
    from basetype_benchmark.runner.params import get_generator

    generator = get_generator("P1")
    variants = generator.generate_variants(query_id, profile, dataset_info)
"""

from typing import Dict, Type

from .base import ParamGenerator
from .sql import SQLParamGenerator
from .cypher import CypherParamGenerator
from .sparql import SPARQLParamGenerator


# Registry mapping scenario codes to generator classes
GENERATOR_REGISTRY: Dict[str, Type[ParamGenerator]] = {
    # SQL paradigm (PostgreSQL)
    "P1": SQLParamGenerator,
    "P2": SQLParamGenerator,
    # Cypher paradigm (Memgraph)
    "M1": CypherParamGenerator,
    "M2": CypherParamGenerator,
    # SPARQL paradigm (Oxigraph)
    "O1": SPARQLParamGenerator,
    "O2": SPARQLParamGenerator,
}

# Paradigm groupings for documentation
PARADIGM_SCENARIOS: Dict[str, list] = {
    "sql": ["P1", "P2"],
    "cypher": ["M1", "M2"],
    "sparql": ["O1", "O2"],
}


def get_generator(scenario: str) -> ParamGenerator:
    """Get the parameter generator for a scenario.

    Args:
        scenario: Scenario code (P1, P2, M1, M2, O1, O2)

    Returns:
        ParamGenerator instance for the scenario's paradigm

    Raises:
        ValueError: If scenario is not recognized
    """
    scenario_upper = scenario.upper()

    if scenario_upper not in GENERATOR_REGISTRY:
        valid = ", ".join(sorted(GENERATOR_REGISTRY.keys()))
        raise ValueError(f"Unknown scenario: {scenario}. Valid scenarios: {valid}")

    generator_class = GENERATOR_REGISTRY[scenario_upper]
    return generator_class()


def get_paradigm(scenario: str) -> str:
    """Get the paradigm name for a scenario.

    Args:
        scenario: Scenario code (P1, P2, M1, M2, O1, O2)

    Returns:
        Paradigm name (sql, cypher, sparql)

    Raises:
        ValueError: If scenario is not recognized
    """
    scenario_upper = scenario.upper()

    for paradigm, scenarios in PARADIGM_SCENARIOS.items():
        if scenario_upper in scenarios:
            return paradigm

    valid = ", ".join(sorted(GENERATOR_REGISTRY.keys()))
    raise ValueError(f"Unknown scenario: {scenario}. Valid scenarios: {valid}")


def list_scenarios() -> list:
    """List all supported scenario codes.

    Returns:
        Sorted list of scenario codes
    """
    return sorted(GENERATOR_REGISTRY.keys())


def list_paradigms() -> Dict[str, list]:
    """List all paradigms and their scenarios.

    Returns:
        Dict mapping paradigm names to scenario lists
    """
    return PARADIGM_SCENARIOS.copy()
