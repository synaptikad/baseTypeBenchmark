"""Query execution models for Benchmark Runner V3.

Defines QueryPlan for planned executions and QueryResult for results.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field

from ..config import EngineType, ParadigmStatus


class ExecutionStatus(str, Enum):
    """Status of a query execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"
    IMPOSSIBLE = "impossible"


class QueryDialect(str, Enum):
    """Query language dialect."""
    SQL = "sql"
    CYPHER = "cypher"


class QueryPhase(str, Enum):
    """Phase of query execution for hybrid paradigms."""
    SINGLE = "single"      # Single-phase query (P1, P2, M1)
    GRAPH = "graph"        # Graph phase of hybrid query (M2)
    TIMESERIES = "ts"      # Timeseries phase of hybrid query


class QueryText(BaseModel):
    """Query text with dialect information."""
    dialect: QueryDialect
    text: str
    phase: QueryPhase = QueryPhase.SINGLE
    file_path: Optional[Path] = None

    def with_params(self, params: dict[str, Any]) -> str:
        """Return query text with parameters substituted (for display only)."""
        result = self.text
        for key, value in params.items():
            # Simple substitution for display purposes
            if isinstance(value, str):
                display_value = f"'{value}'"
            elif isinstance(value, (list, tuple)):
                display_value = str(list(value))
            else:
                display_value = str(value)
            result = result.replace(f"${key}", display_value)
            result = result.replace(f":{key}", display_value)
            result = result.replace(f"?{key}", display_value)
        return result


class QueryPlan(BaseModel):
    """Planned query execution.

    Represents a query ready to be executed on a specific paradigm,
    with all necessary information for execution.
    """
    query_id: str
    query_name: str
    engine: EngineType
    paradigm_status: ParadigmStatus

    # Query texts (may have multiple for hybrid paradigms)
    queries: list[QueryText] = Field(default_factory=list)

    # Parameters
    parameters: dict[str, Any] = Field(default_factory=dict)

    # Execution settings
    timeout_seconds: float = 300.0
    warmup_runs: int = 0
    timed_runs: int = 1

    # Metadata
    category: str = ""
    intention: str = ""
    relations: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def can_execute(self) -> bool:
        """Check if query can be executed."""
        return self.paradigm_status != ParadigmStatus.IMPOSSIBLE

    @computed_field
    @property
    def is_hybrid(self) -> bool:
        """Check if this is a hybrid query (graph + timeseries)."""
        return any(q.phase != QueryPhase.SINGLE for q in self.queries)

    @computed_field
    @property
    def primary_dialect(self) -> Optional[QueryDialect]:
        """Get the primary query dialect."""
        if self.queries:
            return self.queries[0].dialect
        return None

    def get_query(self, phase: QueryPhase = QueryPhase.SINGLE) -> Optional[QueryText]:
        """Get query text for a specific phase."""
        for q in self.queries:
            if q.phase == phase:
                return q
        # Fallback: return first query if phase not found
        return self.queries[0] if self.queries else None

    def get_graph_query(self) -> Optional[QueryText]:
        """Get graph phase query for hybrid execution."""
        return self.get_query(QueryPhase.GRAPH)

    def get_ts_query(self) -> Optional[QueryText]:
        """Get timeseries phase query for hybrid execution."""
        return self.get_query(QueryPhase.TIMESERIES)


class ResourceMetrics(BaseModel):
    """Resource usage metrics during query execution."""
    cpu_percent_avg: float = 0.0
    cpu_percent_max: float = 0.0
    memory_mb_avg: float = 0.0
    memory_mb_max: float = 0.0
    memory_limit_mb: Optional[float] = None
    io_read_mb: float = 0.0
    io_write_mb: float = 0.0

    @computed_field
    @property
    def memory_percent_max(self) -> Optional[float]:
        """Memory usage as percentage of limit."""
        if self.memory_limit_mb and self.memory_limit_mb > 0:
            return (self.memory_mb_max / self.memory_limit_mb) * 100
        return None


class TimingMetrics(BaseModel):
    """Timing metrics for query execution."""
    execution_time_ms: float = 0.0
    planning_time_ms: Optional[float] = None

    # For hybrid queries
    graph_time_ms: Optional[float] = None
    ts_time_ms: Optional[float] = None

    # For multiple runs
    warmup_times_ms: list[float] = Field(default_factory=list)
    run_times_ms: list[float] = Field(default_factory=list)

    @computed_field
    @property
    def avg_time_ms(self) -> float:
        """Average execution time from timed runs."""
        if self.run_times_ms:
            return sum(self.run_times_ms) / len(self.run_times_ms)
        return self.execution_time_ms

    @computed_field
    @property
    def min_time_ms(self) -> float:
        """Minimum execution time from timed runs."""
        if self.run_times_ms:
            return min(self.run_times_ms)
        return self.execution_time_ms

    @computed_field
    @property
    def max_time_ms(self) -> float:
        """Maximum execution time from timed runs."""
        if self.run_times_ms:
            return max(self.run_times_ms)
        return self.execution_time_ms

    @computed_field
    @property
    def stddev_ms(self) -> float:
        """Standard deviation of execution times."""
        if len(self.run_times_ms) < 2:
            return 0.0
        avg = self.avg_time_ms
        variance = sum((t - avg) ** 2 for t in self.run_times_ms) / len(self.run_times_ms)
        return variance ** 0.5


class QueryResult(BaseModel):
    """Result of a query execution.

    Contains the result data, timing, resource metrics, and validation status.
    """
    # Identity
    query_id: str
    engine: EngineType
    status: ExecutionStatus

    # Result data
    rows: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    columns: list[str] = Field(default_factory=list)

    # Metrics
    timing: TimingMetrics = Field(default_factory=TimingMetrics)
    resources: ResourceMetrics = Field(default_factory=ResourceMetrics)

    # Validation
    validated: bool = False
    validation_error: Optional[str] = None
    matches_expected: Optional[bool] = None

    # Error info
    error_message: Optional[str] = None
    error_type: Optional[str] = None

    # Metadata
    executed_at: datetime = Field(default_factory=datetime.now)
    dataset_profile: str = ""

    # For hybrid queries
    intermediate_results: dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.SUCCESS

    @computed_field
    @property
    def execution_time_ms(self) -> float:
        """Convenience accessor for execution time."""
        return self.timing.execution_time_ms

    @computed_field
    @property
    def memory_mb(self) -> float:
        """Convenience accessor for peak memory."""
        return self.resources.memory_mb_max

    def to_summary_dict(self) -> dict[str, Any]:
        """Convert to summary dictionary for reporting."""
        return {
            "query_id": self.query_id,
            "engine": self.engine.value,
            "status": self.status.value,
            "row_count": self.row_count,
            "execution_time_ms": self.timing.avg_time_ms,
            "memory_mb": self.resources.memory_mb_max,
            "validated": self.validated,
            "matches_expected": self.matches_expected,
        }


class BatchResult(BaseModel):
    """Results from executing multiple queries."""
    results: list[QueryResult] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    dataset_profile: str = ""

    @computed_field
    @property
    def total_queries(self) -> int:
        """Total number of queries executed."""
        return len(self.results)

    @computed_field
    @property
    def successful_queries(self) -> int:
        """Number of successful queries."""
        return sum(1 for r in self.results if r.is_success)

    @computed_field
    @property
    def failed_queries(self) -> int:
        """Number of failed queries."""
        return sum(1 for r in self.results if r.status == ExecutionStatus.FAILED)

    @computed_field
    @property
    def skipped_queries(self) -> int:
        """Number of skipped queries."""
        return sum(1 for r in self.results if r.status in (ExecutionStatus.SKIPPED, ExecutionStatus.IMPOSSIBLE))

    @computed_field
    @property
    def total_time_ms(self) -> float:
        """Total execution time."""
        return sum(r.timing.execution_time_ms for r in self.results)

    def get_result(self, query_id: str, engine: Optional[EngineType] = None) -> Optional[QueryResult]:
        """Get result for a specific query."""
        for r in self.results:
            if r.query_id == query_id:
                if engine is None or r.engine == engine:
                    return r
        return None

    def get_results_by_engine(self, engine: EngineType) -> list[QueryResult]:
        """Get all results for a specific engine."""
        return [r for r in self.results if r.engine == engine]

    def get_results_by_status(self, status: ExecutionStatus) -> list[QueryResult]:
        """Get all results with a specific status."""
        return [r for r in self.results if r.status == status]

    def to_dataframe_dict(self) -> list[dict[str, Any]]:
        """Convert to list of dicts suitable for DataFrame creation."""
        return [r.to_summary_dict() for r in self.results]


class DryRunResult(BaseModel):
    """Result from dry-run validation (no database execution)."""
    query_id: str
    query_name: str
    engine: EngineType
    can_execute: bool
    paradigm_status: ParadigmStatus

    # Validation results
    query_parsed: bool = False
    parameters_valid: bool = False
    schema_valid: bool = False

    # Issues found
    issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    # Query preview
    query_preview: Optional[str] = None

    @computed_field
    @property
    def is_valid(self) -> bool:
        """Check if dry-run validation passed."""
        return (
            self.can_execute and
            self.query_parsed and
            self.parameters_valid and
            len(self.issues) == 0
        )


class DryRunBatch(BaseModel):
    """Results from dry-run validation of multiple queries."""
    results: list[DryRunResult] = Field(default_factory=list)
    catalog_version: str = ""
    validated_at: datetime = Field(default_factory=datetime.now)

    @computed_field
    @property
    def total_queries(self) -> int:
        """Total number of queries validated."""
        return len(self.results)

    @computed_field
    @property
    def valid_queries(self) -> int:
        """Number of valid queries."""
        return sum(1 for r in self.results if r.is_valid)

    @computed_field
    @property
    def executable_queries(self) -> int:
        """Number of executable queries (can_execute=True)."""
        return sum(1 for r in self.results if r.can_execute)

    def get_by_engine(self, engine: EngineType) -> list[DryRunResult]:
        """Get results for a specific engine."""
        return [r for r in self.results if r.engine == engine]

    def get_paradigm_matrix(self) -> dict[str, dict[str, str]]:
        """Get paradigm support matrix."""
        matrix: dict[str, dict[str, str]] = {}
        for r in self.results:
            if r.query_id not in matrix:
                matrix[r.query_id] = {}
            status_icon = "OK" if r.can_execute else "X"
            if r.issues:
                status_icon = "W"
            matrix[r.query_id][r.engine.value] = status_icon
        return matrix
