"""Workload configuration and execution.

This module provides a YAML-configurable workload system for
running realistic benchmark scenarios.

Usage:
    from basetype_benchmark.runner.workload import WorkloadConfig, WorkloadExecutor

    config = WorkloadConfig.load("config/workloads/bos_operational.yaml")
    executor = WorkloadExecutor(
        config=config,
        query_executor=lambda qid: (engine.execute_query(qid)[0], 0, None),
        containers=["timescaledb"],
        all_queries=["Q1", "Q2", ..., "Q13"],
    )
    result = executor.run()
"""

from .config import (
    WorkloadConfig,
    QuerySpec,
    MetricsStrategy,
    ExecutionMode,
    SelectionStrategy,
    MetricsConfig,
    ExecutionConfig,
    SelectionConfig,
)
from .selector import (
    QuerySelector,
    SequentialSelector,
    WeightedRandomSelector,
    RoundRobinSelector,
    create_selector,
)
from .executor import (
    WorkloadExecutor,
    WorkloadResult,
    LatencyStats,
)

__all__ = [
    # Config
    "WorkloadConfig",
    "QuerySpec",
    "MetricsStrategy",
    "ExecutionMode",
    "SelectionStrategy",
    "MetricsConfig",
    "ExecutionConfig",
    "SelectionConfig",
    # Selectors
    "QuerySelector",
    "SequentialSelector",
    "WeightedRandomSelector",
    "RoundRobinSelector",
    "create_selector",
    # Executor
    "WorkloadExecutor",
    "WorkloadResult",
    "LatencyStats",
]
