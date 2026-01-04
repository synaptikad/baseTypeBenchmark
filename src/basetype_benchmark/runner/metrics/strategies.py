"""Metrics collection strategies for different workload types.

Two strategies:
- PerQueryCollector: Reset peak before each query (debug/isolation mode)
- AggregateCollector: Reset only after load (realistic stress test)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .snapshot import Metrics


@dataclass
class QueryMetrics:
    """Metrics result for a single query execution."""
    query_id: str
    latency_ms: float
    row_count: int
    memory_mb: float
    peak_memory_mb: float
    status: str = "ok"
    error: Optional[str] = None


class MetricsCollector(ABC):
    """Abstract interface for metrics collection.

    Implementations define when/how memory peak is reset.
    """

    def __init__(self, containers: List[str]):
        """Initialize collector.

        Args:
            containers: Container names WITHOUT btb_ prefix (e.g., ["timescaledb"])
                       For M2/O2: ["memgraph", "timescaledb"] or ["oxigraph", "timescaledb"]
        """
        # Accepte les deux formats : "timescaledb" ou "btb_timescaledb"
        self.containers = [c if c.startswith("btb_") else f"btb_{c}" for c in containers]
        self._results: List[QueryMetrics] = []
        self._per_container_peak: Dict[str, float] = {}

    def _capture_all(self) -> Tuple[float, float, Dict[str, Dict[str, float]]]:
        """Capture metrics from all containers.

        Returns:
            (total_memory_mb, total_peak_mb, per_container_dict)
            per_container_dict format: {"btb_memgraph": {"memory_mb": 512.3, "peak_mb": 600.1}, ...}
        """
        total_mem = 0.0
        total_peak = 0.0
        per_container: Dict[str, Dict[str, float]] = {}

        for container in self.containers:
            m = Metrics.capture(container)
            total_mem += m.memory_mb
            total_peak += m.memory_peak_mb
            per_container[container] = {
                "memory_mb": m.memory_mb,
                "peak_mb": m.memory_peak_mb,
            }
            # Track max peak per container
            if container not in self._per_container_peak:
                self._per_container_peak[container] = 0.0
            self._per_container_peak[container] = max(
                self._per_container_peak[container],
                m.memory_peak_mb
            )

        return total_mem, total_peak, per_container

    @abstractmethod
    def on_workload_start(self) -> None:
        """Called at workload start (after data load)."""
        pass

    @abstractmethod
    def before_query(self, query_id: str) -> None:
        """Called before each query execution."""
        pass

    @abstractmethod
    def after_query(
        self,
        query_id: str,
        latency_ms: float,
        row_count: int,
        error: Optional[str] = None
    ) -> QueryMetrics:
        """Called after each query. Returns metrics for this query."""
        pass

    @abstractmethod
    def on_workload_end(self) -> Dict:
        """Called at workload end. Returns aggregated stats."""
        pass

    def get_results(self) -> List[QueryMetrics]:
        """Get all collected query metrics."""
        return self._results

    def get_per_container_peak(self) -> Dict[str, float]:
        """Get max peak memory per container (for multi-container scenarios)."""
        return self._per_container_peak.copy()


class PerQueryCollector(MetricsCollector):
    """Reset peak before each query (debug/isolation mode).

    Use this strategy when you need to measure memory impact
    of each query in isolation.
    """

    def on_workload_start(self) -> None:
        # Initial reset
        for container in self.containers:
            m = Metrics.capture(container)
            m.reset_peak()

    def before_query(self, query_id: str) -> None:
        # Reset peak for isolated measurement
        for container in self.containers:
            m = Metrics.capture(container)
            m.reset_peak()

    def after_query(
        self,
        query_id: str,
        latency_ms: float,
        row_count: int,
        error: Optional[str] = None
    ) -> QueryMetrics:
        # Capture peak (isolated to this query) using _capture_all for multi-container
        total_mem, total_peak, _ = self._capture_all()

        qm = QueryMetrics(
            query_id=query_id,
            latency_ms=latency_ms,
            row_count=row_count,
            memory_mb=total_mem,
            peak_memory_mb=total_peak,
            status="error" if error else "ok",
            error=error,
        )
        self._results.append(qm)
        return qm

    def on_workload_end(self) -> Dict:
        return {
            "strategy": "per_query",
            "total_queries": len(self._results),
            "peak_max_mb": max(r.peak_memory_mb for r in self._results) if self._results else 0,
            "per_container_peak": self._per_container_peak,
        }


class AggregateCollector(MetricsCollector):
    """No reset between queries (realistic stress mode).

    Use this strategy for stress testing where you want to see
    cumulative memory behavior under sustained load.
    """

    def __init__(self, containers: List[str]):
        super().__init__(containers)
        self._baseline_peak = 0.0

    def on_workload_start(self) -> None:
        # Reset only once after load
        for container in self.containers:
            m = Metrics.capture(container)
            m.reset_peak()
        _, self._baseline_peak, _ = self._capture_all()

    def before_query(self, query_id: str) -> None:
        # NO reset - accumulate
        pass

    def after_query(
        self,
        query_id: str,
        latency_ms: float,
        row_count: int,
        error: Optional[str] = None
    ) -> QueryMetrics:
        # Capture cumulative peak using _capture_all for multi-container
        total_mem, total_peak, _ = self._capture_all()

        qm = QueryMetrics(
            query_id=query_id,
            latency_ms=latency_ms,
            row_count=row_count,
            memory_mb=total_mem,
            peak_memory_mb=total_peak,  # Cumulative since load
            status="error" if error else "ok",
            error=error,
        )
        self._results.append(qm)
        return qm

    def on_workload_end(self) -> Dict:
        _, final_peak, _ = self._capture_all()
        return {
            "strategy": "aggregate",
            "total_queries": len(self._results),
            "baseline_peak_mb": self._baseline_peak,
            "final_peak_mb": final_peak,
            "peak_growth_mb": final_peak - self._baseline_peak,
            "per_container_peak": self._per_container_peak,
        }


def create_collector(strategy: str, containers: List[str]) -> MetricsCollector:
    """Factory to create appropriate collector.

    Args:
        strategy: "per_query" or "aggregate"
        containers: Container names without btb_ prefix

    Returns:
        MetricsCollector instance
    """
    if strategy == "aggregate":
        return AggregateCollector(containers)
    return PerQueryCollector(containers)
