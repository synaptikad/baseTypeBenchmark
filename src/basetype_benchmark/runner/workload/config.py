"""Workload configuration dataclasses and YAML loading."""

import warnings
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional

import yaml


class MetricsStrategy(Enum):
    """How to collect metrics during workload."""
    PER_QUERY = "per_query"      # Reset peak before each query
    AGGREGATE = "aggregate"      # Reset only after load


class ExecutionMode(Enum):
    """How to execute the workload."""
    SEQUENTIAL = "sequential"    # Each query N times in order
    DURATION = "duration"        # Run for N seconds
    ITERATIONS = "iterations"    # Run N total queries


class SelectionStrategy(Enum):
    """How to select next query."""
    SEQUENTIAL = "sequential"        # Q1, Q2, ..., Q13, Q1, ...
    WEIGHTED_RANDOM = "weighted_random"  # Random based on weights
    ROUND_ROBIN = "round_robin"      # Proportional to weights


# Valid query IDs
VALID_QUERY_IDS = {"ALL"} | {f"Q{i}" for i in range(1, 14)}


@dataclass
class QuerySpec:
    """Specification for a single query in workload."""
    id: str                          # Q1, Q2, ..., Q13, or ALL
    weight: int = 10                 # Relative weight (default 10)
    category: str = "default"        # For reporting: dashboard, analytics, report


@dataclass
class MetricsConfig:
    """Metrics collection configuration."""
    strategy: MetricsStrategy = MetricsStrategy.PER_QUERY


@dataclass
class ExecutionConfig:
    """Workload execution configuration."""
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    duration_seconds: int = 60           # For DURATION mode
    iterations: int = 100                # For ITERATIONS mode
    iterations_per_query: int = 1        # For SEQUENTIAL mode
    concurrency: int = 1                 # Number of threads
    warmup_iterations: int = 0           # Warmup before measurement


@dataclass
class SelectionConfig:
    """Query selection configuration."""
    strategy: SelectionStrategy = SelectionStrategy.SEQUENTIAL
    seed: Optional[int] = None           # For reproducibility


@dataclass
class WorkloadConfig:
    """Complete workload configuration."""
    name: str
    description: str = ""
    version: str = "1.0"
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    queries: List[QuerySpec] = field(default_factory=list)
    selection: SelectionConfig = field(default_factory=SelectionConfig)

    @classmethod
    def load(cls, path: Path) -> "WorkloadConfig":
        """Load workload configuration from YAML file.

        Args:
            path: Path to YAML file

        Returns:
            WorkloadConfig instance

        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If file doesn't exist
        """
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        wl = data.get("workload", {})
        metrics_data = data.get("metrics", {})
        exec_data = data.get("execution", {})
        sel_data = data.get("selection", {})
        queries_data = data.get("queries", [])

        # Parse metrics
        metrics = MetricsConfig(
            strategy=MetricsStrategy(metrics_data.get("strategy", "per_query"))
        )

        # Parse execution
        execution = ExecutionConfig(
            mode=ExecutionMode(exec_data.get("mode", "sequential")),
            duration_seconds=exec_data.get("duration_seconds", 60),
            iterations=exec_data.get("iterations", 100),
            iterations_per_query=exec_data.get("iterations_per_query", 1),
            concurrency=exec_data.get("concurrency", 1),
            warmup_iterations=exec_data.get("warmup_iterations", 0),
        )

        # Parse selection
        selection = SelectionConfig(
            strategy=SelectionStrategy(sel_data.get("strategy", "sequential")),
            seed=sel_data.get("seed"),
        )

        # Parse and validate queries
        queries = []
        for q in queries_data:
            if isinstance(q, str):
                query_id = q
                weight = 10
                category = "default"
            else:
                query_id = q.get("id", "Q1")
                weight = q.get("weight", 10)
                category = q.get("category", "default")

            # Validate query_id
            if query_id not in VALID_QUERY_IDS:
                raise ValueError(
                    f"Invalid query_id: '{query_id}'. "
                    f"Must be 'ALL' or Q1-Q13."
                )

            queries.append(QuerySpec(
                id=query_id,
                weight=weight,
                category=category,
            ))

        config = cls(
            name=wl.get("name", path.stem),
            description=wl.get("description", ""),
            version=wl.get("version", "1.0"),
            metrics=metrics,
            execution=execution,
            queries=queries,
            selection=selection,
        )

        # Warn if per_query + concurrency > 1
        if (config.metrics.strategy == MetricsStrategy.PER_QUERY
            and config.execution.concurrency > 1):
            warnings.warn(
                "per_query metrics strategy with concurrency > 1 may give "
                "inaccurate per-query peak RAM (race condition on reset). "
                "Consider using 'aggregate' strategy for concurrent workloads.",
                UserWarning
            )

        return config

    def expand_queries(self, all_queries: List[str]) -> List[QuerySpec]:
        """Expand 'ALL' to actual query list.

        Args:
            all_queries: List of all available query IDs (e.g., ["Q1", "Q2", ...])

        Returns:
            List of QuerySpec with ALL expanded
        """
        result = []
        for q in self.queries:
            if q.id == "ALL":
                for qid in all_queries:
                    result.append(QuerySpec(
                        id=qid,
                        weight=q.weight,
                        category=q.category,
                    ))
            else:
                result.append(q)
        return result
