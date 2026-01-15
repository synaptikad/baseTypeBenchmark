"""Query runners for Benchmark Runner V3.

Sprint 3 - Benchmark BaseType V3

Provides query execution for all 4 paradigms:
- P1: PostgreSQL relational (PostgresRunner)
- P2: PostgreSQL JSONB (PostgresRunner)
- M1: Memgraph standalone (MemgraphRunner)
- M2: Memgraph + TimescaleDB (HybridRunner)

Example:
    ```python
    from basetype_benchmark.runner.runners import get_runner
    from basetype_benchmark.runner.config import PostgresConfig

    config = PostgresConfig(dsn="postgresql://...")
    runner = get_runner("P1", config)

    result = runner.execute("SELECT * FROM nodes LIMIT 10")
    print(f"Got {result.row_count} rows in {result.duration_ms}ms")

    runner.close()
    ```
"""
from __future__ import annotations

from typing import Union

from ..config import (
    PostgresConfig,
    MemgraphConfig,
)
from .base import (
    QueryRunner,
    HybridQueryRunner,
    BaseRunner,
    RunResult,
    RunStatus,
    HybridRunResult,
    RUNNER_REGISTRY,
    register_runner,
)
from .postgres import PostgresRunner
from .memgraph import MemgraphRunner
from .hybrid import (
    HybridRunner,
    M2HybridRunner,
)

__all__ = [
    # Protocols
    "QueryRunner",
    "HybridQueryRunner",
    "BaseRunner",
    # Result types
    "RunResult",
    "RunStatus",
    "HybridRunResult",
    # Runners
    "PostgresRunner",
    "MemgraphRunner",
    "HybridRunner",
    "M2HybridRunner",
    # Factory
    "get_runner",
    "get_hybrid_runner",
    # Registry
    "RUNNER_REGISTRY",
    "register_runner",
]


# Type alias for configs
ConfigType = Union[PostgresConfig, MemgraphConfig]


def get_runner(
    paradigm: str,
    config: ConfigType,
) -> Union[PostgresRunner, MemgraphRunner]:
    """Factory to get the appropriate runner for a paradigm.

    For hybrid paradigm (M2), use get_hybrid_runner() instead.

    Args:
        paradigm: P1, P2, M1, or M2
        config: Appropriate config for the paradigm

    Returns:
        Runner instance

    Raises:
        ValueError: If paradigm is invalid
        TypeError: If config type doesn't match paradigm

    Example:
        ```python
        runner = get_runner("P1", PostgresConfig(...))
        result = runner.execute("SELECT 1")
        runner.close()
        ```
    """
    paradigm = paradigm.upper()

    if paradigm in ("P1", "P2"):
        if not isinstance(config, PostgresConfig):
            raise TypeError(f"PostgresConfig required for {paradigm}")
        return PostgresRunner(config, paradigm=paradigm)

    elif paradigm in ("M1", "M2"):
        if not isinstance(config, MemgraphConfig):
            raise TypeError(f"MemgraphConfig required for {paradigm}")
        return MemgraphRunner(config, paradigm=paradigm)

    else:
        raise ValueError(
            f"Unknown paradigm: {paradigm}. "
            f"Valid options: P1, P2, M1, M2"
        )


def get_hybrid_runner(
    paradigm: str,
    graph_config: MemgraphConfig,
    ts_config: PostgresConfig,
) -> HybridRunner:
    """Factory to get a hybrid runner for M2.

    Hybrid runners orchestrate two-phase execution:
    1. Graph phase (Cypher)
    2. Timeseries phase (SQL)

    Args:
        paradigm: M2
        graph_config: Config for graph database
        ts_config: Config for TimescaleDB

    Returns:
        HybridRunner instance

    Raises:
        ValueError: If paradigm is not M2
        TypeError: If config types don't match paradigm

    Example:
        ```python
        runner = get_hybrid_runner(
            "M2",
            MemgraphConfig(uri="bolt://localhost:7687"),
            PostgresConfig(dsn="postgresql://..."),
        )
        result = runner.execute_hybrid(
            graph_query="MATCH (p:Point) RETURN p.id",
            ts_query="SELECT * FROM timeseries WHERE point_id = ANY(%(point_ids)s)",
        )
        runner.close()
        ```
    """
    paradigm = paradigm.upper()

    if paradigm == "M2":
        if not isinstance(graph_config, MemgraphConfig):
            raise TypeError("MemgraphConfig required for M2 graph")
        return M2HybridRunner(graph_config, ts_config)

    else:
        raise ValueError(
            f"Hybrid runner not available for {paradigm}. "
            f"Valid options: M2"
        )
