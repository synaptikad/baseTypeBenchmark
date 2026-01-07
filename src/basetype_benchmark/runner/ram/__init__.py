"""RAM gradient testing for Benchmark Runner V3.

Sprint 3 - Benchmark BaseType V3

Provides RAM as an experimental variable for benchmark testing:
- Container isolation for clean state
- Memory limits via docker update
- RAM gradient execution (decreasing levels)
- OOM detection and early termination

Key contribution from papier.md Section 3.4:
"Contrairement aux benchmarks LDBC/gMark qui ne testent pas
la contrainte RAM, notre protocole introduit la memoire
comme variable independante."

Example:
    ```python
    from basetype_benchmark.runner.ram import (
        IsolationManager,
        RAMGradientExecutor,
    )

    isolation = IsolationManager()
    isolation.start_paradigm("M1")

    executor = RAMGradientExecutor(
        paradigm="M1",
        isolation=isolation,
        configs={"M1": memgraph_config},
    )

    result = executor.run_gradient(
        queries=["Q1", "Q2", "Q3"],
        levels_mb=[32768, 16384, 8192],  # 32, 16, 8 GB
    )

    print(f"RAM viable for M1: {result.ram_viable_mb} MB")
    isolation.stop_paradigm("M1")
    ```
"""
from __future__ import annotations

from .isolation import (
    IsolationManager,
    IsolationError,
    ContainerSet,
    PARADIGM_CONTAINERS,
    get_paradigm_containers,
)
from .gradient import (
    RAMGradientExecutor,
    GradientError,
    GradientLevel,
    GradientResult,
    QueryRunResult,
    QueryStats,
)

__all__ = [
    # Isolation
    "IsolationManager",
    "IsolationError",
    "ContainerSet",
    "PARADIGM_CONTAINERS",
    "get_paradigm_containers",
    # Gradient
    "RAMGradientExecutor",
    "GradientError",
    "GradientLevel",
    "GradientResult",
    "QueryRunResult",
    "QueryStats",
]
