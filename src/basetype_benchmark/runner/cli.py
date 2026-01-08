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
from .core.params import get_golden_loader, get_query_parameters
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
        parameters_valid=True,
    )

    # Check parameters
    try:
        params = get_query_parameters(query_id)
        required_params = query_def.get_parameter_names()
        for param_name in required_params:
            if params.get(param_name) is None:
                result.warnings.append(f"Parameter '{param_name}' not in golden_answers")
    except Exception as e:
        result.issues.append(f"Parameter loading error: {e}")
        result.parameters_valid = False

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
            help="Specific engine to validate (P1, P2, M1, M2, O2)"
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
            help="Paradigm to use (P1, P2, M1, M2, O2)"
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

    # Validate paradigm
    if paradigm not in ("P1", "P2", "M1", "M2", "O2"):
        console.print(f"[red]Unknown paradigm: {paradigm}[/red]")
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
) -> None:
    """Execute full benchmark with RAM gradient and disk optimization.

    The benchmark exports, loads, and benchmarks each paradigm sequentially,
    optionally cleaning up exports after each paradigm to save disk space.

    Examples:
        btb-runner benchmark -s data/generated/small-1w -o results.json
        btb-runner benchmark -s data/generated/small-1w --scenario quick
        btb-runner benchmark -s data/generated/small-1w --scenario config/scenarios/custom.yaml
        btb-runner benchmark -s data/generated/small-1w -p P1,M1 --ram "32,16,8"
        btb-runner benchmark -s data/generated/small-1w --no-cleanup  # Keep exports
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
        paradigm_list = ["P1", "P2", "M1", "M2", "O2"]
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
        orchestrator = BenchmarkOrchestrator(configs=configs)
        results = orchestrator.run_full_benchmark(
            source_dir=source_dir,
            export_dir=export_dir,
            output_path=output,
            scenario=scenario,
            cleanup_exports=cleanup,
        )
        console.print(f"\n[green]Benchmark complete! Results saved to {output}[/green]")
    except Exception as e:
        console.print(f"[red]Benchmark failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("gradient")
def gradient(
    paradigm: Annotated[
        str,
        typer.Argument(help="Paradigm to test (P1, P2, M1, M2, O2)")
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

    # Validate
    if paradigm not in ("P1", "P2", "M1", "M2", "O2"):
        console.print(f"[red]Unknown paradigm: {paradigm}[/red]")
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
        typer.Argument(help="Target paradigm (P1, P2, M1, M2, O2)")
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
        btb-runner load O2 -d data/export/o2 --dry-run
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

    # Validate paradigm
    if paradigm not in ("P1", "P2", "M1", "M2", "O2"):
        console.print(f"[red]Unknown paradigm: {paradigm}[/red]")
        console.print("Valid paradigms: P1, P2, M1, M2, O2")
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
    paradigms = ["p1", "p2", "m1", "m2", "o2"]
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
# GOLDEN COMMANDS
# =============================================================================

golden_app = typer.Typer(
    name="golden",
    help="Golden dataset validation commands",
)
app.add_typer(golden_app, name="golden")


@golden_app.command("export")
def golden_export(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output directory for Parquet files")
    ] = Path("data/golden"),
) -> None:
    """Export golden dataset to Parquet files.

    Creates nodes.parquet, edges.parquet, timeseries.parquet from the
    reference golden dataset for validation purposes.
    """
    from ..dataset.golden import export_to_parquet

    console.print(Panel.fit(
        "[bold blue]Export Golden Dataset[/bold blue]",
        border_style="blue"
    ))

    try:
        output.mkdir(parents=True, exist_ok=True)
        export_to_parquet(output)
        console.print(f"\n[green]Golden dataset exported to {output}[/green]")

        # Show file sizes
        for f in output.glob("*.parquet"):
            size_kb = f.stat().st_size / 1024
            console.print(f"  {f.name}: {size_kb:.1f} KB")

    except Exception as e:
        console.print(f"[red]Export failed: {e}[/red]")
        raise typer.Exit(1)


@golden_app.command("validate")
def golden_validate(
    paradigm: Annotated[
        Optional[str],
        typer.Option("--paradigm", "-p", help="Paradigm to validate (P1, P2, M1, M2, O2)")
    ] = None,
    queries: Annotated[
        Optional[str],
        typer.Option("--queries", "-q", help="Comma-separated query IDs to validate")
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed validation results")
    ] = False,
) -> None:
    """Validate query results against golden answers.

    Compares actual query execution results with expected values
    from golden_answers.yaml to ensure reproducibility.
    """
    from .core.validator import GoldenValidator

    console.print(Panel.fit(
        "[bold blue]Golden Validation[/bold blue]",
        border_style="blue"
    ))

    try:
        validator = GoldenValidator()

        # Parse queries
        query_list = None
        if queries:
            query_list = [q.strip().upper() for q in queries.split(",")]

        # Run validation
        results = validator.validate_all(
            paradigm=paradigm.upper() if paradigm else None,
            queries=query_list,
        )

        # Display results
        table = Table(title="Validation Results", show_header=True)
        table.add_column("Query")
        table.add_column("Status", justify="center")
        table.add_column("Details" if verbose else "")

        passed = 0
        failed = 0

        for qid, result in results.items():
            if result["valid"]:
                status = "[green]PASS[/green]"
                passed += 1
            else:
                status = "[red]FAIL[/red]"
                failed += 1

            details = ""
            if verbose and not result["valid"]:
                details = result.get("error", "")[:50]

            table.add_row(qid, status, details)

        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] {passed} passed, {failed} failed")

        if failed > 0:
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        raise typer.Exit(1)


@golden_app.command("report")
def golden_report() -> None:
    """Show golden validation report.

    Displays a summary of the golden dataset and expected answers.
    """
    from .core.params import get_golden_loader

    console.print(Panel.fit(
        "[bold blue]Golden Dataset Report[/bold blue]",
        border_style="blue"
    ))

    try:
        loader = get_golden_loader()

        # Query count
        console.print("\n[cyan]Golden Answers:[/cyan]")
        for qid in sorted(loader.get_query_ids()):
            answer = loader.get_answer(qid)
            if answer:
                row_count = answer.get("row_count", "?")
                console.print(f"  {qid}: {row_count} rows expected")

    except Exception as e:
        console.print(f"[red]Report failed: {e}[/red]")
        raise typer.Exit(1)


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
        typer.Argument(help="Target paradigm (P1, P2, M1, M2, O2)")
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
# SCENARIOS COMMAND
# =============================================================================

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
