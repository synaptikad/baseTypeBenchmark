"""Workload executor for stress testing.

Executes workload scenarios (query sequences) and collects metrics.
Unlike the simple benchmark, workloads:
- Don't reset database state between queries
- Run sequences in loops with optional duration limits
- Focus on throughput (QPS) and latency distribution
"""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Callable

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from ..config import EngineType, QueryCategory
from ..core.catalog import QueryCatalog
from ..monitoring import (
    CgroupsV2Monitor,
    PeakMemoryTracker,
    DockerClient,
)
from ..runners import get_runner, get_hybrid_runner, RunResult, RunStatus
from ..ram.isolation import IsolationManager

from .models import (
    QueryStep,
    QueryStats,
    WorkloadResult,
    WorkloadResults,
    WorkloadScenario,
)


# Progress callback type
ProgressCallback = Callable[[str, int, int], None]


class WorkloadExecutor:
    """Execute workload scenarios and collect metrics.

    Unlike RAMGradientExecutor, this executor:
    - Runs at fixed RAM (no gradient)
    - Doesn't reset state between queries
    - Supports looping with duration limits
    - Tracks per-query memory via cgroups reset

    Example:
        ```python
        executor = WorkloadExecutor(
            paradigm="M1",
            isolation=IsolationManager(...),
            configs={"M1": MemgraphConfig(...)},
        )

        result = executor.run_scenario(scenario)
        print(f"QPS: {result.qps:.1f}")
        print(f"p95 latency: {result.latency_p95_ms:.1f} ms")
        ```
    """

    def __init__(
        self,
        paradigm: str,
        isolation: IsolationManager,
        configs: dict,
        timeout_seconds: float = 60.0,
        verbose: bool = True,
    ):
        """Initialize workload executor.

        Args:
            paradigm: P1, P2, M1, or M2
            isolation: Container isolation manager
            configs: Dict with connection configs by paradigm
            timeout_seconds: Query timeout
            verbose: Show detailed progress
        """
        self.paradigm = paradigm.upper()
        self.isolation = isolation
        self.configs = configs
        self.timeout = timeout_seconds
        self.verbose = verbose

        self._docker = DockerClient()
        self._console = Console()
        self._catalog = QueryCatalog()
        self._data_path: Path | None = None
        self._params_cache: dict = {}

    def set_data_path(self, data_path: Path) -> None:
        """Set data directory for queries_params.yaml."""
        self._data_path = Path(data_path)
        self._load_params()

    def _load_params(self) -> None:
        """Load query parameters from data directory."""
        if not self._data_path:
            return

        params_file = self._data_path / "queries_params.yaml"
        if params_file.exists():
            import yaml
            with open(params_file) as f:
                self._params_cache = yaml.safe_load(f) or {}

    def run_scenario(
        self,
        scenario: WorkloadScenario,
        on_progress: ProgressCallback | None = None,
    ) -> WorkloadResult:
        """Execute a complete workload scenario.

        Args:
            scenario: Workload scenario to execute
            on_progress: Optional progress callback

        Returns:
            WorkloadResult with throughput and latency metrics
        """
        result = WorkloadResult(
            scenario_name=scenario.name,
            paradigm=self.paradigm,
        )
        result.start_time = datetime.now().isoformat()

        # Ensure containers are running
        if not self.isolation.is_paradigm_running(self.paradigm):
            self.isolation.start_paradigm(self.paradigm)

        # Get container IDs for memory tracking
        container_ids = self.isolation.get_container_ids(self.paradigm)
        peak_trackers = self._setup_peak_trackers(container_ids)

        # Get RAM limit if set
        try:
            for name, cid in container_ids.items():
                monitor = CgroupsV2Monitor(cid)
                if monitor.get_memory_max():
                    result.ram_limit_mb = monitor.get_memory_max() // (1024 * 1024)
                break
        except Exception:
            pass

        # Get runner
        runner = self._get_runner()

        # Initialize query stats
        for step in scenario.sequence:
            if step.query_id not in result.query_stats:
                result.query_stats[step.query_id] = QueryStats(query_id=step.query_id)

        # Execute workload
        start_time = time.perf_counter()
        global_peak_mb = 0.0

        if self.verbose:
            self._console.print(f"\n[bold]Running workload: {scenario.name}[/bold]")
            self._console.print(f"Profile: {scenario.profile.value}")
            self._console.print(f"Duration: {scenario.duration_seconds}s, Loop: {scenario.loop}")
            self._console.print()

        try:
            if scenario.loop and scenario.duration_seconds:
                # Loop until duration
                loop_count = 0
                while (time.perf_counter() - start_time) < scenario.duration_seconds:
                    loop_count += 1
                    if self.verbose and loop_count % 10 == 1:
                        elapsed = time.perf_counter() - start_time
                        self._console.print(
                            f"  [dim]Loop {loop_count}, elapsed: {elapsed:.0f}s[/dim]"
                        )

                    loop_peak = self._execute_sequence(
                        scenario.sequence,
                        runner,
                        result.query_stats,
                        peak_trackers,
                    )
                    global_peak_mb = max(global_peak_mb, loop_peak)
            else:
                # Run sequence once
                global_peak_mb = self._execute_sequence(
                    scenario.sequence,
                    runner,
                    result.query_stats,
                    peak_trackers,
                )

        except KeyboardInterrupt:
            if self.verbose:
                self._console.print("\n[yellow]Interrupted by user[/yellow]")
        except Exception as e:
            if self.verbose:
                self._console.print(f"\n[red]Error: {e}[/red]")

        # Compute final stats
        result.total_duration_seconds = time.perf_counter() - start_time
        result.scenario_memory_peak_mb = global_peak_mb
        result.end_time = datetime.now().isoformat()

        # Compute per-query stats
        for stats in result.query_stats.values():
            stats.compute_stats()

        # Compute global stats
        result.compute_global_stats()

        # Cleanup peak trackers
        for tracker in peak_trackers.values():
            tracker.close()

        if self.verbose:
            self._print_summary(result)

        return result

    def _execute_sequence(
        self,
        sequence: list[QueryStep],
        runner,
        query_stats: dict[str, QueryStats],
        peak_trackers: dict[str, PeakMemoryTracker],
    ) -> float:
        """Execute a sequence of query steps.

        Args:
            sequence: List of QueryStep to execute
            runner: Query runner
            query_stats: Dict to accumulate stats
            peak_trackers: Memory peak trackers

        Returns:
            Maximum memory peak observed during sequence
        """
        max_peak_mb = 0.0

        for step in sequence:
            query_id = step.query_id

            # Check if query can be executed for this paradigm
            try:
                query_def = self._catalog.get_query(query_id)
                engine_type = EngineType(self.paradigm)
                if not query_def.can_execute(engine_type):
                    # Skip impossible queries
                    continue
            except Exception:
                continue

            # Execute step (with repeats)
            for _ in range(step.repeat):
                try:
                    # Reset memory peak before query
                    for tracker in peak_trackers.values():
                        tracker.reset()

                    # Get query text and params
                    query_text = self._get_query_text(query_id)
                    params = self._get_params(query_id, step.batch_size)

                    # Execute query
                    exec_start = time.perf_counter()
                    result = runner.execute(query_text, params, self.timeout)
                    duration_ms = (time.perf_counter() - exec_start) * 1000

                    # Read memory peak
                    memory_peak_mb = 0.0
                    for tracker in peak_trackers.values():
                        peak = tracker.read_peak() / (1024 * 1024)
                        memory_peak_mb = max(memory_peak_mb, peak)

                    max_peak_mb = max(max_peak_mb, memory_peak_mb)

                    # Record execution
                    success = result.status == RunStatus.SUCCESS
                    query_stats[query_id].add_execution(
                        duration_ms=duration_ms,
                        success=success,
                        memory_peak_mb=memory_peak_mb,
                    )

                except Exception as e:
                    # Record failure
                    query_stats[query_id].add_execution(
                        duration_ms=0,
                        success=False,
                        memory_peak_mb=0,
                    )

                # Think time
                if step.think_time_ms > 0:
                    time.sleep(step.think_time_ms / 1000)

        return max_peak_mb

    def _setup_peak_trackers(
        self,
        container_ids: dict[str, str],
    ) -> dict[str, PeakMemoryTracker]:
        """Setup memory peak trackers for containers."""
        trackers: dict[str, PeakMemoryTracker] = {}

        for name, cid in container_ids.items():
            try:
                monitor = CgroupsV2Monitor(cid)
                trackers[name] = PeakMemoryTracker(monitor.cgroup_path)
            except Exception:
                pass

        return trackers

    def _get_runner(self):
        """Get appropriate runner for paradigm."""
        if self.paradigm == "M2":
            return get_hybrid_runner(self.paradigm, self.configs)
        else:
            return get_runner(self.paradigm, self.configs)

    def _get_query_text(self, query_id: str) -> str:
        """Get query text for paradigm."""
        query_def = self._catalog.get_query(query_id)
        return query_def.get_query_text(EngineType(self.paradigm))

    def _get_params(self, query_id: str, batch_size: int | None = None) -> dict | tuple:
        """Get query parameters."""
        # Check cache first
        if query_id in self._params_cache:
            params = self._params_cache[query_id].copy()
        else:
            # Use default params from catalog
            query_def = self._catalog.get_query(query_id)
            params = {p.name: p.default for p in query_def.parameters}

        # Handle batch_size for write queries
        if batch_size is not None:
            params["batch_size"] = batch_size

        # Convert to tuple for SQL positional binding (P1/P2)
        # Skip for write_workload, jsonb_write, and jsonb_validation which use named placeholders %(name)s
        query_def = self._catalog.get_query(query_id)
        if self.paradigm in ("P1", "P2") and query_def.category not in (
            QueryCategory.WRITE_WORKLOAD, QueryCategory.JSONB_WRITE, QueryCategory.JSONB_VALIDATION
        ):
            from ..core.query_utils import get_ordered_params
            return get_ordered_params(params, query_def.parameter_order)

        return params

    def _print_summary(self, result: WorkloadResult) -> None:
        """Print result summary to console."""
        self._console.print()
        self._console.print("[bold]Workload Results[/bold]")
        self._console.print(f"  Paradigm: {result.paradigm}")
        self._console.print(f"  Duration: {result.total_duration_seconds:.1f}s")
        self._console.print(f"  Queries: {result.total_queries}")
        self._console.print(f"  [green]QPS: {result.qps:.1f}[/green]")
        self._console.print()
        self._console.print("[bold]Latency[/bold]")
        self._console.print(f"  p50: {result.latency_p50_ms:.1f} ms")
        self._console.print(f"  p95: {result.latency_p95_ms:.1f} ms")
        self._console.print(f"  p99: {result.latency_p99_ms:.1f} ms")
        self._console.print(f"  max: {result.latency_max_ms:.1f} ms")

        if result.total_errors > 0:
            self._console.print()
            self._console.print(f"[red]Errors: {result.total_errors} ({result.error_rate:.1%})[/red]")

        if result.scenario_memory_peak_mb > 0:
            self._console.print()
            self._console.print(f"[bold]Memory Peak[/bold]: {result.scenario_memory_peak_mb:.0f} MB")


class WorkloadOrchestrator:
    """Orchestrate workload execution across multiple paradigms.

    Example:
        ```python
        orchestrator = WorkloadOrchestrator(
            isolation=IsolationManager(...),
            configs=configs,
        )

        results = orchestrator.run_workload(
            scenario=workload,
            paradigms=["P1", "M1", "M2"],
            data_path=Path("data/generated/small-1w"),
        )

        results.to_json("workload_results.json")
        ```
    """

    def __init__(
        self,
        isolation: IsolationManager,
        configs: dict,
        timeout_seconds: float = 60.0,
        verbose: bool = True,
    ):
        self.isolation = isolation
        self.configs = configs
        self.timeout = timeout_seconds
        self.verbose = verbose
        self._console = Console()

    def run_workload(
        self,
        scenario: WorkloadScenario,
        paradigms: list[str] | None = None,
        data_path: Path | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> WorkloadResults:
        """Run workload across multiple paradigms.

        Args:
            scenario: Workload scenario
            paradigms: Paradigms to test (default: from scenario)
            data_path: Path to dataset
            on_progress: Progress callback

        Returns:
            WorkloadResults with per-paradigm results
        """
        paradigms = paradigms or scenario.paradigms
        results = WorkloadResults(scenario=scenario)

        for i, paradigm in enumerate(paradigms):
            if self.verbose:
                self._console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
                self._console.print(f"[bold]Paradigm: {paradigm}[/bold] ({i+1}/{len(paradigms)})")
                self._console.print(f"[bold cyan]{'='*60}[/bold cyan]")

            if on_progress:
                on_progress(paradigm, i + 1, len(paradigms))

            try:
                executor = WorkloadExecutor(
                    paradigm=paradigm,
                    isolation=self.isolation,
                    configs=self.configs,
                    timeout_seconds=self.timeout,
                    verbose=self.verbose,
                )

                if data_path:
                    executor.set_data_path(data_path)

                result = executor.run_scenario(scenario)
                results.results[paradigm] = result

            except Exception as e:
                if self.verbose:
                    self._console.print(f"[red]Failed: {e}[/red]")
                # Create error result
                results.results[paradigm] = WorkloadResult(
                    scenario_name=scenario.name,
                    paradigm=paradigm,
                )

        return results
