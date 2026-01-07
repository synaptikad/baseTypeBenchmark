"""Benchmark orchestration for Benchmark Runner V3.

Sprint 3 - Benchmark BaseType V3

Provides complete benchmark execution:
- Multi-paradigm orchestration
- RAM gradient testing
- Results aggregation and export
- Report generation

Example:
    ```python
    from basetype_benchmark.runner.benchmark import (
        BenchmarkOrchestrator,
        BenchmarkResults,
    )

    orchestrator = BenchmarkOrchestrator(
        paradigms=["P1", "P2", "M1", "M2", "O2"],
        configs=configs,
    )

    results = orchestrator.run_full_benchmark(
        data_dir=Path("data/export"),
        output_path=Path("results.json"),
    )

    print(f"RAM viable for M1: {results.get_ram_viable('M1')} MB")
    ```
"""
from __future__ import annotations

from .results import (
    BenchmarkResults,
    ParadigmResults,
    BenchmarkConfig,
    compute_statistics,
)
from .scenario import (
    BenchmarkOrchestrator,
    ScenarioConfig,
)

__all__ = [
    # Results
    "BenchmarkResults",
    "ParadigmResults",
    "BenchmarkConfig",
    "compute_statistics",
    # Orchestration
    "BenchmarkOrchestrator",
    "ScenarioConfig",
]
