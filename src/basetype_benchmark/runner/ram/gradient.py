"""RAM gradient executor for benchmark testing.

Sprint 3 - Benchmark BaseType V3

Implements the RAM-Gradient protocol from papier.md Section 3.4:
- Test with decreasing RAM levels (128, 64, 32, 16, 8 GB)
- Detect OOM early and stop gradient
- Measure actual memory usage via cgroups v2
- Drop caches between levels for isolation

This is a key methodological contribution: RAM as independent variable.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal

logger = logging.getLogger(__name__)

from rich.console import Console

from ..config import EngineType, QueryCategory
from ..core.catalog import QueryCatalog
from ..monitoring import (
    MetricsSampler,
    MultiContainerSampler,
    SamplingResult,
    DockerClient,
)
from ..runners import (
    RunResult,
    RunStatus,
    get_runner,
    get_hybrid_runner,
)
from .isolation import IsolationManager, get_paradigm_containers


class GradientError(Exception):
    """Raised when gradient execution fails."""
    pass


@dataclass
class QueryRunResult:
    """Result of a single query run."""
    query_id: str
    variant_id: int
    run_id: int
    result: RunResult
    sampling: SamplingResult | None = None

    @property
    def latency_ms(self) -> float:
        return self.result.duration_ms

    @property
    def status(self) -> RunStatus:
        return self.result.status

    @property
    def memory_peak_mb(self) -> float:
        if self.sampling:
            return self.sampling.memory_peak_mb
        return 0.0


@dataclass
class QueryStats:
    """Statistics for a query across runs."""
    query_id: str
    runs: list[QueryRunResult] = field(default_factory=list)

    @property
    def latencies_ms(self) -> list[float]:
        return [r.latency_ms for r in self.runs if r.status == RunStatus.SUCCESS]

    # Validation data properties (from first successful run)
    @property
    def row_count(self) -> int:
        """Total row count from first successful run."""
        for r in self.runs:
            if r.status == RunStatus.SUCCESS:
                return r.result.row_count
        return 0

    @property
    def sample_rows(self) -> list[dict] | None:
        """First N rows from first successful run (for cross-paradigm comparison)."""
        for r in self.runs:
            if r.status == RunStatus.SUCCESS and r.result.rows:
                # Return first 100 rows for comparison
                return r.result.rows[:100]
        return None

    @property
    def all_rows(self) -> list[dict] | None:
        """All rows from first successful run (for archiving)."""
        for r in self.runs:
            if r.status == RunStatus.SUCCESS and r.result.rows:
                return r.result.rows
        return None

    @property
    def row_hash(self) -> str | None:
        """SHA256 hash of full result for integrity verification."""
        import hashlib
        import json
        for r in self.runs:
            if r.status == RunStatus.SUCCESS and r.result.rows:
                # Hash the full result for integrity checking
                rows_json = json.dumps(r.result.rows, sort_keys=True, default=str)
                return hashlib.sha256(rows_json.encode()).hexdigest()
        return None

    @property
    def column_names(self) -> list[str] | None:
        """Column names from first successful run."""
        for r in self.runs:
            if r.status == RunStatus.SUCCESS and r.result.rows:
                return list(r.result.rows[0].keys()) if r.result.rows else None
        return None

    @property
    def p50_ms(self) -> float:
        latencies = sorted(self.latencies_ms)
        if not latencies:
            return 0.0
        idx = len(latencies) // 2
        return latencies[idx]

    @property
    def p95_ms(self) -> float:
        latencies = sorted(self.latencies_ms)
        if not latencies:
            return 0.0
        idx = int(len(latencies) * 0.95)
        return latencies[min(idx, len(latencies) - 1)]

    @property
    def avg_ms(self) -> float:
        latencies = self.latencies_ms
        if not latencies:
            return 0.0
        return sum(latencies) / len(latencies)

    @property
    def min_ms(self) -> float:
        latencies = self.latencies_ms
        return min(latencies) if latencies else 0.0

    @property
    def max_ms(self) -> float:
        latencies = self.latencies_ms
        return max(latencies) if latencies else 0.0

    @property
    def stddev_ms(self) -> float:
        latencies = self.latencies_ms
        if len(latencies) < 2:
            return 0.0
        avg = self.avg_ms
        variance = sum((x - avg) ** 2 for x in latencies) / len(latencies)
        return variance ** 0.5

    @property
    def success_rate(self) -> float:
        if not self.runs:
            return 0.0
        successes = sum(1 for r in self.runs if r.status == RunStatus.SUCCESS)
        return successes / len(self.runs)

    @property
    def memory_peak_mb(self) -> float:
        peaks = [r.memory_peak_mb for r in self.runs if r.memory_peak_mb > 0]
        return max(peaks) if peaks else 0.0


GradientStatus = Literal["success", "oom", "timeout", "error"]


@dataclass
class GradientLevel:
    """Results for a single RAM level."""
    limit_mb: int
    status: GradientStatus
    actual_peak_mb: float = 0.0
    query_stats: dict[str, QueryStats] = field(default_factory=dict)
    duration_seconds: float = 0.0
    error_message: str | None = None

    @property
    def is_success(self) -> bool:
        return self.status == "success"

    @property
    def total_latency_ms(self) -> float:
        """Sum of avg latencies across all queries (for plateau detection)."""
        return sum(stats.avg_ms for stats in self.query_stats.values())

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "limit_mb": self.limit_mb,
            "status": self.status,
            "actual_peak_mb": self.actual_peak_mb,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "queries": {
                qid: {
                    "p50_ms": stats.p50_ms,
                    "p95_ms": stats.p95_ms,
                    "avg_ms": stats.avg_ms,
                    "min_ms": stats.min_ms,
                    "max_ms": stats.max_ms,
                    "stddev_ms": stats.stddev_ms,
                    "success_rate": stats.success_rate,
                    "memory_peak_mb": stats.memory_peak_mb,
                    "run_count": len(stats.runs),
                }
                for qid, stats in self.query_stats.items()
            },
        }


@dataclass
class GradientResult:
    """Complete gradient result for a paradigm."""
    paradigm: str
    levels: list[GradientLevel] = field(default_factory=list)
    baseline_peak_mb: float = 0.0

    @property
    def ram_viable_mb(self) -> int | None:
        """Smallest RAM level without OOM."""
        successful = [l for l in self.levels if l.is_success]
        if not successful:
            return None
        return min(l.limit_mb for l in successful)

    @property
    def ram_plateau_mb(self) -> int | None:
        """RAM level where performance plateaued (last successful level tested).

        In ascending gradient (4GB → 8GB → 16GB → ...), this is the highest
        RAM level tested before stopping due to plateau detection.
        """
        successful = [l for l in self.levels if l.is_success]
        if not successful:
            return None
        return max(l.limit_mb for l in successful)

    @property
    def all_oom(self) -> bool:
        """Check if all levels resulted in OOM."""
        return all(l.status == "oom" for l in self.levels)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "paradigm": self.paradigm,
            "baseline_peak_mb": self.baseline_peak_mb,
            "ram_viable_mb": self.ram_viable_mb,
            "ram_plateau_mb": self.ram_plateau_mb,
            "levels": [l.to_dict() for l in self.levels],
        }


# Progress callback type
ProgressCallback = Callable[[str, int, int], None]


class RAMGradientExecutor:
    """Execute benchmark with decreasing RAM levels.

    Implements the RAM-Gradient protocol:
    1. Start at highest RAM (128 GB)
    2. Run all queries at each level
    3. Decrease RAM and repeat
    4. Stop on OOM (early termination)

    Example:
        ```python
        executor = RAMGradientExecutor(
            paradigm="M1",
            isolation=IsolationManager(...),
            configs={"M1": MemgraphConfig(...)},
        )

        result = executor.run_gradient(
            queries=["Q1", "Q2", "Q3"],
            levels_mb=[131072, 65536, 32768, 16384, 8192],
        )

        print(f"RAM viable: {result.ram_viable_mb} MB")
        ```
    """

    # Default RAM levels (MB) - descending to detect OOM early
    DEFAULT_LEVELS_MB = [131072, 65536, 32768, 16384, 8192]  # 128, 64, 32, 16, 8 GB

    # Execution parameters
    DEFAULT_WARMUP_RUNS = 0  # Warmup disabled by default (middleware benchmark)
    DEFAULT_TIMED_RUNS = 10
    DEFAULT_VARIANTS = 3

    # Plateau detection threshold (ratio of current/previous total latency)
    # If ratio >= threshold, consider it a plateau (less than 5% improvement)
    PLATEAU_THRESHOLD = 0.95

    def __init__(
        self,
        paradigm: str,
        isolation: IsolationManager,
        configs: dict,
        n_warmup: int = DEFAULT_WARMUP_RUNS,
        n_runs: int = DEFAULT_TIMED_RUNS,
        n_variants: int = DEFAULT_VARIANTS,
        timeout_seconds: float = 300.0,
        plateau_threshold: float = PLATEAU_THRESHOLD,
        verbose: bool = True,
    ):
        """Initialize gradient executor.

        Args:
            paradigm: P1, P2, M1, M2, or O2
            isolation: Container isolation manager
            configs: Dict with connection configs by paradigm
            n_warmup: Warmup runs per query (not counted)
            n_runs: Timed runs per query variant
            n_variants: Number of parameter variants per query
            timeout_seconds: Query timeout
            verbose: Show detailed query execution progress
        """
        self.paradigm = paradigm.upper()
        self.isolation = isolation
        self.configs = configs
        self.n_warmup = n_warmup
        self.n_runs = n_runs
        self.n_variants = n_variants
        self.timeout = timeout_seconds
        self.plateau_threshold = plateau_threshold
        self.verbose = verbose

        self._docker = DockerClient()
        self._console = Console()
        self._catalog = QueryCatalog()  # Fix Bug #4: Initialize catalog
        self._data_path: Path | None = None

    def set_data_path(self, data_path: Path) -> None:
        """Set the data directory path for loading queries_params.yaml."""
        self._data_path = Path(data_path)

    def run_gradient(
        self,
        queries: list[str],
        levels_mb: list[int] | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> GradientResult:
        """Execute complete RAM gradient for paradigm.

        Args:
            queries: List of query IDs to run
            levels_mb: RAM levels in MB (descending)
            on_progress: Optional progress callback

        Returns:
            GradientResult with all levels
        """
        # Early warning if data_path not set
        if not self._data_path:
            logger.warning(
                "run_gradient called without data_path set. "
                "Call set_data_path() before run_gradient() for proper parameter loading."
            )

        levels_mb = levels_mb or self.DEFAULT_LEVELS_MB
        result = GradientResult(paradigm=self.paradigm)

        # Ensure containers are running
        if not self.isolation.is_paradigm_running(self.paradigm):
            self.isolation.start_paradigm(self.paradigm)

        # Initialize param sampler early (needed by _measure_baseline)
        if not hasattr(self, "_sampled_params"):
            self._init_param_sampler()

        # Measure baseline (run query without RAM limit, after resetting load peak)
        result.baseline_peak_mb = self._measure_baseline(queries)

        # Run gradient (ascending: low RAM → high RAM, stop at plateau)
        prev_total_latency: float | None = None

        for i, limit_mb in enumerate(levels_mb):
            if on_progress:
                on_progress(f"RAM {limit_mb}MB", i + 1, len(levels_mb))

            # Skip if limit is below baseline (guaranteed OOM)
            if limit_mb < result.baseline_peak_mb * 0.8:
                result.levels.append(GradientLevel(
                    limit_mb=limit_mb,
                    status="oom",
                    error_message="Skipped: limit below baseline",
                ))
                continue

            level_result = self._run_level(limit_mb, queries)
            result.levels.append(level_result)

            # Early termination on OOM
            if level_result.status == "oom":
                break

            # Plateau detection: compare total latency with previous level
            if level_result.is_success and prev_total_latency is not None:
                current_total = level_result.total_latency_ms
                if current_total > 0 and prev_total_latency > 0:
                    ratio = current_total / prev_total_latency
                    improvement_pct = (1 - ratio) * 100

                    if ratio >= self.plateau_threshold:
                        # Plateau detected: less than 5% improvement
                        if self.verbose:
                            self._console.print(
                                f"  [yellow]Plateau detected at {limit_mb}MB "
                                f"({improvement_pct:+.1f}% vs previous)[/yellow]"
                            )
                        break
                    elif self.verbose:
                        self._console.print(
                            f"  [dim]RAM {limit_mb}MB: {improvement_pct:+.1f}% improvement[/dim]"
                        )

            # Update previous total latency for next iteration
            if level_result.is_success:
                prev_total_latency = level_result.total_latency_ms

        return result

    def _run_level(self, limit_mb: int, queries: list[str]) -> GradientLevel:
        """Run all queries at a specific RAM level.

        Args:
            limit_mb: Memory limit in MB
            queries: Query IDs to run

        Returns:
            GradientLevel with results
        """
        start_time = time.perf_counter()

        try:
            # Apply memory limit
            self.isolation.set_memory_limit(self.paradigm, limit_mb)

            # Drop caches for clean state
            self.isolation.drop_caches()

            # Get container IDs for monitoring
            container_ids = self.isolation.get_container_ids(self.paradigm)

            # Setup sampler
            if len(container_ids) == 1:
                container_id = list(container_ids.values())[0]
                sampler = MetricsSampler(container_id)
            else:
                sampler = MultiContainerSampler(container_ids)

            # Initialize dynamic parameter sampler (once per level)
            if not hasattr(self, "_sampled_params"):
                self._init_param_sampler()

            # Run warmup (not counted)
            if self.verbose:
                self._console.print(f"      [dim]Warmup ({self.n_warmup} runs)...[/dim]")
            self._run_warmup(queries)

            # Run timed queries with sampling
            if self.verbose:
                self._console.print(
                    f"      [dim]Running {len(queries)} queries "
                    f"({self.n_variants} variants × {self.n_runs} runs)...[/dim]"
                )
            sampler.start()
            query_stats = self._run_queries(queries, sampler)

            # Fix: MultiContainerSampler.stop() returns dict, use get_combined_result()
            if isinstance(sampler, MultiContainerSampler):
                sampling_result = sampler.get_combined_result()
            else:
                sampling_result = sampler.stop()

            duration = time.perf_counter() - start_time

            # Check for OOM
            if sampling_result.oom_detected:
                return GradientLevel(
                    limit_mb=limit_mb,
                    status="oom",
                    actual_peak_mb=sampling_result.memory_peak_mb,
                    query_stats=query_stats,
                    duration_seconds=duration,
                )

            # Check for query-level OOM
            for stats in query_stats.values():
                if any(r.status == RunStatus.OOM for r in stats.runs):
                    return GradientLevel(
                        limit_mb=limit_mb,
                        status="oom",
                        actual_peak_mb=sampling_result.memory_peak_mb,
                        query_stats=query_stats,
                        duration_seconds=duration,
                    )

            return GradientLevel(
                limit_mb=limit_mb,
                status="success",
                actual_peak_mb=sampling_result.memory_peak_mb,
                query_stats=query_stats,
                duration_seconds=duration,
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return GradientLevel(
                limit_mb=limit_mb,
                status="error",
                duration_seconds=duration,
                error_message=str(e),
            )

    def _run_warmup(self, queries: list[str]) -> None:
        """Run warmup queries (not counted)."""
        runner = self._get_runner()

        for _ in range(self.n_warmup):
            for query_id in queries[:3]:  # Limit warmup queries
                try:
                    # Execute with simple params
                    runner.execute(
                        self._get_query_text(query_id),
                        self._get_default_params(query_id),
                        self.timeout,
                    )
                except Exception:
                    pass

    def _run_queries(
        self,
        queries: list[str],
        sampler: MetricsSampler | MultiContainerSampler,
    ) -> dict[str, QueryStats]:
        """Run all queries with variants and collect stats."""
        runner = self._get_runner()
        stats: dict[str, QueryStats] = {}
        total_queries = len(queries)

        # Get PeakMemoryTrackers for per-query peak measurement
        # These maintain persistent fds for proper per-fd reset semantics
        container_ids = self.isolation.get_container_ids(self.paradigm)
        peak_trackers: dict[str, "PeakMemoryTracker"] = {}
        for name, cid in container_ids.items():
            try:
                from ..monitoring import CgroupsV2Monitor, PeakMemoryTracker
                monitor = CgroupsV2Monitor(cid)
                peak_trackers[name] = PeakMemoryTracker(monitor.cgroup_path)
            except Exception:
                pass

        for q_idx, query_id in enumerate(queries, 1):
            query_stats = QueryStats(query_id=query_id)
            query_start = time.perf_counter()

            if self.verbose:
                self._console.print(
                    f"      [dim]{query_id}[/dim] ({q_idx}/{total_queries}) ",
                    end=""
                )

            # Get query definition and files
            query_def = self._catalog.get_query(query_id)

            # Skip queries marked IMPOSSIBLE for this paradigm
            engine_type = EngineType(self.paradigm)
            if not query_def.can_execute(engine_type):
                if self.verbose:
                    self._console.print("[yellow]SKIPPED (IMPOSSIBLE)[/yellow]")
                # Record as skipped
                query_stats.runs.append(QueryRunResult(
                    query_id=query_id,
                    variant_id=0,
                    run_id=0,
                    result=RunResult(
                        rows=[],
                        duration_ms=0,
                        status=RunStatus.SKIPPED,
                        error_message=f"Query {query_id} is IMPOSSIBLE for {self.paradigm}",
                    ),
                ))
                stats[query_id] = query_stats
                continue

            query_files = self._load_query_files(query_id)

            for variant_id in range(self.n_variants):
                params = self._get_variant_params(query_id, variant_id)

                # Convert params to ordered tuple for P1/P2 (SQL positional binding)
                # Skip for write_workload, jsonb_write, and jsonb_validation which use named placeholders %(name)s
                if self.paradigm in ("P1", "P2") and query_def.category not in (
                    QueryCategory.WRITE_WORKLOAD, QueryCategory.JSONB_WRITE, QueryCategory.JSONB_VALIDATION
                ):
                    from ..core.query_utils import get_ordered_params
                    params = get_ordered_params(params, query_def.parameter_order)

                for run_id in range(self.n_runs):
                    try:
                        # Reset memory peak before each run (per-fd reset)
                        for tracker in peak_trackers.values():
                            tracker.reset()

                        # Execute based on query category
                        if query_def.category == "hybrid" and self.paradigm in ("M2", "O2"):
                            # Hybrid execution: two-phase (graph + timeseries)
                            result = runner.execute_hybrid(
                                query_files["graph_query"],
                                query_files["ts_query"],
                                params,
                                float(self.timeout),
                            )
                        else:
                            # Single-phase execution
                            result = runner.execute(
                                query_files["query"],
                                params,
                                float(self.timeout),
                            )

                        # Capture memory peak after query (via same fd)
                        run_peak_bytes = 0
                        for tracker in peak_trackers.values():
                            run_peak_bytes += tracker.read_peak()

                        # Create sampling result for this run
                        run_sampling = SamplingResult(
                            memory_peak_bytes=run_peak_bytes,
                        ) if run_peak_bytes > 0 else None

                        query_stats.runs.append(QueryRunResult(
                            query_id=query_id,
                            variant_id=variant_id,
                            run_id=run_id,
                            result=result,
                            sampling=run_sampling,
                        ))

                        # Early exit on OOM
                        if result.status == RunStatus.OOM:
                            break

                    except Exception as e:
                        query_stats.runs.append(QueryRunResult(
                            query_id=query_id,
                            variant_id=variant_id,
                            run_id=run_id,
                            result=RunResult(
                                rows=[],
                                duration_ms=0,
                                status=RunStatus.ERROR,
                                error_message=str(e),
                            ),
                        ))

                # Exit variant loop on OOM
                if query_stats.runs and query_stats.runs[-1].status == RunStatus.OOM:
                    break

            stats[query_id] = query_stats
            query_duration = time.perf_counter() - query_start

            # Print query result
            if self.verbose:
                if query_stats.runs:
                    last_status = query_stats.runs[-1].status
                    if last_status == RunStatus.SUCCESS:
                        avg_ms = query_stats.avg_ms
                        self._console.print(
                            f"[green]OK[/green] "
                            f"[dim]avg={avg_ms:.1f}ms rows={query_stats.runs[0].result.row_count}[/dim]"
                        )
                    elif last_status == RunStatus.OOM:
                        self._console.print(f"[red]OOM[/red]")
                    elif last_status == RunStatus.TIMEOUT:
                        self._console.print(f"[yellow]TIMEOUT[/yellow]")
                    else:
                        err = query_stats.runs[-1].result.error_message or "unknown"
                        self._console.print(f"[red]ERROR: {err[:50]}[/red]")
                else:
                    self._console.print(f"[red]NO RUNS[/red]")

            # Exit query loop on OOM
            if query_stats.runs and query_stats.runs[-1].status == RunStatus.OOM:
                break

        # Cleanup peak trackers (close fds)
        for tracker in peak_trackers.values():
            tracker.close()

        return stats

    def _measure_baseline(self, queries: list[str] | None = None) -> float:
        """Measure baseline memory for queries without RAM limit.

        This resets memory.peak after load, then runs a warmup query to measure
        the actual RAM needed for query execution (not the load peak which can
        be much higher due to multi-worker bulk inserts).

        Args:
            queries: Query IDs to use for baseline measurement. Uses first query.

        Returns:
            Peak memory in MB during query execution
        """
        container_ids = self.isolation.get_container_ids(self.paradigm)

        if not container_ids:
            return 0.0

        try:
            from ..monitoring import CgroupsV2Monitor

            # Reset peak for all containers (clears load peak)
            monitors = {}
            for name, container_id in container_ids.items():
                monitor = CgroupsV2Monitor(container_id)
                monitor.reset_memory_peak()
                monitors[name] = monitor

            # Run one warmup query without RAM limit to measure query baseline
            if queries:
                runner = self._get_runner()
                query_id = queries[0]
                query_files = self._load_query_files(query_id)
                if query_files:
                    params = self._get_variant_params(query_id, 0)
                    try:
                        if self.paradigm in ("M2", "O2") and "ts" in query_files:
                            runner.execute_hybrid(
                                query_files["graph"],
                                query_files["ts"],
                                params,
                                timeout=self.timeout,
                            )
                        else:
                            query_text = query_files.get("main") or query_files.get("graph", "")
                            runner.execute(query_text, params, timeout=self.timeout, query_id=query_id)
                    except Exception:
                        pass  # Baseline measurement, ignore errors

            # Get peak after query execution
            total_peak = sum(m.get_memory_peak() for m in monitors.values())
            return total_peak / (1024 * 1024)

        except Exception:
            return 0.0

    def _get_runner(self):
        """Get appropriate runner for paradigm."""
        config = self.configs.get(self.paradigm)
        if config is None:
            raise GradientError(f"No config for paradigm {self.paradigm}")

        # For hybrid, need to get both configs
        if self.paradigm in ("M2", "O2"):
            ts_config = self.configs.get("timescale")
            if ts_config is None:
                raise GradientError("TimescaleDB config required for hybrid paradigm")
            return get_hybrid_runner(self.paradigm, config, ts_config)

        return get_runner(self.paradigm, config)

    def _find_query_file(self, base_dir: Path, query_id: str, ext: str) -> Path | None:
        """Find query file with tolerant naming (Q6 or Q06).

        Args:
            base_dir: Directory to search in
            query_id: Query ID (e.g., "Q6" or "Q06")
            ext: File extension (e.g., "sql", "cypher", "sparql")

        Returns:
            Path to query file, or None if not found
        """
        # Try exact match first
        exact = base_dir / f"{query_id}.{ext}"
        if exact.exists():
            return exact

        # Try zero-padded version (Q6 → Q06)
        if query_id.startswith("Q") and len(query_id) == 2:
            padded = f"Q{query_id[1:].zfill(2)}"
            padded_path = base_dir / f"{padded}.{ext}"
            if padded_path.exists():
                return padded_path

        # Try unpadded version (Q06 → Q6)
        if query_id.startswith("Q") and len(query_id) == 3 and query_id[1:].isdigit():
            unpadded = f"Q{int(query_id[1:])}"
            unpadded_path = base_dir / f"{unpadded}.{ext}"
            if unpadded_path.exists():
                return unpadded_path

        return None

    def _load_query_files(self, query_id: str) -> dict[str, str]:
        """Load query file(s) for execution based on paradigm and category.

        Returns:
            Dictionary with keys:
            - "query": Single query text (for non-hybrid)
            - "graph_query": Graph phase query (for hybrid)
            - "ts_query": Timeseries phase query (for hybrid)
        """
        from ..core.query_utils import strip_query_comments

        query_def = self._catalog.get_query(query_id)
        category = query_def.category
        queries_dir = Path(__file__).parents[4] / "queries"

        # Single-file paradigms: P1, P2, M1
        if self.paradigm in ("P1", "P2", "M1"):
            ext_map = {"P1": "sql", "P2": "sql", "M1": "cypher"}
            ext = ext_map[self.paradigm]

            # Check for write categories - look in write/ subdirectory
            if category in (QueryCategory.WRITE_WORKLOAD, QueryCategory.JSONB_WRITE):
                query_file = self._find_query_file(
                    queries_dir / self.paradigm.lower() / "write",
                    query_id,
                    ext
                )
            else:
                query_file = self._find_query_file(
                    queries_dir / self.paradigm.lower(),
                    query_id,
                    ext
                )

            if query_file is None:
                raise GradientError(f"Query file not found for {query_id} in {self.paradigm}")

            text = query_file.read_text(encoding="utf-8")
            cleaned = strip_query_comments(text, ext)
            return {"query": cleaned}

        # Hybrid paradigms: M2, O2 - route by category
        elif self.paradigm in ("M2", "O2"):
            ext = "cypher" if self.paradigm == "M2" else "sparql"

            if category in (QueryCategory.GRAPH_ONLY, QueryCategory.GRAPH_NATIVE,
                           QueryCategory.JSONB_SPECIFIC, QueryCategory.JSONB_VALIDATION,
                           QueryCategory.SQL_NATIVE):
                # Graph-based queries load from graph/ subdirectory
                query_file = self._find_query_file(
                    queries_dir / self.paradigm.lower() / "graph",
                    query_id,
                    ext
                )

                if query_file is None:
                    raise GradientError(f"Query file not found for {query_id} in {self.paradigm}/graph")

                text = query_file.read_text(encoding="utf-8")
                cleaned = strip_query_comments(text, ext)
                return {"query": cleaned}

            elif category == QueryCategory.TIMESERIES_PURE:
                # Q6: Load from ts/ subdirectory (SQL)
                query_file = self._find_query_file(
                    queries_dir / self.paradigm.lower() / "ts",
                    query_id,
                    "sql"
                )

                if query_file is None:
                    # Graceful fallback
                    self._console.print(
                        f"[yellow]Warning: Query file not found: {query_file}[/yellow]"
                    )
                    return {"query": f"-- Query {query_id} not implemented for {self.paradigm}"}

                text = query_file.read_text(encoding="utf-8")
                cleaned = strip_query_comments(text, "sql")
                return {"query": cleaned}

            elif category == QueryCategory.HYBRID:
                # Q7-Q9, Q12-Q13: Load BOTH graph and ts files
                graph_file = self._find_query_file(
                    queries_dir / self.paradigm.lower() / "graph",
                    query_id,
                    ext
                )
                ts_file = self._find_query_file(
                    queries_dir / self.paradigm.lower() / "ts",
                    query_id,
                    "sql"
                )

                if graph_file is None or ts_file is None:
                    missing = []
                    if graph_file is None:
                        missing.append(f"{query_id}.{ext} in graph/")
                    if ts_file is None:
                        missing.append(f"{query_id}.sql in ts/")
                    raise GradientError(f"Hybrid query files not found: {', '.join(missing)}")

                graph_text = graph_file.read_text(encoding="utf-8")
                ts_text = ts_file.read_text(encoding="utf-8")

                return {
                    "graph_query": strip_query_comments(graph_text, ext),
                    "ts_query": strip_query_comments(ts_text, "sql"),
                }

            elif category in (QueryCategory.WRITE_WORKLOAD, QueryCategory.JSONB_WRITE):
                # Write workloads: look in write/ subdirectory
                # For hybrid paradigms, write queries may be either graph (cypher/sparql) or SQL
                write_dir = queries_dir / self.paradigm.lower() / "write"
                
                # Try graph extension first (cypher/sparql)
                query_file = self._find_query_file(write_dir, query_id, ext)
                actual_ext = ext
                
                # If not found, try SQL (e.g., QW1 writes to TimescaleDB)
                if query_file is None:
                    query_file = self._find_query_file(write_dir, query_id, "sql")
                    actual_ext = "sql"

                if query_file is None:
                    raise GradientError(f"Query file not found for {query_id} in {self.paradigm}/write")

                text = query_file.read_text(encoding="utf-8")
                cleaned = strip_query_comments(text, actual_ext)
                return {"query": cleaned}

            else:
                # Unknown category
                raise GradientError(f"Unknown category '{category}' for {query_id}")

        else:
            raise GradientError(f"Unknown paradigm: {self.paradigm}")

    def _get_query_text(self, query_id: str) -> str:
        """Get query text for execution (backward compatibility).

        DEPRECATED: Use _load_query_files() instead.
        """
        files = self._load_query_files(query_id)
        return files.get("query", "")

    def _get_default_params(self, query_id: str) -> dict[str, Any]:
        """Get default parameters for a query.

        Strategy:
        1. Try dynamic sampling from loaded dataset (if available)
        2. Return empty dict if no sampled params (dataset must provide params)
        """
        from ..core.query_utils import normalize_param_keys

        # Use sampled parameters from dataset
        if hasattr(self, "_sampled_params") and self._sampled_params:
            from ..core.param_sampler import get_params_for_query
            params = get_params_for_query(query_id, self._sampled_params)
            # Note: params can be {} for queries without parameters - that's valid
            if params is not None:
                # Filter out None values - queries should handle missing params gracefully
                params = {k: v for k, v in params.items() if v is not None}
                # Normalize parameter keys based on paradigm
                # P1/P2: lowercase for named %(name)s placeholders
                # M1/M2: lowercase for $name Cypher params
                # O2: camelCase for SPARQL ?var bindings
                if self.paradigm in ("P1", "P2", "M1", "M2"):
                    params = normalize_param_keys(params, target_case="lower")
                elif self.paradigm == "O2":
                    params = normalize_param_keys(params, target_case="camel")
                return params

        # No sampled params available - return empty dict
        # Parameters MUST come from the dataset (queries_params.yaml or expected_answers)
        # The caller should ensure _sampled_params is initialized from the dataset
        has_sampled = hasattr(self, "_sampled_params")
        sampled_value = self._sampled_params if has_sampled else "unset"
        logger.warning(
            f"No sampled parameters for {query_id}. "
            f"data_path={self._data_path}, _sampled_params={sampled_value}. "
            "Ensure dataset is loaded with queries_params.yaml."
        )
        return {}

    def _init_param_sampler(self):
        """Initialize parameters from queries_params.yaml or dynamic sampling."""
        logger.debug(f"Initializing param sampler, data_path={self._data_path}")

        # Try to load from queries_params.yaml first
        if self._data_path:
            params_file = self._data_path / "queries_params.yaml"
            logger.debug(f"Looking for params file: {params_file}, exists={params_file.exists()}")

            if params_file.exists():
                try:
                    import yaml
                    with open(params_file, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    file_params = data.get("parameters", {})
                    logger.debug(f"Loaded {len(file_params)} parameters from YAML")

                    self._sampled_params = self._build_sampled_params(file_params)
                    logger.info(f"Successfully loaded params from {params_file}")
                    if self.verbose:
                        self._console.print("[dim]Loaded params from queries_params.yaml[/dim]")
                    return
                except Exception as e:
                    # Always log errors, not just in verbose mode
                    logger.error(f"Failed to load queries_params.yaml: {e}", exc_info=True)
                    if self.verbose:
                        self._console.print(f"[yellow]Warning: Failed to load queries_params.yaml: {e}[/yellow]")
            else:
                logger.warning(f"queries_params.yaml not found at {params_file}")
        else:
            logger.warning("No data_path set, cannot load queries_params.yaml")

        # Fallback to dynamic sampling
        logger.debug("Falling back to dynamic sampling")
        try:
            from ..core.param_sampler import ParamSampler
            runner = self._get_runner()
            sampler = ParamSampler(self.paradigm, runner, seed=42)
            self._sampled_params = sampler.sample()
            logger.info("Dynamic params sampled successfully")
            if self.verbose:
                self._console.print("[dim]Dynamic params sampled from dataset[/dim]")
        except Exception as e:
            # Always log errors
            logger.error(f"Param sampling failed: {e}", exc_info=True)
            self._sampled_params = None
            if self.verbose:
                self._console.print(f"[dim]Param sampling failed: {e}[/dim]")

    def _build_sampled_params(self, file_params: dict):
        """Build SampledParams from queries_params.yaml content."""
        from ..core.param_sampler import SampledParams

        # Validate critical fields
        critical_fields = ["meter_id", "equipment_id", "space_id", "floor_id", "building_id"]
        missing = [f for f in critical_fields if not file_params.get(f)]
        if missing:
            logger.warning(f"Missing critical fields in queries_params.yaml: {missing}")

        return SampledParams(
            building_id=file_params.get("building_id"),
            floor_id=file_params.get("floor_id"),
            space_id=file_params.get("space_id"),
            equipment_id=file_params.get("equipment_id"),
            meter_id=file_params.get("meter_id"),
            ups_id=file_params.get("ups_id"),
            tenant_id=file_params.get("tenant_id"),
            point_id=file_params.get("point_id"),
            source_type=file_params.get("source_type", "MainMeter"),
            tag_pattern=file_params.get("tag_pattern", "^brick:"),
            capability=file_params.get("capability", "humidity_control"),
            date_start=file_params.get("date_start", "2024-01-15T00:00:00Z"),
            date_end=file_params.get("date_end", "2024-01-15T23:59:59Z"),
            reference_date=file_params.get("reference_date", "2024-06-01"),
            days_ahead=file_params.get("days_ahead", 90),
            max_hops=file_params.get("max_hops", 3),
            co2_factor=file_params.get("co2_factor", 0.5),
            device_id=file_params.get("device_id", 1234),
            # New fields for Q20/Q21
            hvac_source_equipment_id=file_params.get("hvac_source_equipment_id"),
            hvac_target_space_id=file_params.get("hvac_target_space_id"),
            critical_equipment_id=file_params.get("critical_equipment_id"),
            building_with_offices_id=file_params.get("building_with_offices_id"),
            # New fields for Q26/Q29/Q32
            transformer_id=file_params.get("transformer_id"),
            domain=file_params.get("domain", "HVAC"),
            # Q27 evacuation path
            evacuation_space_id=file_params.get("evacuation_space_id"),
        )

    def _get_variant_params(self, query_id: str, variant_id: int) -> dict[str, Any]:
        """Get parameters for a specific variant.

        Variant 0 = default params, variants 1+ add some variation.
        """
        params = self._get_default_params(query_id)

        # For now, just use default params for all variants
        # TODO: implement proper variant generation with seed
        return params
