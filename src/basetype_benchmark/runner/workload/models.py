"""Workload scenario models for stress testing.

Defines dataclasses for workload scenarios that simulate realistic
middleware usage patterns (dashboard refresh, IoT ingestion, etc.).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkloadProfile(Enum):
    """Workload profile types based on read/write ratio."""

    READ_HEAVY = "read_heavy"  # 90% reads, 10% writes
    WRITE_HEAVY = "write_heavy"  # 20% reads, 80% writes
    MIXED = "mixed"  # 50% reads, 50% writes
    ANALYTICS = "analytics"  # 100% reads, complex queries
    INGESTION = "ingestion"  # 100% writes, timeseries append
    GRAPH_STRESS = "graph_stress"  # Graph traversal intensive
    TIMESERIES_STRESS = "timeseries_stress"  # TS aggregation intensive


@dataclass
class QueryStep:
    """Single step in a workload sequence."""

    query_id: str  # Q1, Q6, QW1, etc.
    repeat: int = 1  # Number of times to execute
    think_time_ms: int = 0  # Pause after execution (simulates user think time)
    batch_size: int | None = None  # For write queries (QW1)
    concurrent: bool = False  # Run in parallel with next step (future)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        d = {
            "query_id": self.query_id,
            "repeat": self.repeat,
        }
        if self.think_time_ms > 0:
            d["think_time_ms"] = self.think_time_ms
        if self.batch_size is not None:
            d["batch_size"] = self.batch_size
        if self.concurrent:
            d["concurrent"] = self.concurrent
        return d


@dataclass
class WorkloadScenario:
    """Complete workload scenario definition."""

    name: str
    description: str
    profile: WorkloadProfile
    paradigms: list[str]  # Which paradigms to test
    sequence: list[QueryStep]  # Query sequence

    # Duration control
    duration_seconds: int | None = None  # Max duration (None = run sequence once)
    loop: bool = False  # Repeat sequence until duration

    # Metrics to collect
    collect_throughput: bool = True
    collect_latency_distribution: bool = True
    collect_error_rate: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "profile": self.profile.value,
            "paradigms": self.paradigms,
            "sequence": [s.to_dict() for s in self.sequence],
            "duration_seconds": self.duration_seconds,
            "loop": self.loop,
            "metrics": {
                "throughput": self.collect_throughput,
                "latency_distribution": self.collect_latency_distribution,
                "error_rate": self.collect_error_rate,
            },
        }


@dataclass
class QueryStats:
    """Statistics for a single query type within a workload."""

    query_id: str
    executions: int = 0
    successes: int = 0
    failures: int = 0

    # Latency stats (milliseconds)
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    latency_avg_ms: float = 0.0
    latency_min_ms: float = 0.0
    latency_max_ms: float = 0.0

    # Memory stats (MB) - compiled from per-query measurements
    memory_peak_avg_mb: float = 0.0  # Average peak across executions
    memory_peak_max_mb: float = 0.0  # Maximum peak observed
    memory_peak_total_mb: float = 0.0  # Sum = resource impact

    # Raw data for percentile calculation
    _latencies_ms: list[float] = field(default_factory=list, repr=False)
    _memory_peaks_mb: list[float] = field(default_factory=list, repr=False)

    def add_execution(
        self,
        duration_ms: float,
        success: bool,
        memory_peak_mb: float = 0.0,
    ) -> None:
        """Record a query execution."""
        self.executions += 1
        if success:
            self.successes += 1
            self._latencies_ms.append(duration_ms)
            if memory_peak_mb > 0:
                self._memory_peaks_mb.append(memory_peak_mb)
        else:
            self.failures += 1

    def compute_stats(self) -> None:
        """Compute percentiles and averages from raw data."""
        if self._latencies_ms:
            sorted_lat = sorted(self._latencies_ms)
            n = len(sorted_lat)
            self.latency_min_ms = sorted_lat[0]
            self.latency_max_ms = sorted_lat[-1]
            self.latency_avg_ms = sum(sorted_lat) / n
            self.latency_p50_ms = sorted_lat[int(n * 0.50)]
            self.latency_p95_ms = sorted_lat[int(n * 0.95)] if n > 1 else sorted_lat[-1]
            self.latency_p99_ms = sorted_lat[int(n * 0.99)] if n > 1 else sorted_lat[-1]

        if self._memory_peaks_mb:
            self.memory_peak_avg_mb = sum(self._memory_peaks_mb) / len(self._memory_peaks_mb)
            self.memory_peak_max_mb = max(self._memory_peaks_mb)
            self.memory_peak_total_mb = sum(self._memory_peaks_mb)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "query_id": self.query_id,
            "executions": self.executions,
            "successes": self.successes,
            "failures": self.failures,
            "latency": {
                "p50_ms": round(self.latency_p50_ms, 2),
                "p95_ms": round(self.latency_p95_ms, 2),
                "p99_ms": round(self.latency_p99_ms, 2),
                "avg_ms": round(self.latency_avg_ms, 2),
                "min_ms": round(self.latency_min_ms, 2),
                "max_ms": round(self.latency_max_ms, 2),
            },
            "memory": {
                "peak_avg_mb": round(self.memory_peak_avg_mb, 2),
                "peak_max_mb": round(self.memory_peak_max_mb, 2),
                "peak_total_mb": round(self.memory_peak_total_mb, 2),
            },
        }


@dataclass
class WorkloadResult:
    """Results from workload execution."""

    scenario_name: str
    paradigm: str

    # Throughput
    total_queries: int = 0
    total_duration_seconds: float = 0.0
    qps: float = 0.0  # Queries per second

    # Latency distribution (global across all queries)
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    latency_avg_ms: float = 0.0
    latency_max_ms: float = 0.0

    # Errors
    total_errors: int = 0
    error_rate: float = 0.0

    # Memory
    scenario_memory_peak_mb: float = 0.0  # Global peak during scenario
    query_memory_breakdown: dict[str, float] = field(default_factory=dict)

    # Per-query breakdown
    query_stats: dict[str, QueryStats] = field(default_factory=dict)

    # Metadata
    start_time: str = ""
    end_time: str = ""
    ram_limit_mb: int | None = None

    def compute_global_stats(self) -> None:
        """Compute global latency stats from per-query stats."""
        all_latencies: list[float] = []
        for stats in self.query_stats.values():
            all_latencies.extend(stats._latencies_ms)

        if all_latencies:
            sorted_lat = sorted(all_latencies)
            n = len(sorted_lat)
            self.latency_avg_ms = sum(sorted_lat) / n
            self.latency_max_ms = sorted_lat[-1]
            self.latency_p50_ms = sorted_lat[int(n * 0.50)]
            self.latency_p95_ms = sorted_lat[int(n * 0.95)] if n > 1 else sorted_lat[-1]
            self.latency_p99_ms = sorted_lat[int(n * 0.99)] if n > 1 else sorted_lat[-1]

        # Compute memory breakdown
        for query_id, stats in self.query_stats.items():
            self.query_memory_breakdown[query_id] = stats.memory_peak_total_mb

        # Compute totals
        self.total_queries = sum(s.executions for s in self.query_stats.values())
        self.total_errors = sum(s.failures for s in self.query_stats.values())
        if self.total_queries > 0:
            self.error_rate = self.total_errors / self.total_queries
        if self.total_duration_seconds > 0:
            self.qps = self.total_queries / self.total_duration_seconds

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "scenario_name": self.scenario_name,
            "paradigm": self.paradigm,
            "throughput": {
                "total_queries": self.total_queries,
                "duration_seconds": round(self.total_duration_seconds, 2),
                "qps": round(self.qps, 2),
            },
            "latency": {
                "p50_ms": round(self.latency_p50_ms, 2),
                "p95_ms": round(self.latency_p95_ms, 2),
                "p99_ms": round(self.latency_p99_ms, 2),
                "avg_ms": round(self.latency_avg_ms, 2),
                "max_ms": round(self.latency_max_ms, 2),
            },
            "errors": {
                "total": self.total_errors,
                "rate": round(self.error_rate, 4),
            },
            "memory": {
                "scenario_peak_mb": round(self.scenario_memory_peak_mb, 2),
                "query_breakdown": {
                    k: round(v, 2) for k, v in self.query_memory_breakdown.items()
                },
            },
            "query_stats": {
                query_id: stats.to_dict()
                for query_id, stats in self.query_stats.items()
            },
            "metadata": {
                "start_time": self.start_time,
                "end_time": self.end_time,
                "ram_limit_mb": self.ram_limit_mb,
            },
        }


@dataclass
class WorkloadResults:
    """Collection of results across multiple paradigms."""

    scenario: WorkloadScenario
    results: dict[str, WorkloadResult] = field(default_factory=dict)  # paradigm -> result

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "scenario": self.scenario.to_dict(),
            "results": {
                paradigm: result.to_dict()
                for paradigm, result in self.results.items()
            },
        }

    def to_json(self, path: str) -> None:
        """Export results to JSON file."""
        import json
        from pathlib import Path

        Path(path).write_text(json.dumps(self.to_dict(), indent=2))
