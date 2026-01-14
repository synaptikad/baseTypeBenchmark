"""CLI for Benchmark Runner V3.

Modern Typer-based CLI with Rich output.
"""
from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .config import (
    EngineType,
    ParadigmStatus,
    DatasetProfile,
    ENGINE_PROFILES,
    DATASET_SIZE_ESTIMATES,
)
from .core.catalog import QueryCatalog, get_catalog
from .core.query import (
    DryRunResult,
    DryRunBatch,
    QueryDialect,
)

# Initialize CLI app
app = typer.Typer(
    name="btb-runner",
    help="Benchmark Runner V3 - Query execution and validation for BaseType Benchmark",
    add_completion=True,
    rich_markup_mode="rich",
)

# Rich console for output
console = Console()


# Status icons for paradigm matrix
STATUS_ICONS = {
    ParadigmStatus.NATIVE: "[green]N[/green]",
    ParadigmStatus.DEGRADED: "[yellow]D[/yellow]",
    ParadigmStatus.VERY_DEGRADED: "[cyan]V[/cyan]",
    ParadigmStatus.IMPOSSIBLE: "[red]X[/red]",
}


def _get_status_icon(status: ParadigmStatus) -> str:
    """Get Rich-formatted status icon."""
    return STATUS_ICONS.get(status, "[dim]?[/dim]")


def _validate_query(
    catalog: QueryCatalog,
    query_id: str,
    engine: EngineType,
) -> DryRunResult:
    """Validate a single query for dry-run."""
    query_def = catalog.get_query(query_id)

    if query_def is None:
        return DryRunResult(
            query_id=query_id,
            query_name="Unknown",
            engine=engine,
            can_execute=False,
            paradigm_status=ParadigmStatus.IMPOSSIBLE,
            issues=[f"Query {query_id} not found in catalog"],
        )

    status = query_def.get_status(engine)
    can_execute = query_def.can_execute(engine)

    result = DryRunResult(
        query_id=query_id,
        query_name=query_def.name,
        engine=engine,
        can_execute=can_execute,
        paradigm_status=status,
        query_parsed=True,  # Will be validated when we load query files
        parameters_valid=True,  # Parameters are validated at runtime from dataset
    )

    # Add notes from paradigm status
    status_info = query_def.paradigm_status.get(engine)
    if status_info and status_info.note:
        result.warnings.append(status_info.note)

    return result


@app.command("dry-run")
def dry_run(
    query: Annotated[
        Optional[str],
        typer.Option(
            "--query", "-q",
            help="Query ID to validate (e.g., Q1, Q7). If not specified, validates all."
        )
    ] = None,
    all_queries: Annotated[
        bool,
        typer.Option("--all", "-a", help="Validate all queries")
    ] = False,
    engine: Annotated[
        Optional[str],
        typer.Option(
            "--engine", "-e",
            help="Specific engine to validate (P1, P2, M1, M2)"
        )
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed validation info")
    ] = False,
    matrix: Annotated[
        bool,
        typer.Option("--matrix", "-m", help="Show paradigm support matrix")
    ] = False,
) -> None:
    """Validate queries without database connection.

    Checks query syntax, parameters, and paradigm compatibility.
    """
    console.print(Panel.fit(
        "[bold blue]Benchmark Runner V3[/bold blue] - Dry Run Mode",
        border_style="blue"
    ))

    # Load catalog
    try:
        catalog = get_catalog()
        catalog.load()
        console.print(f"[dim]Catalog version: {catalog.version}[/dim]")
    except Exception as e:
        console.print(f"[red]Error loading catalog: {e}[/red]")
        raise typer.Exit(1)

    # Determine which queries to validate
    if query:
        query_ids = [query.upper()]
    elif all_queries:
        query_ids = catalog.get_query_ids()
    else:
        # Default: show matrix
        matrix = True
        query_ids = catalog.get_query_ids()

    # Determine which engines to validate
    if engine:
        try:
            engines = [EngineType(engine.upper())]
        except ValueError:
            console.print(f"[red]Unknown engine: {engine}[/red]")
            console.print(f"Valid engines: {', '.join(e.value for e in EngineType)}")
            raise typer.Exit(1)
    else:
        engines = list(EngineType)

    # Show matrix view if requested
    if matrix:
        _show_paradigm_matrix(catalog, query_ids)
        return

    # Validate queries
    batch = DryRunBatch(catalog_version=catalog.version)

    for q_id in query_ids:
        for eng in engines:
            result = _validate_query(catalog, q_id, eng)
            batch.results.append(result)

    # Show results
    _show_dry_run_results(batch, verbose)

    # Summary
    console.print()
    console.print(Panel.fit(
        f"Total: {batch.total_queries} | "
        f"[green]Valid: {batch.valid_queries}[/green] | "
        f"[yellow]Executable: {batch.executable_queries}[/yellow] | "
        f"[red]Impossible: {batch.total_queries - batch.executable_queries}[/red]",
        title="Summary",
        border_style="blue"
    ))


def _show_paradigm_matrix(catalog: QueryCatalog, query_ids: list[str]) -> None:
    """Show paradigm support matrix."""
    table = Table(
        title="Paradigm Support Matrix",
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("Query", style="bold")
    table.add_column("Name", style="dim", max_width=30)
    for engine in EngineType:
        table.add_column(engine.value, justify="center", width=4)
    table.add_column("Category", style="dim")

    for query_id in query_ids:
        query_def = catalog.get_query(query_id)
        if query_def is None:
            continue

        row = [query_id, query_def.name]
        for engine in EngineType:
            status = query_def.get_status(engine)
            row.append(_get_status_icon(status))
        row.append(query_def.category.value)

        table.add_row(*row)

    console.print(table)

    # Legend
    console.print()
    legend = Text()
    legend.append("Legend: ")
    legend.append("N", style="green bold")
    legend.append("=Native  ")
    legend.append("D", style="yellow bold")
    legend.append("=Degraded  ")
    legend.append("V", style="cyan bold")
    legend.append("=Very Degraded  ")
    legend.append("X", style="red bold")
    legend.append("=Impossible")
    console.print(Panel.fit(legend, border_style="dim"))


def _show_dry_run_results(batch: DryRunBatch, verbose: bool) -> None:
    """Show dry-run validation results."""
    table = Table(
        title="Dry Run Validation Results",
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("Query", style="bold")
    table.add_column("Engine", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Valid", justify="center")
    if verbose:
        table.add_column("Issues/Warnings")

    for result in batch.results:
        status_icon = _get_status_icon(result.paradigm_status)
        valid_icon = "[green]OK[/green]" if result.is_valid else "[red]X[/red]"

        row = [
            result.query_id,
            result.engine.value,
            status_icon,
            valid_icon,
        ]

        if verbose:
            issues = result.issues + result.warnings
            issues_str = "; ".join(issues) if issues else "-"
            row.append(issues_str)

        table.add_row(*row)

    console.print(table)


@app.command("info")
def info(
    query: Annotated[
        str,
        typer.Argument(help="Query ID to show info for (e.g., Q1, Q7)")
    ],
) -> None:
    """Show detailed information about a query."""
    catalog = get_catalog()
    catalog.load()

    query_id = query.upper()
    query_def = catalog.get_query(query_id)

    if query_def is None:
        console.print(f"[red]Query {query_id} not found in catalog[/red]")
        raise typer.Exit(1)

    # Query info panel
    console.print(Panel.fit(
        f"[bold]{query_def.name}[/bold]\n\n"
        f"[dim]Category:[/dim] {query_def.category.value}\n"
        f"[dim]Intention:[/dim] {query_def.intention}\n"
        f"[dim]Use Case:[/dim] {query_def.use_case}",
        title=f"Query {query_id}",
        border_style="blue"
    ))

    # Parameters
    if query_def.parameters:
        param_table = Table(title="Parameters", show_header=True)
        param_table.add_column("Name")
        param_table.add_column("Type")
        param_table.add_column("Description")
        param_table.add_column("Example")

        for p in query_def.parameters:
            param_table.add_row(
                p.name,
                p.type,
                p.description,
                p.example or "-"
            )
        console.print(param_table)

    # Paradigm status
    status_table = Table(title="Paradigm Status", show_header=True)
    status_table.add_column("Engine")
    status_table.add_column("Status", justify="center")
    status_table.add_column("Note")

    for engine in EngineType:
        status = query_def.get_status(engine)
        status_info = query_def.paradigm_status.get(engine)
        note = status_info.note if status_info else ""
        status_table.add_row(
            engine.value,
            _get_status_icon(status),
            note
        )
    console.print(status_table)

    # Result schema
    if query_def.result_schema.columns:
        schema_table = Table(title="Result Schema", show_header=True)
        schema_table.add_column("Column")
        schema_table.add_column("Type")
        schema_table.add_column("Description")

        for col in query_def.result_schema.columns:
            schema_table.add_row(col.name, col.type, col.description)
        console.print(schema_table)


@app.command("profiles")
def show_profiles() -> None:
    """Show engine profiles and dataset sizes.

    Note: RAM requirements are measured via cgroups v2 during benchmark,
    not estimated. Run 'btb-runner benchmark' to get actual RAM_viable values.
    """
    console.print(Panel.fit(
        "[bold blue]Engine Profiles & Dataset Sizes[/bold blue]\n"
        "[dim]RAM measured via cgroups v2 - run benchmark for actual values[/dim]",
        border_style="blue"
    ))

    # Engine profiles
    engine_table = Table(title="Engine Profiles", show_header=True)
    engine_table.add_column("Engine")
    engine_table.add_column("In-Memory", justify="center")
    engine_table.add_column("Base Overhead")
    engine_table.add_column("TS in RAM", justify="center")
    engine_table.add_column("Can OOM", justify="center")

    for engine, profile in ENGINE_PROFILES.items():
        in_mem = "[green]Y[/green]" if profile.is_in_memory else "[dim]-[/dim]"
        ts_in_ram = "[yellow]Y[/yellow]" if profile.timeseries_in_memory else "[dim]-[/dim]"
        can_oom = "[red]![/red]" if profile.can_oom else "[green]OK[/green]"

        engine_table.add_row(
            engine.value,
            in_mem,
            f"{profile.base_overhead_mb} MB",
            ts_in_ram,
            can_oom
        )
    console.print(engine_table)

    # Dataset estimates
    dataset_table = Table(title="Dataset Size Estimates", show_header=True)
    dataset_table.add_column("Profile")
    dataset_table.add_column("Nodes")
    dataset_table.add_column("Edges")
    dataset_table.add_column("TS Rows")
    dataset_table.add_column("Raw Size")

    for key, estimate in DATASET_SIZE_ESTIMATES.items():
        dataset_table.add_row(
            key,
            f"{estimate.node_count:,}",
            f"{estimate.edge_count:,}",
            f"{estimate.timeseries_rows:,}",
            f"{estimate.total_mb:,} MB",
        )
    console.print(dataset_table)

    console.print("\n[dim]Run 'btb-runner benchmark -d <data_dir>' to measure actual RAM_viable[/dim]")


@app.command("run-query")
def run_query(
    query: Annotated[
        str,
        typer.Argument(help="Query ID to execute (e.g., Q1, Q7)")
    ],
    paradigm: Annotated[
        str,
        typer.Option(
            "--paradigm", "-p",
            help="Paradigm to use (P1, P2, M1, M2)"
        )
    ],
    params: Annotated[
        Optional[str],
        typer.Option("--params", help="Query parameters as JSON string")
    ] = None,
    timeout: Annotated[
        int,
        typer.Option("--timeout", "-t", help="Query timeout in seconds")
    ] = 300,
) -> None:
    """Execute a single query for debugging.

    Examples:
        btb-runner run-query Q1 -p P1
        btb-runner run-query Q7 -p M1 --params '{"meter_id": "meter_1"}'
    """
    import json
    from .runners import get_runner, get_hybrid_runner

    paradigm = paradigm.upper()
    query_id = query.upper()

    # Validate paradigm (O2 is exploratory only)
    if paradigm not in ("P1", "P2", "M1", "M2"):
        console.print(f"[red]Unknown paradigm: {paradigm}[/red]")
        console.print("[dim]Note: O2 (Oxigraph) is exploratory only[/dim]")
        raise typer.Exit(1)

    # Parse params
    query_params = {}
    if params:
        try:
            query_params = json.loads(params)
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON params: {e}[/red]")
            raise typer.Exit(1)

    console.print(Panel.fit(
        f"[bold blue]Run Query[/bold blue]\n\n"
        f"Query: {query_id}\n"
        f"Paradigm: {paradigm}\n"
        f"Params: {query_params or 'none'}",
        border_style="blue"
    ))

    # Get config and runner
    try:
        primary_config, ts_config = _get_loader_configs(paradigm)

        if paradigm in ("M2", "O2") and ts_config:
            runner = get_hybrid_runner(paradigm, primary_config, ts_config)
        else:
            runner = get_runner(paradigm, primary_config)

        if not runner.check_connection():
            console.print(f"[red]Cannot connect to {paradigm} database[/red]")
            raise typer.Exit(1)

        # Get query text (placeholder - would load from catalog)
        query_text = f"-- Query {query_id} placeholder"
        console.print(f"[dim]Query: {query_text[:100]}...[/dim]")

        # Execute
        import time
        start = time.perf_counter()
        result = runner.execute(query_text, query_params, float(timeout))
        duration = time.perf_counter() - start

        # Display results
        if result.status.value == "success":
            console.print(f"[green]Success[/green] - {result.row_count} rows in {result.duration_ms:.2f}ms")
            if result.rows:
                # Show first few rows
                table = Table(title=f"Results (first 5 of {result.row_count})")
                if result.rows:
                    for col in result.rows[0].keys():
                        table.add_column(col)
                    for row in result.rows[:5]:
                        table.add_row(*[str(v)[:50] for v in row.values()])
                console.print(table)
        else:
            console.print(f"[red]{result.status.value}[/red]: {result.error_message}")

        runner.close()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("benchmark")
def benchmark(
    source_dir: Annotated[
        Path,
        typer.Option("--source", "-s", help="Path to generated Parquet data (e.g., data/generated/small-1w)")
    ],
    export_dir: Annotated[
        Path,
        typer.Option("--export", "-e", help="Path for temporary exports")
    ] = Path("data/exports"),
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output JSON file")
    ] = Path("results.json"),
    scenario: Annotated[
        Optional[str],
        typer.Option("--scenario", "-S", help="Predefined scenario name or YAML file path")
    ] = None,
    paradigms: Annotated[
        Optional[str],
        typer.Option("--paradigms", "-p", help="Comma-separated paradigms (default: all)")
    ] = None,
    queries: Annotated[
        Optional[str],
        typer.Option("--queries", "-q", help="Comma-separated query IDs (default: all)")
    ] = None,
    ram_levels: Annotated[
        str,
        typer.Option("--ram", help="Comma-separated RAM levels in GB")
    ] = "128,64,32,16,8",
    runs: Annotated[
        int,
        typer.Option("--runs", "-r", help="Number of timed runs per query")
    ] = 10,
    variants: Annotated[
        int,
        typer.Option("--variants", "-v", help="Number of parameter variants")
    ] = 3,
    cleanup: Annotated[
        bool,
        typer.Option("--cleanup/--no-cleanup", help="Cleanup exports after each paradigm (saves disk)")
    ] = True,
    archive: Annotated[
        Optional[Path],
        typer.Option("--archive", "-a", help="Archive raw results to directory for replay")
    ] = None,
) -> None:
    """Execute full benchmark with RAM gradient and disk optimization.

    The benchmark exports, loads, and benchmarks each paradigm sequentially,
    optionally cleaning up exports after each paradigm to save disk space.

    With --archive, saves raw query results for later validation replay.

    Examples:
        btb-runner benchmark -s data/generated/small-1w -o results.json
        btb-runner benchmark -s data/generated/small-1w --scenario quick
        btb-runner benchmark -s data/generated/small-1w --scenario config/scenarios/custom.yaml
        btb-runner benchmark -s data/generated/small-1w -p P1,M1 --ram "32,16,8"
        btb-runner benchmark -s data/generated/small-1w --no-cleanup  # Keep exports
        btb-runner benchmark -s data/generated/small-1w --archive data/results/runs  # Save raw results
    """
    from .benchmark import BenchmarkOrchestrator, ScenarioConfig
    from .scenarios import get_scenario, load_scenario_from_yaml

    # Validate source directory (Parquet files)
    if not source_dir.exists():
        console.print(f"[red]Source directory not found: {source_dir}[/red]")
        raise typer.Exit(1)

    # Check for Parquet files
    if not (source_dir / "nodes.parquet").exists():
        console.print(f"[red]No nodes.parquet found in {source_dir}[/red]")
        console.print("[yellow]Hint: Use data/generated/<profile> directory[/yellow]")
        raise typer.Exit(1)

    # Ensure export directory exists
    export_dir.mkdir(parents=True, exist_ok=True)

    # Load scenario if specified
    if scenario:
        scenario_path = Path(scenario)
        if scenario_path.exists() and (scenario.endswith(".yaml") or scenario.endswith(".yml")):
            # Load from YAML file
            try:
                loaded_config = load_scenario_from_yaml(scenario_path)
                console.print(f"[dim]Loaded scenario from {scenario}[/dim]")
            except Exception as e:
                console.print(f"[red]Failed to load scenario: {e}[/red]")
                raise typer.Exit(1)
        else:
            # Load predefined scenario
            try:
                loaded_config = get_scenario(scenario)
                console.print(f"[dim]Using predefined scenario: {scenario}[/dim]")
            except ValueError as e:
                console.print(f"[red]{e}[/red]")
                console.print("[dim]Use 'btb-runner scenarios' to list available scenarios[/dim]")
                raise typer.Exit(1)

        # Use scenario values, but allow CLI overrides
        paradigm_list = loaded_config.paradigms
        query_list = loaded_config.queries
        ram_levels_mb = loaded_config.ram_levels_mb
        runs = loaded_config.n_runs
        variants = loaded_config.n_variants

        # CLI overrides take precedence
        if paradigms:
            paradigm_list = [p.strip().upper() for p in paradigms.split(",")]
        if queries:
            query_list = [q.strip().upper() for q in queries.split(",")]
        if ram_levels != "128,64,32,16,8":  # Not default
            ram_levels_mb = [int(float(r.strip()) * 1024) for r in ram_levels.split(",")]
    else:
        # Parse from CLI options
        paradigm_list = ["P1", "P2", "M1", "M2"]  # O2 is exploratory only
        if paradigms:
            paradigm_list = [p.strip().upper() for p in paradigms.split(",")]

        query_list = None
        if queries:
            query_list = [q.strip().upper() for q in queries.split(",")]

        ram_levels_mb = [int(float(r.strip()) * 1024) for r in ram_levels.split(",")]

    # Build configs
    configs = {}
    for p in paradigm_list:
        try:
            primary, ts = _get_loader_configs(p)
            configs[p] = primary
            if ts:
                configs["timescale"] = ts
        except Exception as e:
            console.print(f"[yellow]Warning: Cannot get config for {p}: {e}[/yellow]")

    # Create scenario config
    scenario = ScenarioConfig(
        paradigms=paradigm_list,
        queries=query_list,
        ram_levels_mb=ram_levels_mb,
        n_runs=runs,
        n_variants=variants,
    )

    disk_mode = "optimisé (cleanup)" if cleanup else "persistant"
    console.print(Panel.fit(
        f"[bold blue]Benchmark Configuration[/bold blue]\n\n"
        f"Source: {source_dir}\n"
        f"Paradigms: {', '.join(paradigm_list)}\n"
        f"Queries: {len(query_list) if query_list else 'all'}\n"
        f"RAM levels: {', '.join(f'{r}GB' for r in [r//1024 for r in ram_levels_mb])}\n"
        f"Runs: {runs}, Variants: {variants}\n"
        f"Disk mode: {disk_mode}\n"
        f"Output: {output}",
        border_style="blue"
    ))

    # Run benchmark with disk optimization
    try:
        orchestrator = BenchmarkOrchestrator(
            configs=configs,
            archive_path=archive,
        )
        results = orchestrator.run_full_benchmark(
            source_dir=source_dir,
            export_dir=export_dir,
            output_path=output,
            scenario=scenario,
            cleanup_exports=cleanup,
        )
        console.print(f"\n[green]Benchmark complete! Results saved to {output}[/green]")
        if archive:
            console.print(f"[green]Raw results archived to {archive}[/green]")
    except Exception as e:
        console.print(f"[red]Benchmark failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("gradient")
def gradient(
    paradigm: Annotated[
        str,
        typer.Argument(help="Paradigm to test (P1, P2, M1, M2)")
    ],
    data_dir: Annotated[
        Path,
        typer.Option("--data", "-d", help="Path to exported data directory")
    ],
    query: Annotated[
        str,
        typer.Option("--query", "-q", help="Query ID to test")
    ] = "Q1",
    ram_levels: Annotated[
        str,
        typer.Option("--ram", help="Comma-separated RAM levels in GB")
    ] = "32,16,8",
) -> None:
    """Test RAM gradient for a single paradigm.

    Quick test to find RAM_viable for a paradigm.

    Examples:
        btb-runner gradient M1 -d data/export --ram "32,16,8"
    """
    from .ram import IsolationManager, RAMGradientExecutor

    paradigm = paradigm.upper()

    # Validate (O2 is exploratory only)
    if paradigm not in ("P1", "P2", "M1", "M2"):
        console.print(f"[red]Unknown paradigm: {paradigm}[/red]")
        console.print("[dim]Note: O2 (Oxigraph) is exploratory only[/dim]")
        raise typer.Exit(1)

    if not data_dir.exists():
        console.print(f"[red]Data directory not found: {data_dir}[/red]")
        raise typer.Exit(1)

    # Parse RAM levels
    ram_levels_mb = [int(float(r.strip()) * 1024) for r in ram_levels.split(",")]

    console.print(Panel.fit(
        f"[bold blue]RAM Gradient Test[/bold blue]\n\n"
        f"Paradigm: {paradigm}\n"
        f"Query: {query}\n"
        f"RAM levels: {', '.join(f'{r}GB' for r in [r//1024 for r in ram_levels_mb])}",
        border_style="blue"
    ))

    try:
        # Get configs
        primary, ts = _get_loader_configs(paradigm)
        configs = {paradigm: primary}
        if ts:
            configs["timescale"] = ts

        # Setup isolation
        isolation = IsolationManager()

        # Create executor
        executor = RAMGradientExecutor(
            paradigm=paradigm,
            isolation=isolation,
            configs=configs,
            n_warmup=1,
            n_runs=3,
            n_variants=1,
        )

        # Run gradient
        def on_progress(msg: str, current: int, total: int):
            console.print(f"  {msg} ({current}/{total})")

        result = executor.run_gradient(
            queries=[query],
            levels_mb=ram_levels_mb,
            on_progress=on_progress,
        )

        # Display results
        console.print("\n[bold]Results:[/bold]")
        for level in result.levels:
            status_color = "green" if level.is_success else "red"
            console.print(
                f"  {level.limit_mb//1024}GB: [{status_color}]{level.status}[/{status_color}] "
                f"(peak: {level.actual_peak_mb:.0f}MB)"
            )

        if result.ram_viable_mb:
            console.print(f"\n[green]RAM viable: {result.ram_viable_mb//1024} GB[/green]")
        else:
            console.print("\n[red]All levels resulted in OOM[/red]")

    except Exception as e:
        console.print(f"[red]Gradient test failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("load")
def load(
    paradigm: Annotated[
        str,
        typer.Argument(help="Target paradigm (P1, P2, M1, M2)")
    ],
    data_dir: Annotated[
        Path,
        typer.Option("--data", "-d", help="Path to exported data directory")
    ],
    workers: Annotated[
        int,
        typer.Option("--workers", "-w", help="Number of parallel workers")
    ] = 16,
    clear: Annotated[
        bool,
        typer.Option("--clear", help="Clear database before loading")
    ] = False,
    dry_run_load: Annotated[
        bool,
        typer.Option("--dry-run", help="Show load plan without executing")
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Minimal output (no progress bars)")
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Verbose output with detailed logs")
    ] = False,
) -> None:
    """Load exported data into database.

    Optimized for massive datasets (1M+ rows).
    Supports parallel loading for timeseries.

    Examples:
        btb-runner load P1 -d data/export/p1
        btb-runner load M2 -d data/export/m1m2 -w 16 --clear
    """
    from .config import (
        PostgresConfig,
        MemgraphConfig,
        OxigraphConfig,
    )
    from .loaders import (
        get_loader,
        LoadProgressDisplay,
        LoadPhase,
        print_simple_result,
        verbose_callback,
    )

    paradigm = paradigm.upper()

    # Validate paradigm (O2 is exploratory only)
    if paradigm not in ("P1", "P2", "M1", "M2"):
        console.print(f"[red]Unknown paradigm: {paradigm}[/red]")
        console.print("Valid paradigms: P1, P2, M1, M2")
        console.print("[dim]Note: O2 (Oxigraph) is exploratory only[/dim]")
        raise typer.Exit(1)

    # Validate data directory
    if not data_dir.exists():
        console.print(f"[red]Data directory not found: {data_dir}[/red]")
        raise typer.Exit(1)

    # Dry-run: show plan
    if dry_run_load:
        _show_load_plan(paradigm, data_dir, workers)
        return

    # Get configuration (from environment or defaults)
    try:
        primary_config, timescale_config = _get_loader_configs(paradigm)
    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)

    # Create loader
    try:
        loader = get_loader(paradigm, primary_config, timescale_config)
    except Exception as e:
        console.print(f"[red]Loader creation failed: {e}[/red]")
        raise typer.Exit(1)

    # Check connection
    if not loader.check_connection():
        console.print(f"[red]Cannot connect to {paradigm} database[/red]")
        raise typer.Exit(1)

    # Clear database if requested
    if clear:
        console.print("[yellow]Clearing database...[/yellow]")
        if not loader.clear_database():
            console.print("[red]Failed to clear database[/red]")
            raise typer.Exit(1)
        console.print("[green]Database cleared[/green]")

    # Load data
    if quiet:
        # No progress, just final result
        result = loader.load_all(data_dir, progress_callback=None, workers=workers)
        print_simple_result(result)
    elif verbose:
        # Detailed logs
        result = loader.load_all(data_dir, progress_callback=verbose_callback, workers=workers)
        print_simple_result(result)
    else:
        # Interactive progress display
        with LoadProgressDisplay(paradigm) as display:
            # Add phases based on available files
            _setup_progress_phases(display, paradigm, data_dir)

            result = loader.load_all(
                data_dir,
                progress_callback=display.update,
                workers=workers,
            )
            display.print_summary(result)

    # Exit with error code if failed
    if not result.success:
        raise typer.Exit(1)


def _show_load_plan(paradigm: str, data_dir: Path, workers: int) -> None:
    """Show dry-run load plan."""
    console.print(Panel.fit(
        f"[bold blue]Load Plan - {paradigm}[/bold blue]",
        border_style="blue"
    ))

    table = Table(show_header=True)
    table.add_column("Phase", style="cyan")
    table.add_column("File", style="dim")
    table.add_column("Rows", justify="right")
    table.add_column("Status")

    # Check files based on paradigm
    files_to_check = _get_expected_files(paradigm)

    total_rows = 0
    for phase, filename in files_to_check:
        filepath = data_dir / filename
        if filepath.exists():
            # Count rows
            rows = _count_file_rows(filepath)
            total_rows += rows
            table.add_row(phase, filename, f"{rows:,}", "[green]Found[/green]")
        else:
            table.add_row(phase, filename, "-", "[dim]Not found[/dim]")

    console.print(table)

    console.print()
    console.print(f"[bold]Total rows:[/bold] {total_rows:,}")
    console.print(f"[bold]Workers:[/bold] {workers}")
    console.print()
    console.print("[dim]Run without --dry-run to execute load[/dim]")


def _get_expected_files(paradigm: str) -> list[tuple[str, str]]:
    """Get expected files for each paradigm."""
    if paradigm in ("P1", "P2"):
        return [
            ("Schema", "schema.sql"),
            ("Nodes", "nodes.csv"),
            ("Edges", "edges.csv"),
            ("Timeseries", "timeseries.csv"),
        ]
    elif paradigm in ("M1", "M2"):
        return [
            ("Schema", "schema_memgraph.cql"),
            ("Nodes", "nodes.csv"),
            ("Edges", "edges.csv"),
            ("Timeseries", "timeseries.csv"),
        ]
    elif paradigm == "O2":
        return [
            ("Ontology", "ontology.ttl"),
            ("RDF Data", "data.nt"),
            ("Timeseries", "timeseries.csv"),
        ]
    return []


def _count_file_rows(filepath: Path) -> int:
    """Count rows in a file."""
    if filepath.suffix == ".csv":
        with open(filepath, "r", encoding="utf-8") as f:
            return sum(1 for _ in f) - 1  # Exclude header
    elif filepath.suffix == ".nt":
        with open(filepath, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip() and not line.startswith("#"))
    return 0


def _get_loader_configs(paradigm: str):
    """Get loader configurations from environment or defaults.

    Builds proper DSN/URI strings for each database type.
    Port defaults match docker-compose.yml port mappings:
    - TimescaleDB: 5432:5432
    - Memgraph: 7688:7687 (host:container)
    - Oxigraph: 7878:7878
    """
    import os
    from .config import PostgresConfig, MemgraphConfig, OxigraphConfig

    timescale_config = None

    # Helper to build PostgreSQL DSN
    def build_pg_dsn(host: str, port: int, database: str, user: str, password: str) -> str:
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    if paradigm in ("P1", "P2"):
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = int(os.getenv("POSTGRES_PORT", "5432"))
        database = os.getenv("POSTGRES_DB", "benchmark")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        primary_config = PostgresConfig(
            dsn=build_pg_dsn(host, port, database, user, password)
        )
    elif paradigm in ("M1", "M2"):
        # Memgraph uses Bolt protocol - port 7688 on host maps to 7687 in container
        host = os.getenv("MEMGRAPH_HOST", "localhost")
        port = int(os.getenv("MEMGRAPH_PORT", "7688"))  # Host port from docker-compose
        user = os.getenv("MEMGRAPH_USER", "")
        password = os.getenv("MEMGRAPH_PASSWORD", "")

        uri = f"bolt://{host}:{port}"
        auth = (user, password) if user else None
        primary_config = MemgraphConfig(uri=uri, auth=auth)

        if paradigm == "M2":
            ts_host = os.getenv("TIMESCALE_HOST", "localhost")
            ts_port = int(os.getenv("TIMESCALE_PORT", "5432"))
            ts_database = os.getenv("TIMESCALE_DB", "benchmark")
            ts_user = os.getenv("TIMESCALE_USER", "postgres")
            ts_password = os.getenv("TIMESCALE_PASSWORD", "postgres")
            timescale_config = PostgresConfig(
                dsn=build_pg_dsn(ts_host, ts_port, ts_database, ts_user, ts_password)
            )
    elif paradigm == "O2":
        base_url = os.getenv("OXIGRAPH_URL", "http://localhost:7878")
        primary_config = OxigraphConfig(
            query_endpoint=f"{base_url}/query",
            update_endpoint=f"{base_url}/update",
        )
        ts_host = os.getenv("TIMESCALE_HOST", "localhost")
        ts_port = int(os.getenv("TIMESCALE_PORT", "5432"))
        ts_database = os.getenv("TIMESCALE_DB", "benchmark")
        ts_user = os.getenv("TIMESCALE_USER", "postgres")
        ts_password = os.getenv("TIMESCALE_PASSWORD", "postgres")
        timescale_config = PostgresConfig(
            dsn=build_pg_dsn(ts_host, ts_port, ts_database, ts_user, ts_password)
        )
    else:
        raise ValueError(f"Unknown paradigm: {paradigm}")

    return primary_config, timescale_config


def _setup_progress_phases(display, paradigm: str, data_dir: Path) -> None:
    """Setup progress display phases based on available files."""
    from .loaders import LoadPhase

    phase_num = 1

    # Schema phase (always)
    display.add_phase(LoadPhase.SCHEMA, 1, phase_num)
    phase_num += 1

    # Nodes
    nodes_file = data_dir / "nodes.csv"
    if paradigm == "O2":
        nodes_file = data_dir / "data.nt"

    if nodes_file.exists():
        count = _count_file_rows(nodes_file)
        display.add_phase(LoadPhase.NODES, count, phase_num)
        phase_num += 1

    # Edges (not for O2 - combined in data.nt)
    if paradigm != "O2":
        edges_file = data_dir / "edges.csv"
        if edges_file.exists():
            count = _count_file_rows(edges_file)
            display.add_phase(LoadPhase.EDGES, count, phase_num)
            phase_num += 1

    # Timeseries
    ts_file = data_dir / "timeseries.csv"
    if ts_file.exists():
        count = _count_file_rows(ts_file)
        display.add_phase(LoadPhase.TIMESERIES, count, phase_num)


# =============================================================================
# STATUS COMMAND
# =============================================================================

@app.command("status")
def status() -> None:
    """Show system status: Docker, datasets, exports, last run.

    Displays the current state of the benchmark environment.
    """
    import subprocess
    import os

    console.print(Panel.fit(
        "[bold blue]System Status[/bold blue]",
        border_style="blue"
    ))

    # Docker status
    console.print("\n[cyan]Docker Containers:[/cyan]")
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", "docker/docker-compose.yml", "ps", "--format", "table {{.Name}}\t{{.Status}}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                if "Up" in line or "running" in line.lower():
                    console.print(f"  [green]✓[/green] {line}")
                elif line.strip():
                    console.print(f"  [red]✗[/red] {line}")
        else:
            console.print("  [yellow]No containers found or docker-compose not configured[/yellow]")
    except Exception as e:
        console.print(f"  [red]Docker check failed: {e}[/red]")

    # Generated datasets
    console.print("\n[cyan]Generated Datasets:[/cyan]")
    data_dir = Path(os.environ.get("BTB_DATA_DIR", "data"))
    generated_dir = data_dir / "generated"
    if generated_dir.exists():
        datasets = list(generated_dir.glob("*"))
        datasets = [d for d in datasets if d.is_dir() and (d / "nodes.parquet").exists()]
        if datasets:
            for ds in sorted(datasets):
                size_mb = sum(f.stat().st_size for f in ds.rglob("*") if f.is_file()) / 1024 / 1024
                console.print(f"  [green]✓[/green] {ds.name} ({size_mb:.1f} MB)")
        else:
            console.print("  [dim]No datasets generated[/dim]")
    else:
        console.print("  [dim]No generated directory[/dim]")

    # Exports
    console.print("\n[cyan]Exports:[/cyan]")
    export_dir = data_dir / "exports"
    paradigms = ["p1", "p2", "m1", "m2"]  # O2 is exploratory only
    for p in paradigms:
        p_dir = export_dir / p
        if p_dir.exists() and list(p_dir.glob("*")):
            console.print(f"  [green]✓[/green] {p.upper()}")
        else:
            console.print(f"  [dim]✗[/dim] {p.upper()}")

    # Last result
    console.print("\n[cyan]Last Result:[/cyan]")
    results_dir = data_dir / "results"
    if results_dir.exists():
        results = sorted(results_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if results:
            last = results[0]
            mtime = last.stat().st_mtime
            from datetime import datetime
            dt = datetime.fromtimestamp(mtime)
            console.print(f"  [green]✓[/green] {last.name} ({dt.strftime('%Y-%m-%d %H:%M')})")
        else:
            console.print("  [dim]No results yet[/dim]")
    else:
        console.print("  [dim]No results directory[/dim]")


# =============================================================================
# GENERATE COMMAND
# =============================================================================

@app.command("generate")
def generate(
    profile: Annotated[
        str,
        typer.Option("--profile", "-p", help="Dataset profile (small, medium, large)")
    ] = "small",
    duration: Annotated[
        str,
        typer.Option("--duration", "-d", help="Time duration (2d, 1w, 1m, 6m, 1y)")
    ] = "1w",
    seed: Annotated[
        int,
        typer.Option("--seed", "-s", help="Random seed for reproducibility")
    ] = 42,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output directory")
    ] = None,
) -> None:
    """Generate synthetic dataset.

    Creates Parquet files (nodes, edges, timeseries) for benchmarking.

    Examples:
        btb-runner generate --profile small --duration 1w
        btb-runner generate --profile medium --seed 123
    """
    import subprocess
    import os

    console.print(Panel.fit(
        f"[bold blue]Generate Dataset[/bold blue]\n\n"
        f"Profile: {profile}\n"
        f"Duration: {duration}\n"
        f"Seed: {seed}",
        border_style="blue"
    ))

    # Build command
    data_dir = Path(os.environ.get("BTB_DATA_DIR", "data"))
    output_dir = output or data_dir / "generated"

    cmd = [
        sys.executable, "-m", "src.basetype_benchmark.dataset.generator",
        "--profile", profile,
        "--duration", duration,
        "--seed", str(seed),
        "--output", str(output_dir),
        "--format", "parquet",
    ]

    console.print(f"\n[dim]$ {' '.join(cmd)}[/dim]\n")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        console.print("[red]Generation failed[/red]")
        raise typer.Exit(1)

    console.print(f"\n[green]Dataset generated: {output_dir}/{profile}-{duration}[/green]")


# =============================================================================
# EXPORT COMMAND
# =============================================================================

@app.command("export")
def export_cmd(
    paradigm: Annotated[
        str,
        typer.Argument(help="Target paradigm (P1, P2, M1, M2)")
    ],
    source: Annotated[
        Path,
        typer.Option("--source", "-s", help="Source Parquet directory")
    ],
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output directory")
    ] = None,
) -> None:
    """Export Parquet data to paradigm format.

    Converts generated Parquet files to the format required by each paradigm.

    Examples:
        btb-runner export P1 -s data/generated/small-1w
        btb-runner export M1 -s data/generated/small-1w -o data/exports/m1
    """
    import subprocess
    import os

    paradigm = paradigm.upper()

    # Map paradigm to exporter module
    exporter_modules = {
        "P1": "src.basetype_benchmark.exporters.p1_extractor",
        "P2": "src.basetype_benchmark.exporters.p2_extractor",
        "M1": "src.basetype_benchmark.exporters.m1m2_extractor",
        "M2": "src.basetype_benchmark.exporters.m1m2_extractor",
        "O2": "src.basetype_benchmark.exporters.o2_extractor",
    }

    if paradigm not in exporter_modules:
        console.print(f"[red]Unknown paradigm: {paradigm}[/red]")
        console.print(f"Valid paradigms: {', '.join(exporter_modules.keys())}")
        raise typer.Exit(1)

    if not source.exists():
        console.print(f"[red]Source directory not found: {source}[/red]")
        raise typer.Exit(1)

    console.print(Panel.fit(
        f"[bold blue]Export to {paradigm}[/bold blue]\n\n"
        f"Source: {source}",
        border_style="blue"
    ))

    # Determine output directory
    data_dir = Path(os.environ.get("BTB_DATA_DIR", "data"))
    output_dir = output or data_dir / "exports" / paradigm.lower() / source.name
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", exporter_modules[paradigm],
        "--input", str(source),
        "--output", str(output_dir),
    ]

    console.print(f"\n[dim]$ {' '.join(cmd)}[/dim]\n")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        console.print(f"[red]Export failed for {paradigm}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[green]Exported to {output_dir}[/green]")


# =============================================================================
# VALIDATE COMMAND
# =============================================================================

@app.command("validate")
def validate_cmd(
    results_file: Annotated[
        Path,
        typer.Argument(help="Path to results.json from benchmark run")
    ],
    reference: Annotated[
        str,
        typer.Option("--reference", "-r", help="Reference paradigm (ground truth)")
    ] = "P1",
    tolerance: Annotated[
        float,
        typer.Option("--tolerance", "-t", help="Float comparison tolerance (relative)")
    ] = 0.01,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output JSON report file")
    ] = None,
    html: Annotated[
        Optional[Path],
        typer.Option("--html", help="Output HTML report (legacy)")
    ] = None,
    md: Annotated[
        Optional[Path],
        typer.Option("--md", help="Output Markdown report (recommended)")
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed diff information")
    ] = False,
    fail_on_mismatch: Annotated[
        bool,
        typer.Option("--fail-on-mismatch", help="Exit with code 1 if any mismatch found")
    ] = False,
    cross_matrix: Annotated[
        bool,
        typer.Option("--cross-matrix", "-x", help="Compare all paradigm pairs (not just vs reference)")
    ] = False,
    semantic: Annotated[
        bool,
        typer.Option("--semantic/--no-semantic", help="Enable semantic validation (compares INFORMATION, not rows)")
    ] = True,
) -> None:
    """Validate query results across paradigms.

    Compares all paradigms against a reference (default: P1) to verify
    semantic equivalence of query results.

    This command is essential for academic validation - it ensures that
    different database paradigms return equivalent results for the same queries.

    With --semantic (default), uses semantic rules to compare the INFORMATION
    returned by queries, not just row counts. This catches bugs like Q1 where
    P1 includes the source meter but M1/O2 don't.

    Examples:
        btb-runner validate results.json
        btb-runner validate results.json --reference P1 --verbose
        btb-runner validate results.json -o validation_report.json
        btb-runner validate results.json --html docs/validation.html --fail-on-mismatch
        btb-runner validate results.json --cross-matrix  # Compare all pairs
        btb-runner validate results.json --no-semantic   # Row-based only
    """
    from .core.cross_validator import CrossParadigmValidator, ValidationStatus, CrossValidationMatrix
    from .benchmark.results import BenchmarkResults

    # Validate input file
    if not results_file.exists():
        console.print(f"[red]Results file not found: {results_file}[/red]")
        raise typer.Exit(1)

    console.print(Panel.fit(
        "[bold blue]Cross-Paradigm Validation[/bold blue]\n\n"
        f"Results: {results_file}\n"
        f"Reference: {reference}\n"
        f"Tolerance: {tolerance:.1%}",
        border_style="blue"
    ))

    # Load results
    try:
        results = BenchmarkResults.from_json(results_file)
        console.print(f"[dim]Loaded benchmark: {results.benchmark_id}[/dim]")
    except Exception as e:
        console.print(f"[red]Failed to load results: {e}[/red]")
        raise typer.Exit(1)

    # Validate reference paradigm exists (only for non-matrix mode)
    if not cross_matrix and reference not in results.results:
        console.print(f"[red]Reference paradigm '{reference}' not found in results[/red]")
        console.print(f"Available paradigms: {', '.join(results.results.keys())}")
        raise typer.Exit(1)

    # Setup semantic definitions path
    semantic_path = None
    if semantic:
        # Try multiple locations
        semantic_path = Path(__file__).parent.parent.parent / "config" / "semantic_definitions.yaml"
        if not semantic_path.exists():
            semantic_path = Path("config/semantic_definitions.yaml")
        if not semantic_path.exists():
            console.print("[yellow]Warning: semantic_definitions.yaml not found, falling back to row-based validation[/yellow]")
            semantic_path = None
        else:
            console.print(f"[dim]Semantic validation enabled: {semantic_path}[/dim]")

    # Find query parameters file from data profile
    query_params_path = None
    if results.config and results.config.data_profile:
        # Try to find queries_params.yaml in the dataset directory
        data_profile = results.config.data_profile
        # Try multiple locations
        for base in [Path("data/generated"), Path(__file__).parent.parent.parent / "data" / "generated"]:
            candidate = base / data_profile / "queries_params.yaml"
            if candidate.exists():
                query_params_path = candidate
                console.print(f"[dim]Query params loaded: {query_params_path}[/dim]")
                break

    # Run validation
    try:
        validator = CrossParadigmValidator(
            reference=reference,
            float_tolerance=tolerance,
            semantic_definitions_path=semantic_path,
            query_params_path=query_params_path,
        )

        if cross_matrix:
            # Cross-validation matrix mode
            matrix = validator.validate_matrix(results)
            _display_cross_matrix(matrix, verbose)

            # Save reports
            if output:
                matrix.to_json(output)
                console.print(f"\n[green]JSON matrix report saved to {output}[/green]")

            if html:
                _generate_matrix_html_report(matrix, html)
                console.print(f"[green]HTML matrix report saved to {html}[/green]")

            if md:
                _generate_matrix_md_report(matrix, md)
                console.print(f"[green]Markdown matrix report saved to {md}[/green]")

            # Check for mismatches (matrix is now asymmetric, count unique pairs)
            total_mismatch = sum(
                dc.mismatch
                for ref_map in matrix.matrix.values()
                for dc in ref_map.values()
            ) // 2  # Divide by 2 because A→B and B→A count same mismatches

            if fail_on_mismatch and total_mismatch > 0:
                console.print(f"\n[red]Validation failed: {total_mismatch} mismatches found[/red]")
                raise typer.Exit(1)

            console.print(f"\n[green]Cross-matrix validation complete![/green]")
            return

        report = validator.validate(results)
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        raise typer.Exit(1)

    # Display summary table
    console.print("\n")
    summary_table = Table(title="Validation Summary", show_header=True)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Count", justify="right")
    summary_table.add_column("Percentage", justify="right")

    total = report.total_queries * len(report.compared_paradigms)
    if total > 0:
        summary_table.add_row(
            "Equivalent",
            str(report.equivalent_count),
            f"[green]{100*report.equivalent_count/total:.1f}%[/green]"
        )
        summary_table.add_row(
            "Degraded",
            str(report.degraded_count),
            f"[yellow]{100*report.degraded_count/total:.1f}%[/yellow]"
        )
        summary_table.add_row(
            "Skip",
            str(report.skip_count),
            f"[dim]{100*report.skip_count/total:.1f}%[/dim]"
        )
        summary_table.add_row(
            "Mismatch",
            str(report.mismatch_count),
            f"[red]{100*report.mismatch_count/total:.1f}%[/red]"
        )
    console.print(summary_table)

    # Display per-query results
    console.print("\n")
    query_table = Table(title="Query Results", show_header=True)
    query_table.add_column("Query", style="bold")
    for paradigm in report.compared_paradigms:
        query_table.add_column(paradigm, justify="center")

    status_icons = {
        ValidationStatus.EQUIVALENT: "[green]≡[/green]",
        ValidationStatus.DEGRADED: "[yellow]D[/yellow]",
        ValidationStatus.SKIP: "[dim]–[/dim]",
        ValidationStatus.MISMATCH: "[red]✗[/red]",
        ValidationStatus.NO_DATA: "[dim]?[/dim]",
    }

    for query_id in sorted(report.comparisons.keys()):
        row = [query_id]
        for paradigm in report.compared_paradigms:
            if paradigm in report.comparisons[query_id]:
                cmp = report.comparisons[query_id][paradigm]
                row.append(status_icons.get(cmp.status, "?"))
            else:
                row.append("[dim]–[/dim]")
        query_table.add_row(*row)

    console.print(query_table)

    # Legend
    console.print("\n")
    legend = Text()
    legend.append("Legend: ")
    legend.append("≡", style="green bold")
    legend.append("=Equivalent  ")
    legend.append("D", style="yellow bold")
    legend.append("=Degraded  ")
    legend.append("–", style="dim")
    legend.append("=Skip  ")
    legend.append("✗", style="red bold")
    legend.append("=Mismatch")
    console.print(Panel.fit(legend, border_style="dim"))

    # Show verbose details for mismatches
    if verbose and report.mismatch_count > 0:
        console.print("\n[bold red]Mismatches:[/bold red]\n")
        for query_id, paradigm_results in report.comparisons.items():
            for paradigm, cmp in paradigm_results.items():
                if cmp.status == ValidationStatus.MISMATCH:
                    console.print(f"  [bold]{query_id}[/bold] vs {paradigm}:")
                    console.print(f"    Row count: {cmp.row_count_ref} vs {cmp.row_count_cmp}")
                    if cmp.reason:
                        console.print(f"    Reason: {cmp.reason}")
                    if cmp.diffs:
                        console.print(f"    First diff: {cmp.diffs[0]}")
                    console.print()

    # Show degraded reasons if verbose
    if verbose and report.degraded_count > 0:
        console.print("\n[bold yellow]Degraded Queries:[/bold yellow]\n")
        for query_id, paradigm_results in report.comparisons.items():
            for paradigm, cmp in paradigm_results.items():
                if cmp.status == ValidationStatus.DEGRADED:
                    console.print(f"  [bold]{query_id}[/bold] ({paradigm}): {cmp.reason}")

    # Save JSON report
    if output:
        try:
            report.to_json(output)
            console.print(f"\n[green]JSON report saved to {output}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to save JSON report: {e}[/red]")

    # Generate HTML report
    if html:
        try:
            _generate_html_report(report, html)
            console.print(f"[green]HTML report saved to {html}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to generate HTML report: {e}[/red]")

    # Generate Markdown report
    if md:
        try:
            _generate_md_report(report, md)
            console.print(f"[green]Markdown report saved to {md}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to generate Markdown report: {e}[/red]")

    # Exit code
    if fail_on_mismatch and report.mismatch_count > 0:
        console.print(f"\n[red]Validation failed: {report.mismatch_count} mismatches found[/red]")
        raise typer.Exit(1)

    console.print(f"\n[green]Validation complete![/green]")


def _display_cross_matrix(matrix, verbose: bool = False) -> None:
    """Display asymmetric cross-validation matrix in terminal.

    Row = Reference paradigm (ground truth)
    Column = Compared paradigm
    Cell = What the compared paradigm lacks vs reference
    """
    from .core.cross_validator import ValidationStatus

    console.print("\n")

    # Explanation
    console.print("[dim]Matrix reads: Row→Column = what Column lacks when Row is reference[/dim]\n")

    # Create coverage rate matrix table (asymmetric)
    matrix_table = Table(
        title="Cross-Validation Matrix (Row=Ref → Column=Cmp)",
        show_header=True,
        header_style="bold"
    )
    matrix_table.add_column("Ref↓ Cmp→", style="bold cyan")
    for paradigm in matrix.paradigms:
        matrix_table.add_column(paradigm, justify="center")

    for ref in matrix.paradigms:
        row = [ref]
        for cmp in matrix.paradigms:
            if ref == cmp:
                row.append("[dim]—[/dim]")
            else:
                dc = matrix.matrix.get(ref, {}).get(cmp)
                if dc:
                    # Show: equivalent / (total - impossible_in_ref)
                    answerable = dc.total - dc.impossible_in_ref
                    if answerable > 0:
                        rate = dc.coverage_rate
                        lacks = dc.impossible_in_cmp + dc.degraded
                        if rate >= 95:
                            color = "green"
                        elif rate >= 80:
                            color = "yellow"
                        else:
                            color = "red"
                        # Show rate and what's missing
                        if lacks > 0:
                            row.append(f"[{color}]{dc.equivalent}[/{color}][dim]/{answerable}[/dim] [yellow]-{lacks}[/yellow]")
                        else:
                            row.append(f"[{color}]{dc.equivalent}/{answerable}[/{color}]")
                    else:
                        row.append("[dim]n/a[/dim]")
                else:
                    row.append("[dim]—[/dim]")
        matrix_table.add_row(*row)

    console.print(matrix_table)
    console.print("[dim]Format: equivalent/answerable [yellow]-lacks[/yellow] (impossible_in_cmp + degraded)[/dim]")

    # Show detailed directional stats table
    console.print("\n")
    stats_table = Table(title="Directional Comparison (Ref → Cmp)", show_header=True)
    stats_table.add_column("Direction", style="cyan")
    stats_table.add_column("≡", justify="right", style="green", header_style="green")
    stats_table.add_column("Deg", justify="right", style="yellow", header_style="yellow")
    stats_table.add_column("Cmp✗", justify="right", style="red", header_style="red")
    stats_table.add_column("Ref✗", justify="right", style="dim", header_style="dim")
    stats_table.add_column("Mis", justify="right", style="red bold", header_style="red bold")
    stats_table.add_column("Cover%", justify="right")

    for ref in matrix.paradigms:
        for cmp, dc in matrix.matrix.get(ref, {}).items():
            rate = dc.coverage_rate
            if rate >= 95:
                rate_str = f"[green]{rate:.0f}%[/green]"
            elif rate >= 80:
                rate_str = f"[yellow]{rate:.0f}%[/yellow]"
            else:
                rate_str = f"[red]{rate:.0f}%[/red]"

            stats_table.add_row(
                f"{ref} → {cmp}",
                str(dc.equivalent),
                str(dc.degraded),
                str(dc.impossible_in_cmp),
                str(dc.impossible_in_ref),
                str(dc.mismatch),
                rate_str,
            )

    console.print(stats_table)
    console.print("[dim]≡=Equivalent  Deg=Degraded  Cmp✗=Impossible in Compared  Ref✗=Impossible in Ref  Mis=Mismatch[/dim]")

    # Verbose: show mismatches per direction
    if verbose:
        has_mismatches = False
        for qid, ref_map in matrix.query_details.items():
            for ref, cmp_map in ref_map.items():
                for cmp, comparison in cmp_map.items():
                    if comparison.status == ValidationStatus.MISMATCH:
                        if not has_mismatches:
                            console.print("\n[bold red]Mismatches:[/bold red]\n")
                            has_mismatches = True
                        console.print(f"  [bold]{qid}[/bold] ({ref} → {cmp}):")
                        console.print(f"    Row count: {comparison.row_count_ref} vs {comparison.row_count_cmp}")
                        if comparison.reason:
                            console.print(f"    Reason: {comparison.reason}")


def _generate_matrix_html_report(matrix, output_path: Path) -> None:
    """Generate HTML report for asymmetric cross-validation matrix."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cross-Validation Matrix Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1400px; margin: 0 auto; padding: 20px; }}
        h1, h2 {{ color: #1a1a2e; }}
        .matrix-container {{ overflow-x: auto; }}
        table {{ border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px 12px; text-align: center; border: 1px solid #dee2e6; }}
        th {{ background: #343a40; color: white; }}
        .rate-high {{ background: #d4edda; color: #155724; }}
        .rate-medium {{ background: #fff3cd; color: #856404; }}
        .rate-low {{ background: #f8d7da; color: #721c24; }}
        .diagonal {{ background: #e9ecef; color: #6c757d; }}
        .lacks {{ color: #dc3545; font-size: 0.85em; }}
        .note {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; font-size: 0.9em; color: #6c757d; }}
        .footer {{ margin-top: 30px; text-align: center; color: #6c757d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>Cross-Validation Matrix Report</h1>
    <p><strong>Benchmark:</strong> {matrix.benchmark_id}</p>
    <p><strong>Paradigms:</strong> {', '.join(matrix.paradigms)}</p>
    <p><strong>Timestamp:</strong> {matrix.timestamp.isoformat()}</p>

    <div class="note">
        <strong>How to read:</strong> Row = Reference (ground truth), Column = Compared paradigm.<br>
        Cell shows: <code>equivalent/answerable</code> <span class="lacks">-lacks</span> (queries Column cannot answer)
    </div>

    <h2>Coverage Matrix (Row → Column)</h2>
    <div class="matrix-container">
        <table>
            <tr>
                <th>Ref↓ Cmp→</th>
"""

    # Header row
    for p in matrix.paradigms:
        html_content += f"                <th>{p}</th>\n"
    html_content += "            </tr>\n"

    # Data rows (asymmetric)
    for ref in matrix.paradigms:
        html_content += f"            <tr>\n                <th>{ref}</th>\n"
        for cmp in matrix.paradigms:
            if ref == cmp:
                html_content += '                <td class="diagonal">—</td>\n'
            else:
                dc = matrix.matrix.get(ref, {}).get(cmp)
                if dc:
                    answerable = dc.total - dc.impossible_in_ref
                    lacks = dc.impossible_in_cmp + dc.degraded
                    rate = dc.coverage_rate
                    if rate >= 95:
                        css_class = "rate-high"
                    elif rate >= 80:
                        css_class = "rate-medium"
                    else:
                        css_class = "rate-low"
                    lacks_html = f' <span class="lacks">-{lacks}</span>' if lacks > 0 else ''
                    html_content += f'                <td class="{css_class}">{dc.equivalent}/{answerable}{lacks_html}</td>\n'
                else:
                    html_content += '                <td class="diagonal">—</td>\n'
        html_content += "            </tr>\n"

    html_content += """        </table>
    </div>

    <h2>Directional Statistics (Ref → Cmp)</h2>
    <table>
        <tr>
            <th>Direction</th>
            <th>Equivalent</th>
            <th>Degraded</th>
            <th>Cmp Impossible</th>
            <th>Ref Impossible</th>
            <th>Mismatch</th>
            <th>Coverage</th>
        </tr>
"""

    for ref in matrix.paradigms:
        for cmp, dc in matrix.matrix.get(ref, {}).items():
            rate = dc.coverage_rate
            if rate >= 95:
                css_class = "rate-high"
            elif rate >= 80:
                css_class = "rate-medium"
            else:
                css_class = "rate-low"

            html_content += f"""        <tr>
            <td><strong>{ref} → {cmp}</strong></td>
            <td>{dc.equivalent}</td>
            <td>{dc.degraded}</td>
            <td>{dc.impossible_in_cmp}</td>
            <td>{dc.impossible_in_ref}</td>
            <td>{dc.mismatch}</td>
            <td class="{css_class}">{rate:.0f}%</td>
        </tr>
"""

    html_content += """    </table>

    <div class="footer">
        <p>Generated by BaseType Benchmark V3</p>
    </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def _generate_html_report(report, output_path: Path) -> None:
    """Generate HTML validation report for publication."""
    from .core.cross_validator import ValidationStatus

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cross-Paradigm Validation Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #1a1a2e; }}
        .summary {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
        .summary-item {{ text-align: center; padding: 15px; border-radius: 6px; }}
        .equivalent {{ background: #d4edda; color: #155724; }}
        .degraded {{ background: #fff3cd; color: #856404; }}
        .skip {{ background: #e9ecef; color: #6c757d; }}
        .mismatch {{ background: #f8d7da; color: #721c24; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: center; border: 1px solid #dee2e6; }}
        th {{ background: #343a40; color: white; }}
        .status-eq {{ color: #28a745; font-weight: bold; }}
        .status-deg {{ color: #ffc107; font-weight: bold; }}
        .status-skip {{ color: #6c757d; }}
        .status-mis {{ color: #dc3545; font-weight: bold; }}
        .footer {{ margin-top: 30px; text-align: center; color: #6c757d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>Cross-Paradigm Validation Report</h1>
    <p><strong>Benchmark:</strong> {report.benchmark_id}</p>
    <p><strong>Reference Paradigm:</strong> {report.reference_paradigm}</p>
    <p><strong>Timestamp:</strong> {report.timestamp.isoformat()}</p>

    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-grid">
            <div class="summary-item equivalent">
                <div style="font-size: 2em;">{report.equivalent_count}</div>
                <div>Equivalent</div>
            </div>
            <div class="summary-item degraded">
                <div style="font-size: 2em;">{report.degraded_count}</div>
                <div>Degraded</div>
            </div>
            <div class="summary-item skip">
                <div style="font-size: 2em;">{report.skip_count}</div>
                <div>Skip</div>
            </div>
            <div class="summary-item mismatch">
                <div style="font-size: 2em;">{report.mismatch_count}</div>
                <div>Mismatch</div>
            </div>
        </div>
    </div>

    <h2>Query Results</h2>
    <table>
        <thead>
            <tr>
                <th>Query</th>
                {"".join(f'<th>{p}</th>' for p in report.compared_paradigms)}
            </tr>
        </thead>
        <tbody>
"""

    status_classes = {
        ValidationStatus.EQUIVALENT: ("status-eq", "≡"),
        ValidationStatus.DEGRADED: ("status-deg", "D"),
        ValidationStatus.SKIP: ("status-skip", "–"),
        ValidationStatus.MISMATCH: ("status-mis", "✗"),
        ValidationStatus.NO_DATA: ("status-skip", "?"),
    }

    for query_id in sorted(report.comparisons.keys()):
        html_content += f"            <tr><td><strong>{query_id}</strong></td>"
        for paradigm in report.compared_paradigms:
            if paradigm in report.comparisons[query_id]:
                cmp = report.comparisons[query_id][paradigm]
                css_class, symbol = status_classes.get(cmp.status, ("", "?"))
                title = cmp.reason or cmp.status.value
                html_content += f'<td class="{css_class}" title="{title}">{symbol}</td>'
            else:
                html_content += '<td class="status-skip">–</td>'
        html_content += "</tr>\n"

    html_content += f"""        </tbody>
    </table>

    <h2>Legend</h2>
    <ul>
        <li><span class="status-eq">≡</span> Equivalent - Results match within tolerance</li>
        <li><span class="status-deg">D</span> Degraded - Known limitation, acceptable difference</li>
        <li><span class="status-skip">–</span> Skip - Query impossible for this paradigm</li>
        <li><span class="status-mis">✗</span> Mismatch - Unexpected difference</li>
    </ul>

    <div class="footer">
        <p>Generated by BaseType Benchmark V3 - Cross-Paradigm Validation System</p>
        <p>Reference: {report.reference_paradigm} | Total Queries: {report.total_queries}</p>
    </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def _generate_matrix_md_report(matrix, output_path: Path) -> None:
    """Generate Markdown report for asymmetric cross-validation matrix."""
    lines = [
        "# Cross-Validation Matrix Report",
        "",
        f"**Benchmark:** {matrix.benchmark_id}",
        f"**Paradigms:** {', '.join(matrix.paradigms)}",
        f"**Timestamp:** {matrix.timestamp.isoformat()}",
        "",
        "> **How to read:** Row = Reference (ground truth), Column = Compared paradigm.",
        "> Cell shows: `equivalent/answerable` (-lacks queries Column cannot answer)",
        "",
        "## Coverage Matrix (Row → Column)",
        "",
    ]

    # Header row
    header = "| Ref↓ Cmp→ |"
    separator = "|-----------|"
    for p in matrix.paradigms:
        header += f" {p} |"
        separator += "------|"
    lines.append(header)
    lines.append(separator)

    # Data rows (asymmetric)
    for ref in matrix.paradigms:
        row = f"| **{ref}** |"
        for cmp in matrix.paradigms:
            if ref == cmp:
                row += " — |"
            else:
                dc = matrix.matrix.get(ref, {}).get(cmp)
                if dc:
                    answerable = dc.total - dc.impossible_in_ref
                    lacks = dc.impossible_in_cmp + dc.degraded
                    lacks_str = f" -{lacks}" if lacks > 0 else ""
                    row += f" {dc.equivalent}/{answerable}{lacks_str} |"
                else:
                    row += " — |"
        lines.append(row)

    lines.extend([
        "",
        "## Directional Statistics (Ref → Cmp)",
        "",
        "| Direction | Equiv | Degr | Cmp Imposs | Ref Imposs | Mismatch | Coverage |",
        "|-----------|-------|------|------------|------------|----------|----------|",
    ])

    for ref in matrix.paradigms:
        for cmp, dc in matrix.matrix.get(ref, {}).items():
            rate = dc.coverage_rate
            lines.append(
                f"| {ref} → {cmp} | {dc.equivalent} | {dc.degraded} | "
                f"{dc.impossible_in_cmp} | {dc.impossible_in_ref} | {dc.mismatch} | {rate:.0f}% |"
            )

    lines.extend([
        "",
        "---",
        "*Generated by BaseType Benchmark V3*",
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _generate_md_report(report, output_path: Path) -> None:
    """Generate Markdown validation report."""
    from .core.cross_validator import ValidationStatus

    status_symbols = {
        ValidationStatus.EQUIVALENT: "✓",
        ValidationStatus.DEGRADED: "D",
        ValidationStatus.SKIP: "–",
        ValidationStatus.MISMATCH: "✗",
        ValidationStatus.NO_DATA: "?",
    }

    lines = [
        "# Cross-Paradigm Validation Report",
        "",
        f"**Benchmark:** {report.benchmark_id}",
        f"**Reference Paradigm:** {report.reference_paradigm}",
        f"**Timestamp:** {report.timestamp.isoformat()}",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Equivalent | {report.equivalent_count} |",
        f"| Degraded | {report.degraded_count} |",
        f"| Skip | {report.skip_count} |",
        f"| Mismatch | {report.mismatch_count} |",
        "",
        "## Query Results",
        "",
    ]

    # Header
    header = "| Query |"
    separator = "|-------|"
    for p in report.compared_paradigms:
        header += f" {p} |"
        separator += "------|"
    lines.append(header)
    lines.append(separator)

    # Rows
    for query_id in sorted(report.comparisons.keys()):
        row = f"| {query_id} |"
        for paradigm in report.compared_paradigms:
            if paradigm in report.comparisons[query_id]:
                cmp = report.comparisons[query_id][paradigm]
                symbol = status_symbols.get(cmp.status, "?")
                row += f" {symbol} |"
            else:
                row += " – |"
        lines.append(row)

    lines.extend([
        "",
        "## Legend",
        "",
        "- ✓ **Equivalent** - Results match within tolerance",
        "- D **Degraded** - Known limitation, acceptable difference",
        "- – **Skip** - Query impossible for this paradigm",
        "- ✗ **Mismatch** - Unexpected difference",
        "",
        "---",
        f"*Generated by BaseType Benchmark V3 | Reference: {report.reference_paradigm} | Queries: {report.total_queries}*",
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# =============================================================================
# WORKLOAD COMMANDS
# =============================================================================

@app.command("workloads")
def list_workloads_cmd() -> None:
    """List available workload scenarios.

    Shows predefined workloads for stress testing.
    """
    from .workload import WORKLOADS, WORKLOAD_INFO

    console.print(Panel.fit(
        "[bold blue]Available Workloads[/bold blue]",
        border_style="blue"
    ))

    table = Table(show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Profile")
    table.add_column("Paradigms")
    table.add_column("Duration")

    for name, workload in WORKLOADS.items():
        info = WORKLOAD_INFO.get(name, {})
        table.add_row(
            name,
            info.get("description", workload.description[:40]),
            workload.profile.value,
            ", ".join(workload.paradigms[:3]) + ("..." if len(workload.paradigms) > 3 else ""),
            info.get("duration", f"~{workload.duration_seconds}s"),
        )

    console.print(table)

    console.print("\n[dim]Use: btb-runner workload <name> --paradigms P1,M1[/dim]")


@app.command("workload")
def run_workload_cmd(
    name: Annotated[str, typer.Argument(help="Workload name or path to YAML file")],
    source: Annotated[
        Path,
        typer.Option("-s", "--source", help="Dataset path (Parquet)")
    ] = None,
    paradigms: Annotated[
        str,
        typer.Option("-p", "--paradigms", help="Paradigms to test (comma-separated)")
    ] = None,
    duration: Annotated[
        int,
        typer.Option("-d", "--duration", help="Override duration (seconds)")
    ] = None,
    output: Annotated[
        Path,
        typer.Option("-o", "--output", help="Output JSON file")
    ] = None,
    archive: Annotated[
        Optional[Path],
        typer.Option("-a", "--archive", help="Archive raw results to directory for replay")
    ] = None,
) -> None:
    """Run a workload scenario.

    Executes query sequences to test throughput under load.

    Examples:
        btb-runner workload dashboard_refresh -s data/generated/small-1w
        btb-runner workload bos_twin -p M1,M2 -d 60
        btb-runner workload config/workloads/custom.yaml
        btb-runner workload bos_twin --archive data/results/runs
    """
    from .workload import load_or_get_workload, WorkloadOrchestrator
    from .ram.isolation import IsolationManager

    # Load workload
    try:
        workload = load_or_get_workload(name)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # Override duration if specified
    if duration:
        workload.duration_seconds = duration

    # Parse paradigms
    paradigm_list = paradigms.split(",") if paradigms else workload.paradigms

    console.print(Panel.fit(
        f"[bold blue]Workload: {workload.name}[/bold blue]\n"
        f"Profile: {workload.profile.value}\n"
        f"Paradigms: {', '.join(paradigm_list)}\n"
        f"Duration: {workload.duration_seconds}s, Loop: {workload.loop}",
        border_style="blue"
    ))

    # Setup isolation manager
    isolation = IsolationManager()

    # Build configs
    configs = _build_paradigm_configs()

    # Create orchestrator
    orchestrator = WorkloadOrchestrator(
        isolation=isolation,
        configs=configs,
        timeout_seconds=60.0,
        verbose=True,
    )

    # Run workload
    try:
        results = orchestrator.run_workload(
            scenario=workload,
            paradigms=paradigm_list,
            data_path=source,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        raise typer.Exit(1)

    # Print summary
    console.print("\n")
    console.print(Panel.fit("[bold green]Workload Complete[/bold green]", border_style="green"))

    table = Table(show_header=True)
    table.add_column("Paradigm", style="cyan")
    table.add_column("QPS", justify="right")
    table.add_column("p50 (ms)", justify="right")
    table.add_column("p95 (ms)", justify="right")
    table.add_column("Errors", justify="right")
    table.add_column("Peak (MB)", justify="right")

    for paradigm, result in results.results.items():
        table.add_row(
            paradigm,
            f"{result.qps:.1f}",
            f"{result.latency_p50_ms:.1f}",
            f"{result.latency_p95_ms:.1f}",
            f"{result.total_errors}" if result.total_errors else "[green]0[/green]",
            f"{result.scenario_memory_peak_mb:.0f}" if result.scenario_memory_peak_mb else "-",
        )

    console.print(table)

    # Convert to unified format
    benchmark_results = results.to_benchmark_results()

    # Archive if requested
    if archive:
        from .benchmark.archive import ResultsArchive

        archive_mgr = ResultsArchive(archive)
        archive_mgr.start_run(
            benchmark_id=benchmark_results.benchmark_id,
            paradigms=list(results.results.keys()),
            queries=list({step.query_id for step in workload.sequence}),
            data_profile=f"workload:{workload.name}",
            ram_levels_mb=[],
            n_warmup=0,
            n_runs=sum(step.repeat for step in workload.sequence),
            n_variants=1,
            timeout_seconds=float(workload.duration_seconds or 0),
        )
        archive_mgr.finalize_run(benchmark_summary=benchmark_results.to_dict())
        console.print(f"\n[green]Results archived to {archive / benchmark_results.benchmark_id}[/green]")

    # Save results in both formats
    if output:
        # Native workload format (detailed)
        results.to_json(str(output))
        console.print(f"[dim]Workload results saved to: {output}[/dim]")

        # Also save in unified BenchmarkResults format for validation/archiving
        unified_output = output.with_name(output.stem + "_unified.json")
        benchmark_results.to_json(unified_output)
        console.print(f"[dim]Unified results saved to: {unified_output}[/dim]")


def _build_paradigm_configs() -> dict:
    """Build connection configs for all paradigms."""
    from .config import (
        PostgresConfig,
        MemgraphConfig,
        OxigraphConfig,
        HybridConfig,
    )

    # Default configs (can be overridden via environment)
    pg_config = PostgresConfig()
    mg_config = MemgraphConfig()
    ox_config = OxigraphConfig()

    return {
        "P1": pg_config,
        "P2": pg_config,
        "M1": mg_config,
        "M2": HybridConfig(graph=mg_config, timeseries=pg_config),
        "O2": HybridConfig(graph=ox_config, timeseries=pg_config),
    }


# =============================================================================
# SCENARIOS COMMAND
# =============================================================================

# =============================================================================
# ARCHIVE COMMANDS
# =============================================================================

@app.command("runs")
def list_runs_cmd(
    archive_dir: Annotated[
        Path,
        typer.Option("--dir", "-d", help="Archive directory")
    ] = Path("data/results/runs"),
    limit: Annotated[
        int,
        typer.Option("--limit", "-n", help="Number of runs to show")
    ] = 10,
) -> None:
    """List archived benchmark runs.

    Shows recent benchmark runs that can be replayed for validation.

    Examples:
        btb-runner runs
        btb-runner runs --dir data/results/runs --limit 20
    """
    from .benchmark.archive import ResultsArchive

    if not archive_dir.exists():
        console.print(f"[yellow]No archive directory found: {archive_dir}[/yellow]")
        console.print("[dim]Run a benchmark with --archive to create one[/dim]")
        return

    archive = ResultsArchive(archive_dir)
    runs = archive.list_runs()[:limit]

    if not runs:
        console.print("[yellow]No archived runs found[/yellow]")
        return

    console.print(Panel.fit(
        f"[bold blue]Archived Runs[/bold blue]\n"
        f"Directory: {archive_dir}",
        border_style="blue"
    ))

    table = Table(show_header=True)
    table.add_column("Benchmark ID", style="cyan")
    table.add_column("Paradigms")
    table.add_column("Queries")
    table.add_column("Git")
    table.add_column("Date")

    for run_id in runs:
        try:
            run = archive.load_run(run_id)
            metadata = run.metadata
            git_info = metadata.git_hash[:7] if metadata.git_hash else "-"
            if metadata.git_dirty:
                git_info += "*"
            table.add_row(
                run_id,
                ", ".join(run.paradigms[:3]) + ("..." if len(run.paradigms) > 3 else ""),
                str(len(run.queries)),
                git_info,
                metadata.start_time.strftime("%Y-%m-%d %H:%M") if metadata.start_time else "-",
            )
        except Exception as e:
            table.add_row(run_id, "[red]Error[/red]", str(e)[:30], "-", "-")

    console.print(table)
    console.print(f"\n[dim]Use: btb-runner replay <benchmark_id> to replay validation[/dim]")


@app.command("replay")
def replay_validation_cmd(
    benchmark_id: Annotated[
        str,
        typer.Argument(help="Benchmark ID to replay (from 'runs' command)")
    ],
    archive_dir: Annotated[
        Path,
        typer.Option("--dir", "-d", help="Archive directory")
    ] = Path("data/results/runs"),
    reference: Annotated[
        str,
        typer.Option("--reference", "-r", help="Reference paradigm")
    ] = "P1",
    semantic: Annotated[
        bool,
        typer.Option("--semantic/--no-semantic", help="Enable semantic validation")
    ] = True,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output JSON report")
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed results")
    ] = False,
) -> None:
    """Replay validation on archived results.

    Re-runs cross-paradigm validation on previously saved raw results
    without re-executing queries. Useful for:
    - Testing new validation rules
    - Debugging validation issues
    - Generating reports from past runs

    Examples:
        btb-runner replay 2026-01-11_153439
        btb-runner replay 2026-01-11_153439 --semantic --reference P1
        btb-runner replay 2026-01-11_153439 -o new_validation.json
    """
    from .benchmark.archive import ResultsArchive
    from .core.cross_validator import CrossParadigmValidator, ValidationStatus

    # Load archive
    archive_path = archive_dir / benchmark_id
    if not archive_path.exists():
        # Try to find partial match
        archive = ResultsArchive(archive_dir)
        runs = archive.list_runs()
        matches = [r for r in runs if benchmark_id in r]
        if matches:
            console.print(f"[yellow]Run '{benchmark_id}' not found. Did you mean:[/yellow]")
            for m in matches[:5]:
                console.print(f"  {m}")
        else:
            console.print(f"[red]Run not found: {benchmark_id}[/red]")
            console.print(f"[dim]Use 'btb-runner runs' to list available runs[/dim]")
        raise typer.Exit(1)

    archive = ResultsArchive(archive_dir)
    run = archive.load_run(benchmark_id)

    console.print(Panel.fit(
        f"[bold blue]Replay Validation[/bold blue]\n\n"
        f"Run: {benchmark_id}\n"
        f"Paradigms: {', '.join(run.paradigms)}\n"
        f"Queries: {len(run.queries)}\n"
        f"Reference: {reference}\n"
        f"Semantic: {'Yes' if semantic else 'No'}",
        border_style="blue"
    ))

    # Convert to BenchmarkResults
    results = run.to_benchmark_results()

    # Setup validator
    semantic_path = None
    if semantic:
        semantic_path = Path(__file__).parents[2] / "config" / "semantic_definitions.yaml"
        if not semantic_path.exists():
            semantic_path = Path("config/semantic_definitions.yaml")

    validator = CrossParadigmValidator(
        reference=reference,
        float_tolerance=0.01,
        semantic_definitions_path=semantic_path if semantic and semantic_path.exists() else None,
    )

    # Run validation
    report = validator.validate(results)

    # Display results (simplified)
    console.print("\n")
    summary_table = Table(title="Validation Summary", show_header=True)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Count", justify="right")

    summary_table.add_row("Equivalent", f"[green]{report.equivalent_count}[/green]")
    summary_table.add_row("Degraded", f"[yellow]{report.degraded_count}[/yellow]")
    summary_table.add_row("Skip", f"[dim]{report.skip_count}[/dim]")
    summary_table.add_row("Mismatch", f"[red]{report.mismatch_count}[/red]")
    console.print(summary_table)

    # Show mismatches if verbose
    if verbose and report.mismatch_count > 0:
        console.print("\n[bold red]Mismatches:[/bold red]")
        for query_id, paradigm_results in report.comparisons.items():
            for paradigm, cmp in paradigm_results.items():
                if cmp.status == ValidationStatus.MISMATCH:
                    console.print(f"  {query_id} ({paradigm}): {cmp.reason or 'Unknown'}")
                    if cmp.semantic_status:
                        console.print(f"    Semantic: {cmp.semantic_status}")

    # Save report
    if output:
        report.to_json(output)
        console.print(f"\n[green]Report saved to {output}[/green]")

    console.print(f"\n[green]Replay complete![/green]")


@app.command("scenarios")
def list_scenarios_cmd() -> None:
    """List available benchmark scenarios.

    Shows predefined scenarios with their configurations.
    """
    from .scenarios import SCENARIOS, SCENARIO_INFO

    console.print(Panel.fit(
        "[bold blue]Available Scenarios[/bold blue]",
        border_style="blue"
    ))

    table = Table(show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Paradigms")
    table.add_column("RAM Levels")
    table.add_column("Duration")

    for name, config in SCENARIOS.items():
        info = SCENARIO_INFO.get(name, {})
        table.add_row(
            name,
            info.get("description", ""),
            ", ".join(config.paradigms[:3]) + ("..." if len(config.paradigms) > 3 else ""),
            f"{len(config.ram_levels_mb)} levels",
            info.get("estimated_duration", ""),
        )

    console.print(table)

    console.print("\n[dim]Use: btb-runner benchmark --scenario <name>[/dim]")


@app.command("validate-expected")
def validate_expected_cmd(
    archive: Annotated[
        Path,
        typer.Argument(help="Path to benchmark archive directory or results.json")
    ],
    dataset: Annotated[
        Optional[Path],
        typer.Option("--dataset", "-d", help="Path to dataset dir (with expected_answers/)")
    ] = None,
    paradigm: Annotated[
        Optional[str],
        typer.Option("--paradigm", "-p", help="Specific paradigm to validate (default: all)")
    ] = None,
    queries: Annotated[
        Optional[str],
        typer.Option("--queries", "-q", help="Comma-separated query IDs to validate (default: all)")
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output JSON report file")
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed validation info")
    ] = False,
    fail_on_mismatch: Annotated[
        bool,
        typer.Option("--fail-on-mismatch", help="Exit with code 1 if any MISMATCH found")
    ] = False,
) -> None:
    """Validate benchmark results against Expected Answers.

    This validates that paradigm results match the ground truth computed
    during dataset generation (expected_answers/).

    The --dataset option should point to a dataset directory containing
    expected_answers/ (e.g., data/generated/medium-1w/).

    Validation statuses:
    - MATCH: Result matches Expected Answer exactly
    - DEGRADED: Expected difference (documented limitation)
    - IMPOSSIBLE: Query not supported by paradigm
    - MISMATCH: Bug detected! Result differs from Expected

    Examples:
        btb-runner validate-expected results.json --dataset data/generated/medium-1w/
        btb-runner validate-expected archive/ --dataset data/generated/medium-1w/
        btb-runner validate-expected archive/ -p P1 --queries Q1,Q2,Q3 -v
        btb-runner validate-expected archive/ --fail-on-mismatch
    """
    try:
        from ..validation import ExpectedAnswerStore, AnswerValidator, ValidationStatus
    except ImportError as e:
        console.print(f"[red]Failed to import validation module: {e}[/red]")
        raise typer.Exit(1)

    from .benchmark.results import BenchmarkResults

    # Validate paths
    if not archive.exists():
        console.print(f"[red]Archive not found: {archive}[/red]")
        raise typer.Exit(1)

    # Auto-detect dataset directory
    if dataset is None:
        # Try to find expected_answers in common locations
        candidates = [
            Path("data/generated"),
        ]
        for candidate in candidates:
            if candidate.exists():
                for subdir in candidate.iterdir():
                    if subdir.is_dir():
                        expected_dir = subdir / "expected_answers"
                        if expected_dir.exists():
                            dataset = subdir
                            console.print(f"[dim]Auto-detected dataset: {dataset}[/dim]")
                            break
                if dataset:
                    break

        if dataset is None:
            console.print("[red]Could not find expected answers. Use --dataset to specify.[/red]")
            console.print("[yellow]Expected answers are generated with: btb-runner generate[/yellow]")
            raise typer.Exit(1)

    if not dataset.exists():
        console.print(f"[red]Dataset not found: {dataset}[/red]")
        console.print("[yellow]Expected answers are generated with: btb-runner generate[/yellow]")
        raise typer.Exit(1)

    # Check for expected_answers subdirectory
    if not (dataset / "expected_answers").exists():
        console.print(f"[red]No expected_answers/ in {dataset}[/red]")
        console.print("[yellow]Regenerate dataset with: btb-runner generate[/yellow]")
        raise typer.Exit(1)

    console.print(Panel.fit(
        "[bold blue]Expected Answer Validation[/bold blue]\n\n"
        f"Archive: {archive}\n"
        f"Dataset: {dataset}",
        border_style="blue"
    ))

    try:
        # Load Expected Answers
        store = ExpectedAnswerStore(dataset)
        store.load()
        console.print(f"[dim]Loaded {len(store)} Expected Answers[/dim]")

        # Load results
        if archive.is_file() and archive.suffix == ".json":
            results = BenchmarkResults.from_json(archive)
        else:
            # Look for results in archive directory
            # Try different names: benchmark_summary.json, results.json
            results_path = None
            for filename in ["benchmark_summary.json", "results.json"]:
                candidate = archive / filename
                if candidate.exists():
                    results_path = candidate
                    break

            if results_path:
                results = BenchmarkResults.from_json(results_path)
            else:
                console.print(f"[red]No results file found in {archive}[/red]")
                console.print("[dim]Expected: benchmark_summary.json or results.json[/dim]")
                raise typer.Exit(1)

        console.print(f"[dim]Loaded benchmark: {results.benchmark_id}[/dim]")

        # Setup validator
        semantic_path = Path(__file__).parent.parent.parent.parent / "config" / "semantic_definitions.yaml"
        rules_path = Path(__file__).parent.parent.parent.parent / "config" / "validation_rules.yaml"

        if not semantic_path.exists():
            semantic_path = Path("config/semantic_definitions.yaml")
        if not rules_path.exists():
            rules_path = Path("config/validation_rules.yaml")

        validator = AnswerValidator(
            expected_store=store,
            definitions_path=semantic_path if semantic_path.exists() else None,
            rules_path=rules_path if rules_path.exists() else None,
        )

        # Determine paradigms and queries to validate
        paradigms_to_check = [paradigm] if paradigm else list(results.results.keys())
        query_ids = queries.split(",") if queries else None

        # Run validation
        all_validations: dict[str, dict[str, any]] = {}
        counters = {"MATCH": 0, "DEGRADED": 0, "IMPOSSIBLE": 0, "MISMATCH": 0}

        for p in paradigms_to_check:
            if p not in results.results:
                console.print(f"[yellow]Paradigm {p} not in results, skipping[/yellow]")
                continue

            pr = results.results[p]
            all_validations[p] = {}

            # Get raw results from archive if available
            raw_results_dir = archive / "raw_results" / p if archive.is_dir() else None

            for level in pr.levels:
                for qid, qr in level.queries.items():
                    if query_ids and qid not in query_ids:
                        continue

                    # Try to load full rows from archive
                    rows = []
                    if raw_results_dir:
                        raw_file = raw_results_dir / f"{qid}.json"
                        if raw_file.exists():
                            import json
                            with open(raw_file) as f:
                                data = json.load(f)
                                rows = data.get("rows", [])

                    # If no raw rows, use sample_rows from results
                    if not rows and qr.sample_rows:
                        rows = qr.sample_rows
                        if verbose:
                            console.print(f"[yellow]Using sample rows for {p}/{qid} (not full results)[/yellow]")

                    # Get parameters for this specific query (from expected answer)
                    params = store.get_query_parameters(qid)

                    # Validate
                    result = validator.validate_query(qid, p, rows, params)
                    all_validations[p][qid] = result
                    counters[result.status.value] += 1

        # Display results table
        table = Table(title="Validation Results", show_header=True)
        table.add_column("Paradigm", style="cyan")
        table.add_column("Query", style="dim")
        table.add_column("Status")
        table.add_column("Rows", justify="right")
        table.add_column("Reason")

        status_colors = {
            "MATCH": "green",
            "DEGRADED": "yellow",
            "IMPOSSIBLE": "dim",
            "MISMATCH": "red bold",
        }

        for p, validations in all_validations.items():
            for qid in sorted(validations.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 999):
                result = validations[qid]
                status_style = status_colors.get(result.status.value, "white")

                rows_str = ""
                if result.expected_row_count or result.paradigm_row_count:
                    rows_str = f"{result.paradigm_row_count}/{result.expected_row_count}"

                reason = result.reason[:50] + "..." if len(result.reason) > 50 else result.reason

                table.add_row(
                    p,
                    qid,
                    f"[{status_style}]{result.status.value}[/{status_style}]",
                    rows_str,
                    reason,
                )

        console.print(table)

        # Summary
        total = sum(counters.values())
        console.print("\n")
        console.print(Panel.fit(
            f"Total: {total} | "
            f"[green]MATCH: {counters['MATCH']}[/green] | "
            f"[yellow]DEGRADED: {counters['DEGRADED']}[/yellow] | "
            f"[dim]IMPOSSIBLE: {counters['IMPOSSIBLE']}[/dim] | "
            f"[red]MISMATCH: {counters['MISMATCH']}[/red]",
            title="Summary"
        ))

        # Show MISMATCH details if any
        if counters["MISMATCH"] > 0:
            console.print("\n[red bold]MISMATCH Details (possible bugs):[/red bold]")
            for p, validations in all_validations.items():
                for qid, result in validations.items():
                    if result.status.value == "MISMATCH":
                        console.print(f"  • {p}/{qid}: {result.reason}")
                        if result.missing_items:
                            console.print(f"    Missing: {result.missing_items[:5]}")
                        if result.extra_items:
                            console.print(f"    Extra: {result.extra_items[:5]}")

        # Save report if requested
        if output:
            import json
            report = {
                "summary": counters,
                "validations": {
                    p: {qid: v.to_dict() for qid, v in vals.items()}
                    for p, vals in all_validations.items()
                }
            }
            with open(output, "w") as f:
                json.dump(report, f, indent=2)
            console.print(f"\n[green]Report saved to {output}[/green]")

        # Exit with error if mismatches and flag set
        if fail_on_mismatch and counters["MISMATCH"] > 0:
            raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


def version_callback(value: bool) -> None:
    if value:
        console.print("Benchmark Runner V3 - 2025.1.0")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-V", help="Show version", callback=version_callback, is_eager=True)
    ] = False,
) -> None:
    """Benchmark Runner V3 - Parquet-first query execution framework."""
    if ctx.invoked_subcommand is None and not version:
        console.print("Use --help for available commands")
        raise typer.Exit()


if __name__ == "__main__":
    app()
