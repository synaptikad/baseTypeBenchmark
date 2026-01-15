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

import shutil
import subprocess
import sys
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
    TIMESCALE_PARADIGMS,
)
from ..loaders import get_loader
from ..loaders.progress import LoadProgressDisplay, ExportProgressDisplay
from ..ram import IsolationManager, RAMGradientExecutor, GradientResult
from ...dataset.calibration import (
    load_calibration,
    save_calibration,
    get_or_create_calibration,
    needs_calibration,
    RAMCalibration,
)
from .results import (
    BenchmarkResults,
    BenchmarkConfig,
    ParadigmResults,
    LevelResult,
    QueryResult,
)
from .archive import ResultsArchive


console = Console()


@dataclass
class ScenarioConfig:
    """Configuration for benchmark scenario."""
    paradigms: list[str] = field(default_factory=lambda: ["P1", "P2", "M1", "M2"])
    queries: list[str] | None = None  # None = all queries
    data_profile: str = "small"
    ram_levels_mb: list[int] = field(default_factory=lambda: [131072, 65536, 32768, 16384, 8192])
    n_warmup: int = 0  # Warmup disabled by default (middleware benchmark)
    n_runs: int = 10
    n_variants: int = 3
    timeout_seconds: float = 300.0
    # RAM calibration options (2-phase protocol)
    force_calibration: bool = False  # Re-run calibration even if cached
    skip_calibration: bool = False  # Skip calibration entirely (use full ram_levels_mb)
    calibration_max_mb: int = 65536  # Calibration max RAM in MB
    calibration_min_mb: int = 512    # Calibration min RAM in MB

    def to_benchmark_config(self, actual_queries: list[str] | None = None) -> BenchmarkConfig:
        """Convert to BenchmarkConfig for results.

        Args:
            actual_queries: Actual queries that were run (overrides self.queries)
        """
        return BenchmarkConfig(
            paradigms=self.paradigms,
            queries=actual_queries or self.queries or [],
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

    Coordinates the complete benchmark workflow with disk optimization:
    1. For each paradigm:
       a. Export data (from Parquet source)
       b. Start containers
       c. Load data
       d. Run RAM gradient
       e. Stop containers
       f. Cleanup exports (optional, saves disk space)
    2. Aggregate results
    3. Export to JSON

    This disk-optimized workflow keeps only ONE paradigm's exported data
    on disk at a time, reducing peak disk usage from ~5x to ~1x dataset size.

    Example:
        ```python
        orchestrator = BenchmarkOrchestrator(configs={
            "P1": PostgresConfig(...),
            "M1": MemgraphConfig(...),
            ...
        })

        # Disk-optimized mode (default)
        results = orchestrator.run_full_benchmark(
            source_dir=Path("data/generated/small-1w"),  # Parquet source
            export_dir=Path("data/exports"),             # Temporary exports
            output_path=Path("results.json"),
            scenario=ScenarioConfig(paradigms=["P1", "M1"]),
            cleanup_exports=True,  # Remove exports after each paradigm
        )
        ```
    """

    # Map paradigm → exporter module
    EXPORTER_MODULES = {
        "P1": "src.basetype_benchmark.exporters.p1_extractor",
        "P2": "src.basetype_benchmark.exporters.p2_extractor",
        "M1": "src.basetype_benchmark.exporters.m1m2_extractor",
        "M2": "src.basetype_benchmark.exporters.m1m2_extractor",
    }

    def __init__(
        self,
        configs: dict[str, Any],
        compose_file: Path | None = None,
        archive_path: Path | None = None,
    ):
        """Initialize orchestrator.

        Args:
            configs: Dict mapping paradigm to connection config
            compose_file: Path to docker-compose.yml
            archive_path: Path for results archive (enables raw result storage)
        """
        self.configs = configs
        self.isolation = IsolationManager(compose_file=compose_file)
        self._timeseries_loaded = False  # Track if TS loaded (Option A)

        # Results archive for raw data storage
        self._archive: ResultsArchive | None = None
        if archive_path:
            self._archive = ResultsArchive(archive_path)

    def run_full_benchmark(
        self,
        source_dir: Path,
        export_dir: Path,
        output_path: Path | None = None,
        scenario: ScenarioConfig | None = None,
        cleanup_exports: bool = True,
        on_progress: ProgressCallback | None = None,
    ) -> BenchmarkResults:
        """Execute complete benchmark with disk optimization.

        Args:
            source_dir: Directory with Parquet source files (nodes.parquet, etc.)
            export_dir: Base directory for paradigm exports (temporary)
            output_path: Path for JSON output (optional)
            scenario: Scenario configuration
            cleanup_exports: If True, delete exports after each paradigm (saves disk)
            on_progress: Progress callback

        Returns:
            BenchmarkResults with all data
        """
        scenario = scenario or ScenarioConfig()
        results = BenchmarkResults()

        # Reset state for new benchmark run (Option A)
        self._timeseries_loaded = False

        # Get queries if not specified
        queries = scenario.queries
        if not queries:
            queries = self._get_all_queries()

        # Extract data_profile from source_dir name (e.g., "medium-1m" → "medium-1m")
        data_profile = source_dir.name if source_dir else scenario.data_profile
        scenario.data_profile = data_profile

        # Set config with actual queries
        results.config = scenario.to_benchmark_config(actual_queries=queries)
        results.start_time = datetime.now()

        # Start archive if enabled
        if self._archive:
            self._archive.start_run(
                benchmark_id=results.benchmark_id,
                paradigms=scenario.paradigms,
                queries=queries,
                data_profile=scenario.data_profile,
                ram_levels_mb=scenario.ram_levels_mb,
                n_warmup=scenario.n_warmup,
                n_runs=scenario.n_runs,
                n_variants=scenario.n_variants,
                timeout_seconds=scenario.timeout_seconds,
            )

        disk_mode = "optimisé" if cleanup_exports else "persistant"
        console.print(Panel.fit(
            f"[bold blue]Benchmark Runner V3[/bold blue]\n\n"
            f"Paradigms: {', '.join(scenario.paradigms)}\n"
            f"Queries: {len(queries)}\n"
            f"RAM levels: {len(scenario.ram_levels_mb)}\n"
            f"Data profile: {scenario.data_profile}\n"
            f"Disk mode: {disk_mode}",
            title="Starting Benchmark",
            border_style="blue",
        ))

        # Run each paradigm (export → load → benchmark → cleanup)
        for i, paradigm in enumerate(scenario.paradigms):
            console.print(f"\n[bold cyan]===== {paradigm} ({i+1}/{len(scenario.paradigms)}) =====[/bold cyan]")

            try:
                paradigm_results = self._run_paradigm(
                    paradigm=paradigm,
                    source_dir=source_dir,
                    export_dir=export_dir,
                    queries=queries,
                    scenario=scenario,
                    cleanup_exports=cleanup_exports,
                    on_progress=on_progress,
                )
                results.add_paradigm_results(paradigm, paradigm_results)

            except Exception as e:
                console.print(f"[red]Error running {paradigm}: {e}[/red]")
                results.add_paradigm_results(paradigm, ParadigmResults(
                    paradigm=paradigm,
                ))

        # Cleanup: Stop all containers after benchmark completes
        console.print("\n[dim]Stopping all containers...[/dim]")
        for paradigm in scenario.paradigms:
            try:
                self.isolation.stop_paradigm(paradigm)
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to stop {paradigm}: {e}[/yellow]")

        results.end_time = datetime.now()

        # Finalize archive
        if self._archive:
            self._archive.finalize_run(benchmark_summary=results.to_dict())
            archive_path = self._archive.base_path / results.benchmark_id
            console.print(f"\n[green]Results archived to {archive_path}[/green]")

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
        source_dir: Path,
        export_dir: Path,
        queries: list[str],
        scenario: ScenarioConfig,
        cleanup_exports: bool = True,
        on_progress: ProgressCallback | None = None,
    ) -> ParadigmResults:
        """Run benchmark for a single paradigm with disk optimization.

        Workflow: export → start → load → benchmark → stop → cleanup

        Args:
            paradigm: Paradigm ID
            source_dir: Parquet source directory
            export_dir: Base export directory
            queries: Query IDs
            scenario: Scenario config
            cleanup_exports: Delete exports after benchmark
            on_progress: Progress callback

        Returns:
            ParadigmResults
        """
        results = ParadigmResults(paradigm=paradigm)
        paradigm_export_dir = None

        try:
            # 1. Export paradigm data
            console.print(f"  [dim]Exporting {paradigm}...[/dim]")
            paradigm_export_dir = self._export_paradigm(paradigm, source_dir, export_dir)

            # 2. Start containers
            console.print(f"  [dim]Starting containers...[/dim]")
            self.isolation.start_paradigm(paradigm)

            try:
                # 3. Load data
                console.print(f"  [dim]Loading data...[/dim]")
                self._load_data(paradigm, paradigm_export_dir)

                # 4. Run gradient
                console.print(f"  [dim]Running RAM gradient...[/dim]")
                gradient_result = self._run_gradient(
                    paradigm=paradigm,
                    queries=queries,
                    scenario=scenario,
                    source_dir=source_dir,
                    on_progress=on_progress,
                )

                # Convert gradient results
                results.baseline_peak_mb = gradient_result.baseline_peak_mb
                results.ram_plateau_mb = gradient_result.ram_plateau_mb

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
                            # Validation data for cross-paradigm comparison
                            row_count=stats.row_count,
                            sample_rows=stats.sample_rows,
                            row_hash=stats.row_hash,
                            column_names=stats.column_names,
                        )

                        # Archive raw results (all rows, not just sample)
                        if self._archive and stats.all_rows:
                            self._archive.save_query_result(
                                query_id=qid,
                                paradigm=paradigm,
                                rows=stats.all_rows,
                                column_names=stats.column_names or [],
                                parameters={},  # TODO: capture from gradient executor
                                execution_time_ms=stats.avg_ms,
                                ram_limit_mb=level.limit_mb,
                            )

                        # Save metrics separately
                        if self._archive:
                            self._archive.save_query_metrics(
                                query_id=qid,
                                paradigm=paradigm,
                                metrics={
                                    "query_id": qid,
                                    "ram_limit_mb": level.limit_mb,
                                    "p50_ms": stats.p50_ms,
                                    "p95_ms": stats.p95_ms,
                                    "avg_ms": stats.avg_ms,
                                    "min_ms": stats.min_ms,
                                    "max_ms": stats.max_ms,
                                    "stddev_ms": stats.stddev_ms,
                                    "success_rate": stats.success_rate,
                                    "memory_peak_mb": stats.memory_peak_mb,
                                    "run_count": len(stats.runs),
                                    "row_count": stats.row_count,
                                },
                            )

                    results.levels.append(level_result)

            finally:
                # 5. Stop containers (unless next paradigm shares TimescaleDB)
                # Force remove Memgraph if M1/M2 transition (they can't share data)
                force_remove_memgraph = self._needs_memgraph_cleanup(paradigm, scenario.paradigms)
                if self._should_keep_containers_running(paradigm, scenario.paradigms):
                    console.print(f"  [dim]Keeping containers running for Option A...[/dim]")
                    # Still need to clean Memgraph volume if M1->M2 transition
                    if force_remove_memgraph:
                        console.print(f"  [dim]Cleaning Memgraph volume (M1/M2 incompatible)...[/dim]")
                        self.isolation._clean_memgraph_volume()
                else:
                    console.print(f"  [dim]Stopping containers...[/dim]")
                    self.isolation.stop_paradigm(paradigm, force_remove=force_remove_memgraph)

        finally:
            # 6. Cleanup exports (disk optimization)
            if cleanup_exports and paradigm_export_dir and paradigm_export_dir.exists():
                console.print(f"  [dim]Cleaning up exports...[/dim]")
                shutil.rmtree(paradigm_export_dir)

        # Print paradigm summary
        if results.ram_plateau_mb and results.ram_plateau_mb != results.ram_viable_mb:
            console.print(
                f"  [green]RAM viable: {results.ram_viable_mb} MB, "
                f"plateau: {results.ram_plateau_mb} MB[/green]"
            )
        else:
            console.print(f"  [green]RAM viable: {results.ram_viable_mb} MB[/green]")

        return results

    def _should_keep_containers_running(
        self,
        current_paradigm: str,
        all_paradigms: list[str]
    ) -> bool:
        """Check if TimescaleDB container should stay running for later paradigms.

        Returns True if:
        - Current paradigm uses TimescaleDB (P1, P2, M2)
        - ANY remaining paradigm in queue also uses TimescaleDB
        - This enables Option A (shared TimescaleDB across paradigms)

        Note: We check ALL remaining paradigms, not just the next one.
        This is critical for sequences like P1->P2->M1->M2 where M1 doesn't
        use TimescaleDB but M2 does. We must keep TimescaleDB running
        across the M1 gap to preserve the shared timeseries data.

        Args:
            current_paradigm: Current paradigm that just finished
            all_paradigms: Full list of paradigms in execution order

        Returns:
            True if TimescaleDB container should stay running, False otherwise
        """
        # TimescaleDB paradigms that can share state via Option A
        # WITH schema isolation: P1, P2, M2 can all share ts.timeseries
        # P1 and P2 use separate structural schemas (p1/p2) to avoid conflicts

        # Only relevant if current paradigm uses TimescaleDB
        if current_paradigm not in TIMESCALE_PARADIGMS:
            return False

        # Check if there's a next paradigm
        try:
            current_idx = all_paradigms.index(current_paradigm)
        except ValueError:
            return False

        if current_idx >= len(all_paradigms) - 1:
            return False  # Last paradigm, safe to stop

        # Check if ANY remaining paradigm uses TimescaleDB (not just next)
        # This keeps TS running across M1 gap for sequences like P1->P2->M1->M2
        remaining_paradigms = all_paradigms[current_idx + 1:]
        return any(p in TIMESCALE_PARADIGMS for p in remaining_paradigms)

    def _needs_memgraph_cleanup(
        self,
        current_paradigm: str,
        all_paradigms: list[str]
    ) -> bool:
        """Check if Memgraph volume needs cleanup after current paradigm.

        M1 and M2 CANNOT share Memgraph data because:
        - M1 stores timeseries IN Memgraph (TimeseriesChunk nodes)
        - M2 stores timeseries in TimescaleDB

        Returns True if current is M1/M2 AND next Memgraph paradigm is different.

        Args:
            current_paradigm: Current paradigm that just finished
            all_paradigms: Full list of paradigms in execution order

        Returns:
            True if Memgraph volume must be cleaned, False otherwise
        """
        memgraph_paradigms = {"M1", "M2"}

        # Only relevant if current paradigm uses Memgraph
        if current_paradigm not in memgraph_paradigms:
            return False

        # Find next Memgraph paradigm in queue
        try:
            current_idx = all_paradigms.index(current_paradigm)
        except ValueError:
            return False

        remaining_paradigms = all_paradigms[current_idx + 1:]
        for next_paradigm in remaining_paradigms:
            if next_paradigm in memgraph_paradigms:
                # Next Memgraph paradigm found - cleanup needed if different
                return next_paradigm != current_paradigm

        # No more Memgraph paradigms - cleanup for cleanliness
        return True

    def _get_extractor(self, paradigm: str, output_dir: Path, input_dir: Path):
        """Get extractor instance for a paradigm.

        Args:
            paradigm: Paradigm ID (P1, P2, M1, M2)
            output_dir: Output directory for exported files
            input_dir: Input directory with Parquet files

        Returns:
            Extractor instance
        """
        paradigm_upper = paradigm.upper()

        if paradigm_upper == "P1":
            from basetype_benchmark.exporters.p1_extractor import P1Extractor
            return P1Extractor(output_dir=output_dir, input_dir=input_dir)
        elif paradigm_upper == "P2":
            from basetype_benchmark.exporters.p2_extractor import P2Extractor
            return P2Extractor(output_dir=output_dir, input_dir=input_dir)
        elif paradigm_upper in ("M1", "M2"):
            from basetype_benchmark.exporters.m1m2_extractor import M1M2Extractor
            return M1M2Extractor(output_dir=output_dir, input_dir=input_dir)
        else:
            raise ValueError(f"Unknown paradigm: {paradigm}")

    def _export_paradigm(
        self,
        paradigm: str,
        source_dir: Path,
        export_base_dir: Path,
    ) -> Path:
        """Export a paradigm from Parquet source files.

        Args:
            paradigm: Paradigm ID (P1, P2, M1, M2)
            source_dir: Directory with Parquet files
            export_base_dir: Base directory for exports

        Returns:
            Path to exported paradigm directory
        """
        paradigm_export_dir = export_base_dir / paradigm.lower() / source_dir.name
        paradigm_export_dir.mkdir(parents=True, exist_ok=True)

        extractor = self._get_extractor(paradigm, paradigm_export_dir, source_dir)

        with ExportProgressDisplay(paradigm) as display:
            result = extractor.export_all(progress_callback=display.update)
            display.print_summary(result)

        return paradigm_export_dir

    def _load_data(self, paradigm: str, data_dir: Path) -> None:
        """Load data for a paradigm.

        Args:
            paradigm: Paradigm ID
            data_dir: Data directory
        """
        config = self._get_config(paradigm)
        ts_config = self._get_timescale_config(paradigm)

        loader = get_loader(paradigm, config, ts_config)

        # Retry connection with exponential backoff (container may not be ready)
        max_retries = 5
        for attempt in range(max_retries):
            if loader.check_connection():
                break
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1, 2, 4, 8, 16 seconds
                console.print(f"  [dim]Waiting {wait_time}s for {paradigm} database...[/dim]")
                time.sleep(wait_time)
        else:
            raise RuntimeError(f"Cannot connect to {paradigm} database after {max_retries} attempts")

        # Determine if we should keep timeseries (Option A)
        keep_ts = self._should_keep_timeseries(paradigm)

        # Clear and load with progress display
        loader.clear_database(keep_timeseries=keep_ts)

        with LoadProgressDisplay(paradigm) as display:
            result = loader.load_all(data_dir, progress_callback=display.update)
            display.print_summary(result)

        if not result.success:
            raise RuntimeError(f"Data loading failed: {result.errors}")

        # Mark timeseries as loaded if this paradigm loaded it
        if result.timeseries_loaded > 0:
            self._timeseries_loaded = True

    def _should_keep_timeseries(self, paradigm: str) -> bool:
        """Determine if timeseries should be kept during clear.

        Keep timeseries if already loaded by previous paradigm.
        Checks both in-memory flag AND database state (for cross-process scenarios).

        Args:
            paradigm: Current paradigm being loaded

        Returns:
            True if timeseries should be preserved
        """
        if paradigm not in TIMESCALE_PARADIGMS:
            return False

        # Check in-memory flag first (same process)
        if self._timeseries_loaded:
            return True

        # Check database state (cross-process: e.g., P1 loaded in separate btb-runner call)
        # This handles calibration mode where each paradigm runs in a separate process
        try:
            from ..loaders import get_loader
            config = self._get_config(paradigm)
            ts_config = self._get_timescale_config(paradigm)
            loader = get_loader(paradigm, config, ts_config)

            if hasattr(loader, '_is_timeseries_populated') and loader._is_timeseries_populated():
                # Timeseries exist in DB from previous run
                self._timeseries_loaded = True  # Update flag for future calls
                return True
        except Exception:
            pass

        return False

    def _run_gradient(
        self,
        paradigm: str,
        queries: list[str],
        scenario: ScenarioConfig,
        source_dir: Path | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> GradientResult:
        """Run RAM gradient for a paradigm with 2-phase calibration protocol.

        Protocol (from PLAN.md):
        1. Phase 1 (Calibration): Find minimum viable RAM by descending
        2. Phase 2 (Gradient): Run performance gradient from minimum to plateau

        Args:
            paradigm: Paradigm ID
            queries: Query IDs
            scenario: Scenario config
            source_dir: Source data directory (for queries_params.yaml and calibration cache)
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

        # Set data path for queries_params.yaml loading
        if source_dir:
            executor.set_data_path(source_dir)

        def progress_wrapper(msg: str, current: int, total: int):
            console.print(f"    {msg} ({current}/{total})")
            if on_progress:
                on_progress(paradigm, msg, current / total)

        # Determine RAM levels to use
        ram_levels_mb = scenario.ram_levels_mb

        # Phase 1: RAM Calibration (unless skipped)
        if not scenario.skip_calibration and source_dir:
            minimum_viable_mb = self._get_or_calibrate_minimum_viable(
                executor=executor,
                paradigm=paradigm,
                source_dir=source_dir,
                force=scenario.force_calibration,
                max_mb=scenario.calibration_max_mb,
                min_mb=scenario.calibration_min_mb,
            )

            if minimum_viable_mb:
                # Phase 2: Build ascending gradient from minimum viable to plateau
                # Filter ram_levels to start from minimum viable (ascending order)
                ram_levels_mb = [
                    level for level in sorted(scenario.ram_levels_mb)
                    if level >= minimum_viable_mb
                ]
                if not ram_levels_mb:
                    # All levels below minimum viable - use only minimum
                    ram_levels_mb = [minimum_viable_mb]

                console.print(
                    f"    [dim]Gradient from {ram_levels_mb[0]}MB to {ram_levels_mb[-1]}MB "
                    f"(calibrated minimum: {minimum_viable_mb}MB)[/dim]"
                )

        return executor.run_gradient(
            queries=queries,
            levels_mb=ram_levels_mb,
            on_progress=progress_wrapper,
        )

    def _get_or_calibrate_minimum_viable(
        self,
        executor: RAMGradientExecutor,
        paradigm: str,
        source_dir: Path,
        force: bool = False,
        max_mb: int = 65536,
        min_mb: int = 512,
    ) -> int | None:
        """Get cached or run new RAM calibration for a paradigm.

        Args:
            executor: RAMGradientExecutor instance
            paradigm: Paradigm ID
            source_dir: Dataset directory (for calibration cache)
            force: Force re-calibration even if cached
            max_mb: Max RAM for calibration in MB
            min_mb: Min RAM for calibration in MB

        Returns:
            Minimum viable RAM in MB, or None if calibration skipped/failed
        """
        from ..ram.gradient import generate_calibration_levels

        paradigm = paradigm.upper()

        # Check if calibration is needed
        paradigms_needing_calibration = needs_calibration(
            source_dir, [paradigm], force=force
        )

        if not paradigms_needing_calibration:
            # Use cached value
            calibration = load_calibration(source_dir)
            if calibration:
                minimum_mb = calibration.get_minimum_viable(paradigm)
                if minimum_mb:
                    console.print(
                        f"    [dim]Using cached calibration: {minimum_mb}MB minimum viable[/dim]"
                    )
                    return minimum_mb

        # Generate calibration levels from max to min
        levels_tested = generate_calibration_levels(max_mb, min_mb)

        # Run calibration
        console.print(f"    [bold]Running RAM calibration for {paradigm} ({max_mb}MB → {min_mb}MB)...[/bold]")
        try:
            minimum_viable_mb = executor.calibrate_minimum_viable(
                levels_mb=levels_tested,
                test_query="Q1",
            )

            # Determine crash level (first level below minimum viable in tested levels)
            crash_level_mb = None
            for i, level in enumerate(levels_tested):
                if level < minimum_viable_mb:
                    crash_level_mb = level
                    break

            # Save to cache
            calibration = get_or_create_calibration(source_dir)
            calibration.set_calibration(
                paradigm=paradigm,
                minimum_viable_mb=minimum_viable_mb,
                levels_tested=levels_tested,
                crash_level_mb=crash_level_mb,
            )
            save_calibration(source_dir, calibration)

            return minimum_viable_mb

        except Exception as e:
            console.print(f"    [yellow]Calibration failed: {e}[/yellow]")
            return None

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

        raise ValueError(f"No config found for {paradigm}")

    def _get_timescale_config(self, paradigm: str) -> PostgresConfig | None:
        """Get TimescaleDB config for hybrid paradigms."""
        if paradigm != "M2":
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
        """Get all available query IDs in correct execution order.

        Order matters! Write queries (QW) must execute BEFORE their
        corresponding validation queries (Q35-Q41).

        Execution order:
        - Q1-Q23: Independent read queries
        - Q27-Q34: Independent read queries
        - QW1→Q35, QW2→Q36, ...: Write-then-validate pairs
        - QW9-QW12→Q39-Q41: Tenant write queries and validation
        """
        # Independent read queries (no dependencies)
        independent_reads = (
            [f"Q{i}" for i in range(1, 24)] +   # Q1-Q23
            [f"Q{i}" for i in range(27, 35)]    # Q27-Q34
        )

        # Write-then-validate pairs (order critical!)
        write_validation_pairs = (
            ["QW1", "Q35"] +                     # QW1 → Q35 (space reservation)
            ["QW2", "Q36"] +                     # QW2 → Q36 (metadata tag)
            ["QW3", "Q37"] +                     # QW3 → Q37 (relation mutation)
            ["QW4", "Q24"] +                     # QW4 → Q24 (maintenance event)
            ["QW5", "QW6", "Q25"] +              # QW5, QW6 → Q25 (calibration/firmware)
            ["QW7", "Q26"] +                     # QW7 → Q26 (capability)
            ["QW8", "Q38"] +                     # QW8 → Q38 (remove property)
            ["QW9", "Q39"] +                     # QW9 → Q39 (tenant move-in)
            ["QW10", "Q40"] +                    # QW10 → Q40 (tenant move-out)
            ["QW11", "QW12", "Q41"]              # QW11, QW12 → Q41 (space reassign/merge)
        )

        return independent_reads + write_validation_pairs

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
                # Fix: Distinguish OOM from ERROR
                pr = results.results.get(paradigm)
                if pr and any(l.status == "error" for l in pr.levels):
                    console.print(f"  {paradigm}: [red]ERROR (check logs)[/red]")
                else:
                    console.print(f"  {paradigm}: [red]All OOM[/red]")

        console.print("\n[cyan]RAM Baseline:[/cyan]")
        for paradigm, ram in summary["ram_baseline"].items():
            console.print(f"  {paradigm}: {ram:,.0f} MB")

        duration = (results.end_time - results.start_time).total_seconds() if results.end_time else 0
        console.print(f"\n[dim]Total duration: {duration:.0f}s[/dim]")
