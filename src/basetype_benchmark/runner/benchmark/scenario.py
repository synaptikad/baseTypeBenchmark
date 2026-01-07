"""Benchmark scenario orchestration.

Sprint 3 - Benchmark BaseType V3

Main orchestrator for complete benchmark execution:
- Multi-paradigm coordination
- Data loading
- RAM gradient testing
- Results aggregation

Implements the protocol from papier.md Section 3.4.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import (
    EngineType,
    PostgresConfig,
    MemgraphConfig,
    OxigraphConfig,
)
from ..loaders import get_loader
from ..ram import IsolationManager, RAMGradientExecutor, GradientResult
from .results import (
    BenchmarkResults,
    BenchmarkConfig,
    ParadigmResults,
    LevelResult,
    QueryResult,
)


console = Console()


@dataclass
class ScenarioConfig:
    """Configuration for benchmark scenario."""
    paradigms: list[str] = field(default_factory=lambda: ["P1", "P2", "M1", "M2", "O2"])
    queries: list[str] | None = None  # None = all queries
    data_profile: str = "small"
    ram_levels_mb: list[int] = field(default_factory=lambda: [131072, 65536, 32768, 16384, 8192])
    n_warmup: int = 3
    n_runs: int = 10
    n_variants: int = 3
    timeout_seconds: float = 300.0

    def to_benchmark_config(self) -> BenchmarkConfig:
        """Convert to BenchmarkConfig for results."""
        return BenchmarkConfig(
            paradigms=self.paradigms,
            queries=self.queries or [],
            data_profile=self.data_profile,
            ram_levels_mb=self.ram_levels_mb,
            n_warmup=self.n_warmup,
            n_runs=self.n_runs,
            n_variants=self.n_variants,
            timeout_seconds=self.timeout_seconds,
        )


# Progress callback type
ProgressCallback = Callable[[str, str, float], None]


class BenchmarkOrchestrator:
    """Main benchmark orchestration.

    Coordinates the complete benchmark workflow:
    1. For each paradigm:
       a. Start containers
       b. Load data
       c. Run RAM gradient
       d. Stop containers
    2. Aggregate results
    3. Export to JSON

    Example:
        ```python
        orchestrator = BenchmarkOrchestrator(configs={
            "P1": PostgresConfig(...),
            "M1": MemgraphConfig(...),
            ...
        })

        results = orchestrator.run_full_benchmark(
            data_dir=Path("data/export"),
            output_path=Path("results.json"),
            scenario=ScenarioConfig(paradigms=["P1", "M1"]),
        )
        ```
    """

    PAUSE_BETWEEN_PARADIGMS = 30  # seconds

    def __init__(
        self,
        configs: dict[str, Any],
        compose_file: Path | None = None,
    ):
        """Initialize orchestrator.

        Args:
            configs: Dict mapping paradigm to connection config
            compose_file: Path to docker-compose.yml
        """
        self.configs = configs
        self.isolation = IsolationManager(compose_file=compose_file)

    def run_full_benchmark(
        self,
        data_dir: Path,
        output_path: Path | None = None,
        scenario: ScenarioConfig | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> BenchmarkResults:
        """Execute complete benchmark.

        Args:
            data_dir: Directory with exported data
            output_path: Path for JSON output (optional)
            scenario: Scenario configuration
            on_progress: Progress callback

        Returns:
            BenchmarkResults with all data
        """
        scenario = scenario or ScenarioConfig()
        results = BenchmarkResults()
        results.config = scenario.to_benchmark_config()
        results.start_time = datetime.now()

        # Get queries if not specified
        queries = scenario.queries
        if not queries:
            queries = self._get_all_queries()

        console.print(Panel.fit(
            f"[bold blue]Benchmark Runner V3[/bold blue]\n\n"
            f"Paradigms: {', '.join(scenario.paradigms)}\n"
            f"Queries: {len(queries)}\n"
            f"RAM levels: {len(scenario.ram_levels_mb)}\n"
            f"Data profile: {scenario.data_profile}",
            title="Starting Benchmark",
            border_style="blue",
        ))

        # Run each paradigm
        for i, paradigm in enumerate(scenario.paradigms):
            console.print(f"\n[bold cyan]===== {paradigm} ({i+1}/{len(scenario.paradigms)}) =====[/bold cyan]")

            try:
                paradigm_results = self._run_paradigm(
                    paradigm=paradigm,
                    data_dir=data_dir,
                    queries=queries,
                    scenario=scenario,
                    on_progress=on_progress,
                )
                results.add_paradigm_results(paradigm, paradigm_results)

            except Exception as e:
                console.print(f"[red]Error running {paradigm}: {e}[/red]")
                results.add_paradigm_results(paradigm, ParadigmResults(
                    paradigm=paradigm,
                ))

            # Pause between paradigms
            if i < len(scenario.paradigms) - 1:
                console.print(f"[dim]Pausing {self.PAUSE_BETWEEN_PARADIGMS}s before next paradigm...[/dim]")
                time.sleep(self.PAUSE_BETWEEN_PARADIGMS)

        results.end_time = datetime.now()

        # Export results
        if output_path:
            results.to_json(output_path)
            console.print(f"\n[green]Results saved to {output_path}[/green]")

        # Print summary
        self._print_summary(results)

        return results

    def _run_paradigm(
        self,
        paradigm: str,
        data_dir: Path,
        queries: list[str],
        scenario: ScenarioConfig,
        on_progress: ProgressCallback | None = None,
    ) -> ParadigmResults:
        """Run benchmark for a single paradigm.

        Args:
            paradigm: Paradigm ID
            data_dir: Data directory
            queries: Query IDs
            scenario: Scenario config
            on_progress: Progress callback

        Returns:
            ParadigmResults
        """
        results = ParadigmResults(paradigm=paradigm)

        # 1. Start containers
        console.print(f"  [dim]Starting containers...[/dim]")
        self.isolation.start_paradigm(paradigm)

        try:
            # 2. Load data
            console.print(f"  [dim]Loading data...[/dim]")
            self._load_data(paradigm, data_dir)

            # 3. Run gradient
            console.print(f"  [dim]Running RAM gradient...[/dim]")
            gradient_result = self._run_gradient(
                paradigm=paradigm,
                queries=queries,
                scenario=scenario,
                on_progress=on_progress,
            )

            # Convert gradient results
            results.baseline_peak_mb = gradient_result.baseline_peak_mb

            for level in gradient_result.levels:
                level_result = LevelResult(
                    limit_mb=level.limit_mb,
                    status=level.status,
                    actual_peak_mb=level.actual_peak_mb,
                    duration_seconds=level.duration_seconds,
                    error_message=level.error_message,
                )

                # Convert query stats
                for qid, stats in level.query_stats.items():
                    level_result.queries[qid] = QueryResult(
                        query_id=qid,
                        p50_ms=stats.p50_ms,
                        p95_ms=stats.p95_ms,
                        avg_ms=stats.avg_ms,
                        min_ms=stats.min_ms,
                        max_ms=stats.max_ms,
                        stddev_ms=stats.stddev_ms,
                        success_rate=stats.success_rate,
                        memory_peak_mb=stats.memory_peak_mb,
                        run_count=len(stats.runs),
                    )

                results.levels.append(level_result)

        finally:
            # 4. Stop containers
            console.print(f"  [dim]Stopping containers...[/dim]")
            self.isolation.stop_paradigm(paradigm)

        # Print paradigm summary
        console.print(f"  [green]RAM viable: {results.ram_viable_mb} MB[/green]")

        return results

    def _load_data(self, paradigm: str, data_dir: Path) -> None:
        """Load data for a paradigm.

        Args:
            paradigm: Paradigm ID
            data_dir: Data directory
        """
        config = self._get_config(paradigm)
        ts_config = self._get_timescale_config(paradigm)

        loader = get_loader(paradigm, config, ts_config)

        if not loader.check_connection():
            raise RuntimeError(f"Cannot connect to {paradigm} database")

        # Clear and load
        loader.clear_database()
        result = loader.load_all(data_dir)

        if not result.success:
            raise RuntimeError(f"Data loading failed: {result.errors}")

    def _run_gradient(
        self,
        paradigm: str,
        queries: list[str],
        scenario: ScenarioConfig,
        on_progress: ProgressCallback | None = None,
    ) -> GradientResult:
        """Run RAM gradient for a paradigm.

        Args:
            paradigm: Paradigm ID
            queries: Query IDs
            scenario: Scenario config
            on_progress: Progress callback

        Returns:
            GradientResult
        """
        executor = RAMGradientExecutor(
            paradigm=paradigm,
            isolation=self.isolation,
            configs=self.configs,
            n_warmup=scenario.n_warmup,
            n_runs=scenario.n_runs,
            n_variants=scenario.n_variants,
            timeout_seconds=scenario.timeout_seconds,
        )

        def progress_wrapper(msg: str, current: int, total: int):
            console.print(f"    {msg} ({current}/{total})")
            if on_progress:
                on_progress(paradigm, msg, current / total)

        return executor.run_gradient(
            queries=queries,
            levels_mb=scenario.ram_levels_mb,
            on_progress=progress_wrapper,
        )

    def _get_config(self, paradigm: str):
        """Get primary config for paradigm."""
        paradigm = paradigm.upper()

        if paradigm in self.configs:
            return self.configs[paradigm]

        # Try to find by type
        if paradigm in ("P1", "P2"):
            for key, cfg in self.configs.items():
                if isinstance(cfg, PostgresConfig):
                    return cfg
        elif paradigm in ("M1", "M2"):
            for key, cfg in self.configs.items():
                if isinstance(cfg, MemgraphConfig):
                    return cfg
        elif paradigm == "O2":
            for key, cfg in self.configs.items():
                if isinstance(cfg, OxigraphConfig):
                    return cfg

        raise ValueError(f"No config found for {paradigm}")

    def _get_timescale_config(self, paradigm: str) -> PostgresConfig | None:
        """Get TimescaleDB config for hybrid paradigms."""
        if paradigm not in ("M2", "O2"):
            return None

        # Look for timescale config
        if "timescale" in self.configs:
            return self.configs["timescale"]

        # Fall back to any PostgresConfig
        for key, cfg in self.configs.items():
            if isinstance(cfg, PostgresConfig) and key not in ("P1", "P2"):
                return cfg

        return None

    def _get_all_queries(self) -> list[str]:
        """Get all available query IDs."""
        # Default: Q1-Q23
        return [f"Q{i}" for i in range(1, 24)]

    def _print_summary(self, results: BenchmarkResults) -> None:
        """Print benchmark summary."""
        summary = results.get_summary()

        console.print("\n" + "=" * 60)
        console.print("[bold]Benchmark Summary[/bold]")
        console.print("=" * 60)

        console.print("\n[cyan]RAM Viable (smallest without OOM):[/cyan]")
        for paradigm, ram in summary["ram_viable"].items():
            if ram is not None:
                console.print(f"  {paradigm}: {ram:,} MB ({ram/1024:.0f} GB)")
            else:
                console.print(f"  {paradigm}: [red]All OOM[/red]")

        console.print("\n[cyan]RAM Baseline:[/cyan]")
        for paradigm, ram in summary["ram_baseline"].items():
            console.print(f"  {paradigm}: {ram:,.0f} MB")

        duration = (results.end_time - results.start_time).total_seconds() if results.end_time else 0
        console.print(f"\n[dim]Total duration: {duration:.0f}s[/dim]")
