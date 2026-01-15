"""Base types and protocols for Query Runners.

Sprint 3 - Benchmark BaseType V3

Provides the QueryRunner protocol that all paradigm-specific runners
must implement, plus common base classes and utilities.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


# =============================================================================
# RESULT TYPES
# =============================================================================

class RunStatus(str, Enum):
    """Status of a single query run."""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    OOM = "oom"
    SKIPPED = "skipped"  # Query not supported for this paradigm (IMPOSSIBLE)


@dataclass
class RunResult:
    """Result of a single query execution."""
    rows: list[dict[str, Any]]
    duration_ms: float
    status: RunStatus = RunStatus.SUCCESS
    error_message: str | None = None
    row_count: int = 0

    def __post_init__(self):
        if self.row_count == 0:
            self.row_count = len(self.rows)


@dataclass
class HybridRunResult:
    """Result of a hybrid (graph + timeseries) query execution."""
    rows: list[dict[str, Any]]
    total_ms: float
    graph_ms: float
    ts_ms: float
    status: RunStatus = RunStatus.SUCCESS
    error_message: str | None = None
    row_count: int = 0
    # Intermediate data from graph phase
    point_ids: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.row_count == 0:
            self.row_count = len(self.rows)

    @property
    def duration_ms(self) -> float:
        """Alias for total_ms for compatibility with RunResult interface."""
        return self.total_ms


# =============================================================================
# PROTOCOL
# =============================================================================

@runtime_checkable
class QueryRunner(Protocol):
    """Protocol for query execution on a specific paradigm.

    All runners (PostgresRunner, MemgraphRunner) must implement this interface.

    Example:
        ```python
        runner = PostgresRunner(config)
        if runner.check_connection():
            result = runner.execute(
                "SELECT * FROM nodes WHERE id = $1",
                {"$1": "node_123"},
            )
            print(f"Got {result.row_count} rows in {result.duration_ms}ms")
        runner.close()
        ```
    """

    def execute(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: float = 300.0,
    ) -> RunResult:
        """Execute a query and return results.

        Args:
            query: Query string (SQL or Cypher)
            params: Query parameters (optional)
            timeout_seconds: Maximum execution time

        Returns:
            RunResult with rows, timing, and status
        """
        ...

    def check_connection(self) -> bool:
        """Check if database connection is alive.

        Returns:
            True if connected and responsive, False otherwise
        """
        ...

    def close(self) -> None:
        """Close database connection and release resources."""
        ...

    def get_query_plan(self, query: str, params: dict[str, Any] | None = None) -> dict | None:
        """Get query execution plan (EXPLAIN).

        Args:
            query: Query to analyze
            params: Query parameters

        Returns:
            Execution plan as dict, or None if not supported
        """
        ...


@runtime_checkable
class HybridQueryRunner(Protocol):
    """Protocol for hybrid query execution (M2).

    Hybrid runners orchestrate two-phase execution:
    1. Graph phase: Execute Cypher to get point_ids
    2. Timeseries phase: Execute SQL with collected point_ids
    """

    def execute_hybrid(
        self,
        graph_query: str,
        ts_query: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: float = 300.0,
    ) -> HybridRunResult:
        """Execute a hybrid query in two phases.

        Args:
            graph_query: Cypher query (phase 1)
            ts_query: SQL query with $point_ids placeholder (phase 2)
            params: Shared parameters for both queries
            timeout_seconds: Maximum total execution time

        Returns:
            HybridRunResult with rows, timing breakdown, and status
        """
        ...


# =============================================================================
# BASE CLASS
# =============================================================================

class BaseRunner(ABC):
    """Abstract base class with shared logic for runners."""

    def __init__(self, paradigm: str):
        """Initialize runner.

        Args:
            paradigm: Paradigm identifier (P1, P2, M1, M2)
        """
        self.paradigm = paradigm
        self._connected = False

    @abstractmethod
    def execute(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: float = 300.0,
    ) -> RunResult:
        """Execute query - must be implemented by subclasses."""
        ...

    @abstractmethod
    def check_connection(self) -> bool:
        """Check connection - must be implemented by subclasses."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Close connection - must be implemented by subclasses."""
        ...

    def get_query_plan(self, query: str, params: dict[str, Any] | None = None) -> dict | None:
        """Default implementation returns None (not supported)."""
        return None

    def _make_error_result(self, error: Exception, duration_ms: float = 0.0) -> RunResult:
        """Create an error RunResult from an exception."""
        error_type = type(error).__name__

        # Detect OOM from error message
        error_msg = str(error).lower()
        if "out of memory" in error_msg or "oom" in error_msg or "cannot allocate" in error_msg:
            status = RunStatus.OOM
        elif "timeout" in error_msg or "timed out" in error_msg:
            status = RunStatus.TIMEOUT
        else:
            status = RunStatus.ERROR

        return RunResult(
            rows=[],
            duration_ms=duration_ms,
            status=status,
            error_message=f"{error_type}: {error}",
        )


# =============================================================================
# FACTORY TYPES
# =============================================================================

# Type alias for runner factory functions
RunnerFactory = type[BaseRunner]

# Registry of runner classes by paradigm
RUNNER_REGISTRY: dict[str, RunnerFactory] = {}


def register_runner(paradigm: str):
    """Decorator to register a runner class for a paradigm.

    Example:
        @register_runner("P1")
        class PostgresRunner(BaseRunner):
            ...
    """
    def decorator(cls: RunnerFactory) -> RunnerFactory:
        RUNNER_REGISTRY[paradigm.upper()] = cls
        return cls
    return decorator
