"""Workload executor with multi-threading support."""

import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from threading import Lock
from typing import Callable, Dict, List, Optional, Tuple

from .config import WorkloadConfig, ExecutionMode, QuerySpec, MetricsStrategy
from .selector import create_selector
from ..metrics import create_collector, QueryMetrics, MetricsCollector, Metrics


@dataclass
class LatencyStats:
    """Latency statistics with percentiles."""
    min_ms: float = 0.0
    max_ms: float = 0.0
    avg_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0

    @classmethod
    def from_latencies(cls, latencies: List[float]) -> "LatencyStats":
        """Compute stats from list of latencies.

        Uses statistics.quantiles if available (Python 3.8+),
        otherwise falls back to index-based calculation.
        """
        if not latencies:
            return cls()

        sorted_lat = sorted(latencies)
        n = len(sorted_lat)

        # Try to use statistics.quantiles (Python 3.8+)
        try:
            quantiles = statistics.quantiles(sorted_lat, n=100)
            p50 = quantiles[49] if len(quantiles) > 49 else sorted_lat[n // 2]
            p95 = quantiles[94] if len(quantiles) > 94 else sorted_lat[int(n * 0.95)]
            p99 = quantiles[98] if len(quantiles) > 98 else sorted_lat[-1]
        except (AttributeError, statistics.StatisticsError):
            # Fallback to index-based calculation
            p50 = sorted_lat[n // 2]
            p95 = sorted_lat[int(n * 0.95)] if n >= 20 else sorted_lat[-1]
            p99 = sorted_lat[int(n * 0.99)] if n >= 100 else sorted_lat[-1]

        return cls(
            min_ms=sorted_lat[0],
            max_ms=sorted_lat[-1],
            avg_ms=statistics.mean(sorted_lat),
            p50_ms=p50,
            p95_ms=p95,
            p99_ms=p99,
        )


@dataclass
class WorkloadResult:
    """Results from workload execution."""
    workload_name: str
    total_queries: int
    total_duration_s: float
    throughput_qps: float
    peak_memory_mb: float
    latency_stats: LatencyStats = field(default_factory=LatencyStats)
    latency_by_query: Dict[str, LatencyStats] = field(default_factory=dict)
    queries_by_category: Dict[str, int] = field(default_factory=dict)
    query_metrics: List[QueryMetrics] = field(default_factory=list)
    errors: int = 0
    strategy_stats: Dict = field(default_factory=dict)


# Type alias for query executor function
# Returns (row_count, latency_ms, error) or just row_count
QueryExecutorFn = Callable[[str], Tuple[int, float, Optional[str]]]


class WorkloadExecutor:
    """Execute workload with configurable strategy and concurrency.

    Usage:
        config = WorkloadConfig.load("config/workloads/bos_operational.yaml")
        executor = WorkloadExecutor(
            config=config,
            query_executor=lambda qid: (engine.execute_query(qid)[0], 0, None),
            containers=["timescaledb"],
            all_queries=["Q1", "Q2", ..., "Q13"],
        )
        result = executor.run()
    """

    def __init__(
        self,
        config: WorkloadConfig,
        query_executor: QueryExecutorFn,
        containers: List[str],
        all_queries: List[str],
        progress_callback: Optional[Callable[[int, float, str], None]] = None,
    ):
        """Initialize executor.

        Args:
            config: Workload configuration
            query_executor: Function to execute a query, returns (row_count, latency_ms, error)
            containers: Container names without btb_ prefix
            all_queries: List of all available query IDs
            progress_callback: Optional fn(query_count, elapsed_s, last_query_id) for live feedback
        """
        self.config = config
        self.query_executor = query_executor
        self.containers = containers
        self.progress_callback = progress_callback

        # Expand queries (handle ALL)
        self.queries = config.expand_queries(all_queries)

        # Create selector and collector
        self.selector = create_selector(
            config.selection.strategy,
            self.queries,
            config.selection.seed,
        )
        self.collector = create_collector(
            config.metrics.strategy.value,
            containers,
        )

        # Thread safety
        self._lock = Lock()
        self._stop_flag = False
        self._query_count = 0
        self._start_time = 0.0

    def run(self) -> WorkloadResult:
        """Execute the workload.

        Returns:
            WorkloadResult with all metrics
        """
        self._start_time = time.time()
        self._query_count = 0

        # Signal workload start to collector
        self.collector.on_workload_start()

        # Run warmup if configured
        if self.config.execution.warmup_iterations > 0:
            self._run_warmup()

        # Execute based on mode
        mode = self.config.execution.mode
        if mode == ExecutionMode.DURATION:
            self._run_duration_mode()
        elif mode == ExecutionMode.ITERATIONS:
            self._run_iterations_mode()
        else:  # SEQUENTIAL
            self._run_sequential_mode()

        # Signal workload end
        strategy_stats = self.collector.on_workload_end()

        end_time = time.time()
        duration = end_time - self._start_time

        # Compute results
        results = self.collector.get_results()
        categories: Dict[str, int] = {}
        errors = 0
        peak_max = 0.0
        all_latencies: List[float] = []
        latencies_by_query: Dict[str, List[float]] = {}

        for r in results:
            # Collect latencies
            all_latencies.append(r.latency_ms)
            if r.query_id not in latencies_by_query:
                latencies_by_query[r.query_id] = []
            latencies_by_query[r.query_id].append(r.latency_ms)

            # Find category for this query
            for q in self.queries:
                if q.id == r.query_id:
                    cat = q.category
                    categories[cat] = categories.get(cat, 0) + 1
                    break

            if r.status == "error":
                errors += 1
            if r.peak_memory_mb > peak_max:
                peak_max = r.peak_memory_mb

        # Compute latency stats
        latency_stats = LatencyStats.from_latencies(all_latencies)
        latency_by_query = {
            qid: LatencyStats.from_latencies(lats)
            for qid, lats in latencies_by_query.items()
        }

        return WorkloadResult(
            workload_name=self.config.name,
            total_queries=len(results),
            total_duration_s=duration,
            throughput_qps=len(results) / duration if duration > 0 else 0,
            peak_memory_mb=peak_max,
            latency_stats=latency_stats,
            latency_by_query=latency_by_query,
            queries_by_category=categories,
            query_metrics=results,
            errors=errors,
            strategy_stats=strategy_stats,
        )

    def _run_warmup(self) -> None:
        """Run warmup iterations (no metrics collection)."""
        for _ in range(self.config.execution.warmup_iterations):
            query = self.selector.next()
            try:
                self.query_executor(query.id)
            except Exception:
                pass

        # Reset peak RAM after warmup (important!)
        # Otherwise warmup peak pollutes measurements
        for container in self.collector.containers:
            m = Metrics.capture(container)
            m.reset_peak()

        self.selector.reset()

    def _run_sequential_mode(self) -> None:
        """Execute each query N times in order."""
        n = self.config.execution.iterations_per_query
        concurrency = self.config.execution.concurrency

        if concurrency > 1:
            self._run_concurrent(self._sequential_tasks(n), concurrency)
        else:
            for query in self.queries:
                for _ in range(n):
                    self._execute_one(query)

    def _run_iterations_mode(self) -> None:
        """Execute N total queries using selector."""
        n = self.config.execution.iterations
        concurrency = self.config.execution.concurrency

        if concurrency > 1:
            self._run_concurrent(self._iteration_tasks(n), concurrency)
        else:
            for _ in range(n):
                query = self.selector.next()
                self._execute_one(query)

    def _run_duration_mode(self) -> None:
        """Execute queries for N seconds."""
        duration = self.config.execution.duration_seconds
        concurrency = self.config.execution.concurrency
        end_time = time.time() + duration

        if concurrency > 1:
            self._run_concurrent_duration(end_time, concurrency)
        else:
            while time.time() < end_time:
                query = self.selector.next()
                self._execute_one(query)

    def _execute_one(self, query: QuerySpec) -> Optional[QueryMetrics]:
        """Execute a single query with metrics collection."""
        self.collector.before_query(query.id)

        start = time.time()
        error = None
        row_count = 0

        try:
            result = self.query_executor(query.id)
            if isinstance(result, tuple) and len(result) >= 2:
                row_count = result[0]
                # latency_ms might be in result[1], but we measure ourselves
            elif isinstance(result, int):
                row_count = result
        except Exception as e:
            error = str(e)

        latency_ms = (time.time() - start) * 1000

        # Update counter and notify progress
        with self._lock:
            self._query_count += 1
            if self.progress_callback:
                elapsed = time.time() - self._start_time
                self.progress_callback(self._query_count, elapsed, query.id)

        return self.collector.after_query(query.id, latency_ms, row_count, error)

    def _sequential_tasks(self, n: int):
        """Generator for sequential mode tasks."""
        for query in self.queries:
            for _ in range(n):
                yield query

    def _iteration_tasks(self, n: int):
        """Generator for iteration mode tasks."""
        for _ in range(n):
            yield self.selector.next()

    def _run_concurrent(self, tasks, concurrency: int) -> None:
        """Run tasks with thread pool."""
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for query in tasks:
                futures.append(executor.submit(self._execute_one_threadsafe, query))

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass

    def _run_concurrent_duration(self, end_time: float, concurrency: int) -> None:
        """Run concurrent queries until end_time."""
        self._stop_flag = False

        def worker():
            while not self._stop_flag and time.time() < end_time:
                with self._lock:
                    query = self.selector.next()
                self._execute_one_threadsafe(query)

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(worker) for _ in range(concurrency)]

            # Wait for end time
            while time.time() < end_time:
                time.sleep(0.1)

            self._stop_flag = True

            for future in futures:
                try:
                    future.result(timeout=5)
                except Exception:
                    pass

    def _execute_one_threadsafe(self, query: QuerySpec) -> Optional[QueryMetrics]:
        """Thread-safe query execution."""
        with self._lock:
            self.collector.before_query(query.id)

        start = time.time()
        error = None
        row_count = 0

        try:
            result = self.query_executor(query.id)
            if isinstance(result, tuple) and len(result) >= 2:
                row_count = result[0]
            elif isinstance(result, int):
                row_count = result
        except Exception as e:
            error = str(e)

        latency_ms = (time.time() - start) * 1000

        with self._lock:
            return self.collector.after_query(query.id, latency_ms, row_count, error)
