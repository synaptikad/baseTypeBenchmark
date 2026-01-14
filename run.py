#!/usr/bin/env python3
"""BaseType Benchmark V3 - Interactive Runner.

Simple, iterative workflow following the natural benchmark process.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import shutil
import json
import os
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "rich", "-q"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table

console = Console()


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="python run.py",
        description="BaseType Benchmark V3 - Interactive Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py              Launch interactive menu
  python run.py --help       Show this help

For scripting, use btb-runner directly:
  btb-runner benchmark -s data/generated/small-1w -p P1,M1 --ram 8
  btb-runner validate results.json --cross-matrix
  btb-runner run-query Q7 -p M1

See 'btb-runner --help' for all CLI commands.
"""
    )
    parser.add_argument("--version", "-V", action="store_true",
                        help="Show version and exit")
    return parser.parse_args()


# Paths
PROJECT_DIR = Path(__file__).parent
VENV_PYTHON = PROJECT_DIR / ".venv" / "bin" / "python"
VENV_BTB = PROJECT_DIR / ".venv" / "bin" / "btb-runner"
CONFIG_DIR = PROJECT_DIR / "config"
DATA_DIR = Path(os.environ.get("BTB_DATA_DIR", PROJECT_DIR / "data"))
GENERATED_DIR = DATA_DIR / "generated"
RESULTS_DIR = DATA_DIR / "results"
ARCHIVE_DIR = RESULTS_DIR / "runs"  # Raw results archive for replay
# Note: Exports are now on-demand in temporary directories during benchmark

PROFILES = ["small", "medium", "large", "xlarge"]
DURATIONS = ["2d", "1w", "1m", "6m", "1y"]
# Note: O2 (Oxigraph) is exploratory only - not included in benchmark runs
# O2 code remains for research purposes but is excluded from standard benchmarks
PARADIGMS = ["P1", "P2", "M1", "M2"]
SCENARIOS_DIR = CONFIG_DIR / "scenarios"

# All query IDs for reference
# Note: Order matters! Writes (QW) must execute before their validation queries
ALL_READ_QUERIES = [f"Q{i}" for i in range(1, 42)]   # Q1-Q41
ALL_WRITE_QUERIES = [f"QW{i}" for i in range(1, 13)]  # QW1-QW12
# Correct order: independent reads, then write→validation pairs
# Q1-Q23 (independent) + Q27-Q34 (independent) +
# QW1→Q35 + QW2→Q36 + QW3→Q37 + QW4→Q24 + QW5/QW6→Q25 + QW7→Q26 + QW8→Q38
ALL_QUERIES_UNORDERED = ALL_READ_QUERIES + ALL_WRITE_QUERIES  # For reference only
ALL_QUERIES = (
    [f"Q{i}" for i in range(1, 24)] +   # Q1-Q23 (independent reads)
    [f"Q{i}" for i in range(27, 35)] +  # Q27-Q34 (independent reads)
    ["QW1", "Q35"] +                     # QW1 → Q35 (timeseries append then validate)
    ["QW2", "Q36"] +                     # QW2 → Q36 (metadata tag then validate)
    ["QW3", "Q37"] +                     # QW3 → Q37 (relation mutation then validate)
    ["QW4", "Q24"] +                     # QW4 → Q24 (maintenance event then validate)
    ["QW5", "QW6", "Q25"] +              # QW5, QW6 → Q25 (calibration/firmware then validate)
    ["QW7", "Q26"] +                     # QW7 → Q26 (capability then validate)
    ["QW8", "Q38"] +                     # QW8 → Q38 (remove property then validate)
    ["QW9", "Q39"] +                     # QW9 → Q39 (tenant move-in then validate)
    ["QW10", "Q40"] +                    # QW10 → Q40 (tenant move-out then validate)
    ["QW11", "QW12", "Q41"]              # QW11, QW12 → Q41 (space reassignment/merge then validate)
)  # 53 total


def run_cmd(cmd: list[str]) -> int:
    console.print(f"[dim]$ {' '.join(str(c) for c in cmd)}[/dim]\n")
    return subprocess.run(cmd).returncode


def btb(*args) -> int:
    return run_cmd([str(VENV_BTB)] + [str(a) for a in args])


def clear():
    console.clear()


def header(title: str):
    clear()
    console.print(Panel(f"[bold]{title}[/bold]", border_style="blue"))
    console.print()


def wait():
    console.print()
    Prompt.ask("[dim]Enter to continue[/dim]")


def list_dirs(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted([d for d in path.iterdir() if d.is_dir()])


def dir_size(path: Path) -> str:
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    for unit in ["B", "KB", "MB", "GB"]:
        if total < 1024:
            return f"{total:.1f} {unit}"
        total /= 1024
    return f"{total:.1f} TB"


def show_help():
    """Display detailed help using Rich formatting."""
    header("Help")

    console.print(Panel.fit(
        "[bold blue]BaseType Benchmark V3[/bold blue]\n"
        "[dim]Interactive Runner - Menu-driven benchmark interface[/dim]",
        border_style="blue"
    ))
    console.print()

    # Interactive menus table
    table = Table(title="Interactive Menus", show_header=True)
    table.add_column("Key", style="cyan", width=4)
    table.add_column("Menu", width=12)
    table.add_column("Actions")

    table.add_row("1", "Dataset", "Generate synthetic data, Delete datasets")
    table.add_row("2", "Benchmark", "Run benchmark wizard, Debug query, Validate matrix")
    table.add_row("3", "Results", "Validate cross-paradigm, Expected answers, Reports")
    table.add_row("4", "System", "Docker containers, Logs, Schema status, Info")
    table.add_row("h", "Help", "Show this help")
    table.add_row("q", "Quit", "Exit the program")
    console.print(table)
    console.print()

    # btb-runner equivalents
    table2 = Table(title="Equivalent btb-runner Commands (for scripting)", show_header=True)
    table2.add_column("Action", width=22)
    table2.add_column("Command")

    table2.add_row("Generate dataset", "btb-runner generate --profile small --duration 1w")
    table2.add_row("Run benchmark", "btb-runner benchmark -s <source> -p P1,M1 --ram 8,16,32")
    table2.add_row("Debug query", "btb-runner run-query Q7 -p M1")
    table2.add_row("Validate results", "btb-runner validate results.json --cross-matrix")
    table2.add_row("Validate expected", "btb-runner validate-expected --archive <run> --dataset <ds>")
    table2.add_row("Check system", "btb-runner status")
    table2.add_row("List queries", "btb-runner dry-run --matrix")
    table2.add_row("Query info", "btb-runner info Q7")
    console.print(table2)
    console.print()

    # Paradigms info
    console.print("[bold]Paradigms:[/bold]")
    console.print("  P1 = PostgreSQL relational")
    console.print("  P2 = PostgreSQL JSON/EAV")
    console.print("  M1 = Memgraph graph-only")
    console.print("  M2 = Memgraph + TimescaleDB hybrid")
    console.print("  [dim](O2 = Oxigraph - exploratory, not in benchmarks)[/dim]")
    console.print()

    console.print("[dim]For full CLI documentation: btb-runner --help[/dim]")


def select_from_list(items: list, prompt: str = "Select") -> int | None:
    """Display numbered list, return index (0-based) or None."""
    if not items:
        return None
    for i, item in enumerate(items, 1):
        if isinstance(item, Path):
            console.print(f"  [cyan]{i}[/cyan]. {item.name} ({dir_size(item)})")
        else:
            console.print(f"  [cyan]{i}[/cyan]. {item}")
    console.print()
    choice = IntPrompt.ask(prompt, default=1)
    if 1 <= choice <= len(items):
        return choice - 1
    return None


# =============================================================================
# MAIN MENU
# =============================================================================

def main_menu() -> str:
    header("BaseType Benchmark V3")

    # Status line
    datasets = list_dirs(GENERATED_DIR)
    results = list(RESULTS_DIR.glob("*.json")) if RESULTS_DIR.exists() else []
    console.print(f"[dim]{len(datasets)} datasets | {len(results)} results[/dim]\n")

    console.print("[cyan]1[/cyan]. Dataset     [dim]Generate & manage data[/dim]")
    console.print("[cyan]2[/cyan]. Benchmark   [dim]Run comparisons[/dim]")
    console.print("[cyan]3[/cyan]. Results     [dim]View & export[/dim]")
    console.print("[cyan]4[/cyan]. System      [dim]Docker, info[/dim]")
    console.print()
    console.print("[cyan]h[/cyan]. Help")
    console.print("[cyan]q[/cyan]. Quit")
    console.print()

    return Prompt.ask("", choices=["1", "2", "3", "4", "h", "q"], default="1", show_choices=False)


# =============================================================================
# 1. DATASET
# =============================================================================

def menu_dataset():
    while True:
        header("Dataset")

        datasets = list_dirs(GENERATED_DIR)
        if datasets:
            console.print("[bold]Available:[/bold]")
            for ds in datasets:
                console.print(f"  {ds.name} ({dir_size(ds)})")
            console.print()

        console.print("[cyan]1[/cyan]. Generate new")
        console.print("[cyan]2[/cyan]. Delete")
        console.print()
        console.print("[dim]Note: Export is done on-demand during benchmark[/dim]")
        console.print()
        console.print("[cyan]b[/cyan]. Back")
        console.print()

        choice = Prompt.ask("", choices=["1", "2", "b"], default="1", show_choices=False)

        if choice == "b":
            return
        elif choice == "1":
            generate_dataset()
        elif choice == "2":
            delete_dataset()


def generate_dataset():
    header("Generate Dataset")

    console.print("[bold]Profile:[/bold]")
    for i, p in enumerate(PROFILES, 1):
        console.print(f"  [cyan]{i}[/cyan]. {p}")
    console.print()
    idx = IntPrompt.ask("Profile", default=1)
    profile = PROFILES[idx - 1] if 1 <= idx <= len(PROFILES) else "small"

    console.print("\n[bold]Duration:[/bold]")
    for i, d in enumerate(DURATIONS, 1):
        console.print(f"  [cyan]{i}[/cyan]. {d}")
    console.print()
    idx = IntPrompt.ask("Duration", default=2)
    duration = DURATIONS[idx - 1] if 1 <= idx <= len(DURATIONS) else "1w"

    seed = IntPrompt.ask("\nSeed", default=42)

    target_rows_str = Prompt.ask("\nTarget rows timeseries [dim](vide=auto)[/dim]", default="")
    target_rows = int(target_rows_str) if target_rows_str.strip() else None

    console.print(f"\n[yellow]Generate {profile}-{duration} (seed={seed}, target_rows={target_rows or 'auto'})?[/yellow]")
    if not Confirm.ask("", default=True):
        return

    output_dir = GENERATED_DIR / f"{profile}-{duration}"
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(VENV_PYTHON), "-m", "src.basetype_benchmark.dataset.generator",
        "--profile", profile,
        "--duration", duration,
        "--seed", str(seed),
        "--config-dir", str(CONFIG_DIR),
        "--output", str(GENERATED_DIR),
        "--format", "parquet"
    ]
    if target_rows:
        cmd.extend(["--target-rows", str(target_rows)])

    console.print()
    run_cmd(cmd)

    console.print(f"\n[green]Done: {output_dir}[/green]")
    wait()


def delete_dataset():
    header("Delete Dataset")

    datasets = list_dirs(GENERATED_DIR)
    if not datasets:
        console.print("[yellow]No datasets.[/yellow]")
        wait()
        return

    console.print("[bold]Select to delete:[/bold]")
    # Display options with sizes
    for i, d in enumerate(datasets, 1):
        console.print(f"  [cyan]{i}[/cyan]. {d.name} ({dir_size(d)})")
    console.print(f"  [cyan]{len(datasets) + 1}[/cyan]. [red]DELETE ALL[/red]")
    console.print()
    choice = IntPrompt.ask("Select", default=1)
    if not (1 <= choice <= len(datasets) + 1):
        return
    idx = choice - 1

    if idx == len(datasets):
        # Delete ALL selected
        console.print(f"\n[bold red]WARNING: This will delete ALL {len(datasets)} datasets![/bold red]")
        console.print("[yellow]This action cannot be undone.[/yellow]\n")
        if not Confirm.ask("[red]Are you sure you want to delete ALL datasets?[/red]", default=False):
            return
        console.print("\n[bold red]FINAL CONFIRMATION[/bold red]")
        if not Confirm.ask("[red]Type 'y' again to confirm deletion of ALL datasets[/red]", default=False):
            console.print("[green]Cancelled.[/green]")
            wait()
            return
        # Delete all
        for target in datasets:
            shutil.rmtree(target)
        console.print(f"[green]Deleted {len(datasets)} datasets.[/green]")
    else:
        # Single dataset deletion
        target = datasets[idx]
        console.print(f"\n[bold red]WARNING: Delete '{target.name}'?[/bold red]")
        console.print("[yellow]This action cannot be undone.[/yellow]\n")
        if not Confirm.ask("[red]Are you sure?[/red]", default=False):
            console.print("[green]Cancelled.[/green]")
            wait()
            return
        console.print("\n[bold red]FINAL CONFIRMATION[/bold red]")
        if not Confirm.ask(f"[red]Type 'y' again to confirm deletion of '{target.name}'[/red]", default=False):
            console.print("[green]Cancelled.[/green]")
            wait()
            return
        shutil.rmtree(target)
        console.print("[green]Deleted.[/green]")
    wait()


# =============================================================================
# 2. BENCHMARK
# =============================================================================

# RAM levels available for selection
RAM_LEVELS = [128, 96, 64, 48, 32, 24, 16, 12, 8, 4, 2, 1, 0.5]


def menu_benchmark():
    while True:
        header("Benchmark")

        # Check readiness
        datasets = list_dirs(GENERATED_DIR)
        datasets = [d for d in datasets if (d / "nodes.parquet").exists()]
        docker_ok = subprocess.run(["docker", "info"], capture_output=True).returncode == 0

        if not docker_ok:
            console.print("[red]Docker not running[/red]\n")
        if not datasets:
            console.print("[yellow]No datasets available[/yellow]\n")

        console.print("[cyan]1[/cyan]. Run benchmark   [dim]Simple or Scenario, Single RAM or Gradient[/dim]")
        console.print()
        console.print("[cyan]d[/cyan]. Debug query     [dim]Run single query[/dim]")
        console.print("[cyan]v[/cyan]. Validate        [dim]Check query matrix[/dim]")
        console.print()
        console.print("[cyan]b[/cyan]. Back")
        console.print()

        choice = Prompt.ask("", choices=["1", "d", "v", "b"], default="1", show_choices=False)

        if choice == "b":
            return

        if choice == "1":
            if not docker_ok:
                console.print("\n[red]Start Docker first.[/red]")
                wait()
                continue
            if not datasets:
                console.print("\n[yellow]Generate a dataset first (Dataset > Generate).[/yellow]")
                wait()
                continue
            run_benchmark_wizard(datasets)
        elif choice == "d":
            debug_query()
        elif choice == "v":
            btb("dry-run", "--matrix")
            wait()


def run_benchmark_wizard(datasets: list[Path]):
    """Unified benchmark wizard: Dataset → Type → Mode → Paradigms → RAM."""
    header("Run Benchmark")

    # Step 0: Clean Docker option (before dataset selection)
    n_containers, n_volumes, container_list = get_docker_status_summary()

    if n_containers > 0 or n_volumes > 0:
        console.print("[bold]0. Docker Status[/bold]")
        console.print(f"   Containers: {n_containers}, Volumes: {n_volumes}")
        for c in container_list[:3]:  # Show first 3
            console.print(f"   [dim]{c}[/dim]")
        console.print()

        if Confirm.ask("[yellow]Clean Docker state before benchmark?[/yellow]", default=True):
            docker_prune_all()
            console.print()

    # 1. Select dataset
    console.print("[bold]1. Dataset[/bold]")
    idx = select_from_list(datasets)
    if idx is None:
        return
    source = datasets[idx]

    # 2. Select type
    console.print("\n[bold]2. Type[/bold]")
    console.print("  [cyan]1[/cyan]. Simple    [dim]Isolated queries, reset between each[/dim]")
    console.print("  [cyan]2[/cyan]. Scenario  [dim]Query sequences, realistic load[/dim]")
    console.print()
    bench_type = Prompt.ask("Select", choices=["1", "2"], default="1")

    # 3. Select mode
    console.print("\n[bold]3. Mode[/bold]")
    console.print("  [cyan]1[/cyan]. Single RAM   [dim]Fixed memory limit[/dim]")
    console.print("  [cyan]2[/cyan]. Gradient     [dim]Sweep RAM levels, find plateau[/dim]")
    console.print()
    bench_mode = Prompt.ask("Select", choices=["1", "2"], default="2")

    # 4. Select paradigms
    console.print("\n[bold]4. Paradigms[/bold]: P1, P2, M1, M2 (or ALL)")
    paradigms = Prompt.ask("Select", default="ALL")
    if paradigms.upper() == "ALL":
        paradigms = "P1,P2,M1,M2"

    # 5. Select queries
    console.print("\n[bold]5. Queries[/bold]")
    console.print("  [cyan]1[/cyan]. ALL          [dim]Q1-Q41 + QW1-QW12 (53 queries)[/dim]")
    console.print("  [cyan]2[/cyan]. Read only    [dim]Q1-Q41 (41 queries)[/dim]")
    console.print("  [cyan]3[/cyan]. Write only   [dim]QW1-QW12 (12 queries)[/dim]")
    console.print("  [cyan]4[/cyan]. Core         [dim]Q1-Q23 (original 23 queries)[/dim]")
    console.print("  [cyan]5[/cyan]. Custom       [dim]Specify query IDs[/dim]")
    console.print()
    query_choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5"], default="1")

    queries_arg = None  # None = all (default)
    if query_choice == "2":
        queries_arg = ",".join(ALL_READ_QUERIES)
    elif query_choice == "3":
        queries_arg = ",".join(ALL_WRITE_QUERIES)
    elif query_choice == "4":
        queries_arg = ",".join([f"Q{i}" for i in range(1, 24)])
    elif query_choice == "5":
        console.print("[dim]Enter comma-separated query IDs (e.g., Q1,Q2,Q7,QW1)[/dim]")
        queries_arg = Prompt.ask("Queries")

    # 6. Select RAM
    if bench_mode == "1":
        # Single RAM
        console.print("\n[bold]6. RAM (GB)[/bold]")
        console.print(f"[dim]Available: {', '.join(str(l) for l in RAM_LEVELS)}[/dim]")
        ram = Prompt.ask("Select", default="64")
    else:
        # Gradient
        console.print("\n[bold]6. RAM Range[/bold]")
        console.print(f"[dim]Available: {', '.join(str(l) for l in RAM_LEVELS)} GB[/dim]")
        ram_max = Prompt.ask("Max RAM (GB)", default="128")
        ram_min = Prompt.ask("Min RAM (GB)", default="0.5")

        try:
            max_val = float(ram_max)
            min_val = float(ram_min)
            # Ascending order for gradient (low → high, stop at plateau)
            ram_levels = sorted([l for l in RAM_LEVELS if min_val <= l <= max_val])
            ram = ",".join(str(int(l) if l >= 1 else l) for l in ram_levels)
        except ValueError:
            ram = "0.5,1,2,4,8,16,32,64"

    # 6b. Number of runs
    console.print("\n[bold]6b. Number of runs per query[/bold]")
    console.print("[dim]More runs = more stable median, but slower[/dim]")
    n_runs = IntPrompt.ask("Runs", default=5)

    # 7. For Scenario type, select workload
    workload_name = None
    if bench_type == "2":
        console.print("\n[bold]7. Workload[/bold]")
        workloads = [
            ("dashboard_refresh", "Dashboard Refresh", "Read-heavy"),
            ("iot_ingestion", "IoT Ingestion", "Write-heavy"),
            ("mixed_middleware", "Mixed Middleware", "50/50 R/W"),
            ("bos_twin", "BOS Twin", "Digital twin"),
            ("graph_stress", "Graph Stress", "Graph-intensive"),
            ("timeseries_stress", "Timeseries Stress", "TS aggregations"),
        ]
        for i, (name, label, desc) in enumerate(workloads, 1):
            console.print(f"  [cyan]{i}[/cyan]. {label:<20} [dim]{desc}[/dim]")
        console.print()
        wl_idx = IntPrompt.ask("Select", default=4)
        if 1 <= wl_idx <= len(workloads):
            workload_name = workloads[wl_idx - 1][0]
        else:
            workload_name = "bos_twin"

    # Summary
    queries_display = "ALL (46)" if not queries_arg else f"{len(queries_arg.split(','))} queries"
    console.print()
    console.print(Panel.fit(
        f"[bold]Configuration[/bold]\n\n"
        f"Dataset:   {source.name}\n"
        f"Type:      {'Simple' if bench_type == '1' else 'Scenario'}"
        + (f" ({workload_name})" if workload_name else "") + "\n"
        f"Mode:      {'Single RAM' if bench_mode == '1' else 'Gradient'}\n"
        f"Paradigms: {paradigms}\n"
        f"Queries:   {queries_display}\n"
        f"RAM:       {ram} GB\n"
        f"Runs:      {n_runs}",
        border_style="blue"
    ))

    if not Confirm.ask("\nStart?", default=True):
        return

    # Ensure containers are running before starting benchmark
    paradigm_list = [p.strip() for p in paradigms.split(",")]
    if not ensure_containers_running(paradigm_list):
        console.print("[red]Cannot start benchmark: containers not ready[/red]")
        wait()
        return

    # Execute
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    import tempfile
    with tempfile.TemporaryDirectory(prefix="btb_export_") as tmp_export:
        tmp_export_path = Path(tmp_export)
        console.print(f"\n[dim]Temporary export dir: {tmp_export_path}[/dim]")

        if bench_type == "1":
            # Simple benchmark
            type_label = "simple"
            output = RESULTS_DIR / f"{type_label}_{bench_mode == '2' and 'gradient' or 'single'}_{timestamp}.json"

            # Archive raw results for validation replay
            ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

            # Build command
            cmd_args = ["benchmark", "-s", str(source), "-e", str(tmp_export_path), "-o", str(output),
                "-p", paradigms, "--ram", ram, "--runs", str(n_runs), "--variants", "1", "--cleanup",
                "--archive", str(ARCHIVE_DIR)]
            if queries_arg:
                cmd_args.extend(["-q", queries_arg])
            btb(*cmd_args)
        else:
            # Scenario benchmark
            output = RESULTS_DIR / f"scenario_{workload_name}_{timestamp}.json"

            if bench_mode == "1":
                # Single RAM workload
                btb("workload", workload_name, "-s", str(source), "-p", paradigms, "-o", str(output))
            else:
                # Gradient workload (new feature - run workload at each RAM level)
                console.print("\n[yellow]Running workload gradient...[/yellow]")
                ram_list = ram.split(",")
                for ram_level in ram_list:
                    console.print(f"\n[cyan]RAM: {ram_level} GB[/cyan]")
                    level_output = RESULTS_DIR / f"scenario_{workload_name}_{ram_level}gb_{timestamp}.json"
                    # TODO: Need to implement RAM limit for workload
                    # For now, just run workload (RAM limit not yet applied to workload mode)
                    btb("workload", workload_name, "-s", str(source), "-p", paradigms,
                        "-o", str(level_output), "-d", "60")  # 60s per level
                output = RESULTS_DIR / f"scenario_{workload_name}_gradient_{timestamp}"

    console.print("\n[dim]Export directory cleaned.[/dim]")

    # Post-benchmark
    if bench_type == "1" and output and output.exists():
        paradigm_count = len(paradigms.split(","))
        if paradigm_count >= 2:
            console.print()
            console.print(Panel.fit(
                "[bold green]Benchmark Complete![/bold green]\n\n"
                f"Results: {output.name}\n"
                f"Paradigms: {paradigms}",
                border_style="green"
            ))
            console.print()

            if Confirm.ask("[cyan]Run cross-paradigm validation?[/cyan]", default=True):
                run_validation(output)
        else:
            console.print(f"\n[green]Benchmark complete: {output.name}[/green]")
    else:
        console.print(f"\n[green]Workload complete![/green]")

    # Stop containers that were started for this benchmark
    services_to_stop = get_required_services(paradigm_list)
    stop_containers(list(services_to_stop))

    wait()


def debug_query():
    header("Debug Query")

    paradigm = Prompt.ask("Paradigm", choices=PARADIGMS, default="P1")
    query = Prompt.ask("Query ID", default="Q1")

    btb("run-query", query, "-p", paradigm)
    wait()



def run_validation(results_path: Path, generate_reports: bool = True):
    """Run cross-paradigm validation with nice UX."""
    header("Cross-Paradigm Validation")

    console.print(f"[bold]Results:[/bold] {results_path.name}")
    console.print()

    # Ask for validation mode
    console.print("[bold]Validation Mode:[/bold]")
    console.print("  [cyan]1[/cyan]. Cross-Matrix   [dim]All paradigms vs all (A→B, B→A)[/dim]")
    console.print("  [cyan]2[/cyan]. Single Ref     [dim]All vs one reference paradigm[/dim]")
    console.print()
    mode = Prompt.ask("Select", choices=["1", "2"], default="1")

    cross_matrix = (mode == "1")

    if not cross_matrix:
        reference = Prompt.ask("Reference paradigm (P1)", default="P1")

    verbose = Confirm.ask("Verbose output?", default=False)

    # Build command
    cmd_args = ["validate", str(results_path)]

    if cross_matrix:
        cmd_args.append("--cross-matrix")
    else:
        cmd_args.extend(["-r", reference])

    if verbose:
        cmd_args.append("-v")

    # Generate reports if requested
    if generate_reports:
        validation_dir = RESULTS_DIR / "validation"
        validation_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = results_path.stem

        suffix = "cross_matrix" if cross_matrix else "validation"

        json_report = validation_dir / f"{base_name}_{suffix}_{timestamp}.json"
        md_report = validation_dir / f"{base_name}_{suffix}_{timestamp}.md"

        cmd_args.extend(["-o", str(json_report)])
        cmd_args.extend(["--md", str(md_report)])

    console.print()
    btb(*cmd_args)

    if generate_reports:
        console.print()
        console.print(Panel.fit(
            "[bold]Reports Generated:[/bold]\n\n"
            f"JSON: {json_report.name}\n"
            f"MD:   {md_report.name}\n\n"
            f"[dim]Location: {validation_dir}[/dim]",
            border_style="green"
        ))

    wait()


# =============================================================================
# 3. RESULTS
# =============================================================================

def menu_results():
    while True:
        header("Results")

        files = sorted(RESULTS_DIR.glob("*.json"), reverse=True) if RESULTS_DIR.exists() else []
        validation_dir = RESULTS_DIR / "validation"
        validation_reports = list(validation_dir.glob("*.html")) if validation_dir.exists() else []

        if not files:
            console.print("[yellow]No results yet.[/yellow]")
            wait()
            return

        console.print("[bold]Recent Benchmarks:[/bold]")
        for i, f in enumerate(files[:8], 1):
            size_kb = f.stat().st_size / 1024
            # Check if validation exists for this result
            validation_exists = any(f.stem in v.name for v in validation_reports)
            validation_icon = "[green]✓[/green]" if validation_exists else "[dim]·[/dim]"
            console.print(f"  [cyan]{i}[/cyan]. {validation_icon} {f.name} ({size_kb:.0f}KB)")

        if validation_reports:
            console.print(f"\n[dim]{len(validation_reports)} validation reports available[/dim]")

        console.print()
        console.print("[cyan]v[/cyan]. Validate a result       [dim]Cross-paradigm[/dim]")
        console.print("[cyan]e[/cyan]. Validate vs Expected    [dim]Against expected answers[/dim]")
        console.print("[cyan]r[/cyan]. View validation reports")
        console.print("[cyan]a[/cyan]. Archived runs           [dim]Replay validation[/dim]")
        console.print("[cyan]b[/cyan]. Back")
        console.print()

        choice = Prompt.ask("Select result or action", default="1")
        if choice == "b":
            return
        elif choice == "v":
            validate_result_menu(files)
        elif choice == "e":
            validate_expected_menu()
        elif choice == "r":
            view_validation_reports()
        elif choice == "a":
            menu_archived_runs()
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    view_result(files[idx])
            except ValueError:
                pass


def validate_result_menu(files: list[Path]):
    """Menu to select and validate a result file."""
    header("Validate Result")

    if not files:
        console.print("[yellow]No results to validate.[/yellow]")
        wait()
        return

    console.print("[bold]Select result to validate:[/bold]")
    for i, f in enumerate(files[:10], 1):
        console.print(f"  [cyan]{i}[/cyan]. {f.name}")
    console.print()

    choice = IntPrompt.ask("Select", default=1)
    if 1 <= choice <= len(files):
        run_validation(files[choice - 1])


def validate_expected_menu():
    """Validate archived results against expected answers."""
    header("Validate vs Expected Answers")

    # 1. Find datasets with expected_answers
    datasets_with_expected = []
    for ds in list_dirs(GENERATED_DIR):
        expected_dir = ds / "expected_answers"
        if expected_dir.exists() and list(expected_dir.glob("Q*.json")):
            datasets_with_expected.append(ds)

    if not datasets_with_expected:
        console.print("[yellow]No datasets with expected answers found.[/yellow]")
        console.print()
        console.print("[dim]Generate a dataset first - expected answers are computed during generation.[/dim]")
        wait()
        return

    # 2. Find archived runs
    if not ARCHIVE_DIR.exists():
        console.print("[yellow]No archived runs found.[/yellow]")
        console.print("[dim]Run a benchmark with --archive to create archives.[/dim]")
        wait()
        return

    runs = sorted([d for d in ARCHIVE_DIR.iterdir() if d.is_dir()], reverse=True)
    if not runs:
        console.print("[yellow]No archived runs found.[/yellow]")
        wait()
        return

    # 3. Select dataset (expected answers source)
    console.print("[bold]1. Select Dataset:[/bold]")
    for i, ds in enumerate(datasets_with_expected, 1):
        answer_count = len(list((ds / "expected_answers").glob("Q*.json")))
        console.print(f"  [cyan]{i}[/cyan]. {ds.name} [dim]({answer_count} expected answers)[/dim]")
    console.print()

    ds_idx = IntPrompt.ask("Select", default=1)
    if not (1 <= ds_idx <= len(datasets_with_expected)):
        return
    dataset_source = datasets_with_expected[ds_idx - 1]

    # 4. Select archived run
    console.print("\n[bold]2. Select Archived Run to validate:[/bold]")
    for i, run in enumerate(runs[:10], 1):
        # Read metadata for info
        metadata_file = run / "metadata.json"
        info = ""
        if metadata_file.exists():
            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)
                paradigms = ", ".join(metadata.get("config", {}).get("paradigms", [])[:3])
                info = f"[dim]({paradigms})[/dim]"
            except Exception:
                pass
        console.print(f"  [cyan]{i}[/cyan]. {run.name} {info}")
    console.print()

    run_idx = IntPrompt.ask("Select", default=1)
    if not (1 <= run_idx <= len(runs)):
        return
    archive_run = runs[run_idx - 1]

    # 5. Select paradigm (optional)
    console.print("\n[bold]3. Paradigm filter:[/bold]")
    console.print("  [cyan]1[/cyan]. All paradigms")
    console.print("  [cyan]2[/cyan]. Select specific")
    console.print()
    paradigm_choice = Prompt.ask("Select", choices=["1", "2"], default="1")

    paradigm_filter = None
    if paradigm_choice == "2":
        paradigm_filter = Prompt.ask("Paradigm", default="P1")

    # 6. Verbose?
    verbose = Confirm.ask("\nVerbose output?", default=False)

    # 7. Run validation
    console.print()
    console.print(Panel.fit(
        f"[bold]Expected Answers Validation[/bold]\n\n"
        f"Dataset:     {dataset_source.name}\n"
        f"Archive run: {archive_run.name}\n"
        f"Paradigm:    {paradigm_filter or 'ALL'}",
        border_style="blue"
    ))

    if not Confirm.ask("\nRun validation?", default=True):
        return

    # Build command
    cmd_args = ["validate-expected", "--archive", str(archive_run), "--dataset", str(dataset_source)]

    if paradigm_filter:
        cmd_args.extend(["--paradigm", paradigm_filter])

    # Output
    validation_dir = RESULTS_DIR / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = validation_dir / f"expected_{archive_run.name}_{timestamp}.json"
    cmd_args.extend(["--output", str(output)])

    if verbose:
        cmd_args.append("--verbose")

    console.print()
    btb(*cmd_args)

    console.print(f"\n[green]Report saved: {output.name}[/green]")
    wait()


def menu_archived_runs():
    """Menu to view and replay validation on archived runs."""
    header("Archived Runs")

    if not ARCHIVE_DIR.exists():
        console.print("[yellow]No archived runs yet.[/yellow]")
        console.print("[dim]Run a benchmark to create archives.[/dim]")
        wait()
        return

    # List archived runs
    runs = sorted([d for d in ARCHIVE_DIR.iterdir() if d.is_dir()], reverse=True)
    if not runs:
        console.print("[yellow]No archived runs found.[/yellow]")
        wait()
        return

    console.print("[bold]Archived Runs:[/bold]")
    for i, run in enumerate(runs[:10], 1):
        # Try to read metadata
        metadata_file = run / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)
                paradigms = ", ".join(metadata.get("config", {}).get("paradigms", [])[:3])
                queries = len(metadata.get("config", {}).get("queries", []))
                git = metadata.get("environment", {}).get("git_hash", "")[:7]
                console.print(f"  [cyan]{i}[/cyan]. {run.name} [dim]({paradigms}, {queries}Q, git:{git})[/dim]")
            except Exception:
                console.print(f"  [cyan]{i}[/cyan]. {run.name}")
        else:
            console.print(f"  [cyan]{i}[/cyan]. {run.name}")

    console.print()
    console.print("[cyan]b[/cyan]. Back")
    console.print()

    choice = Prompt.ask("Select run to replay validation", default="b")
    if choice == "b":
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(runs):
            replay_validation(runs[idx])
    except ValueError:
        pass


def replay_validation(run_path: Path):
    """Replay validation on an archived run."""
    header(f"Replay: {run_path.name}")

    console.print(f"[bold]Run:[/bold] {run_path.name}")

    # Show run info
    metadata_file = run_path / "metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
            config = metadata.get("config", {})
            console.print(f"[dim]Paradigms: {', '.join(config.get('paradigms', []))}[/dim]")
            console.print(f"[dim]Queries: {len(config.get('queries', []))}[/dim]")
            console.print(f"[dim]Git: {metadata.get('environment', {}).get('git_hash', '?')}[/dim]")
        except Exception:
            pass

    console.print()

    # Options
    semantic = Confirm.ask("Use semantic validation?", default=True)
    reference = Prompt.ask("Reference paradigm", default="P1")

    # Output
    validation_dir = RESULTS_DIR / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = validation_dir / f"replay_{run_path.name}_{timestamp}.json"

    # Run replay
    cmd_args = ["replay", run_path.name, "-d", str(ARCHIVE_DIR), "-r", reference, "-o", str(output)]
    if semantic:
        cmd_args.append("--semantic")
    else:
        cmd_args.append("--no-semantic")

    console.print()
    btb(*cmd_args)

    console.print(f"\n[green]Report saved: {output.name}[/green]")
    wait()


def view_validation_reports():
    """View available validation reports."""
    header("Validation Reports")

    validation_dir = RESULTS_DIR / "validation"
    if not validation_dir.exists():
        console.print("[yellow]No validation reports yet.[/yellow]")
        wait()
        return

    md_reports = sorted(validation_dir.glob("*.md"), reverse=True)
    json_reports = sorted(validation_dir.glob("*.json"), reverse=True)

    if not md_reports and not json_reports:
        console.print("[yellow]No validation reports yet.[/yellow]")
        wait()
        return

    console.print("[bold]Markdown Reports:[/bold]")
    for i, f in enumerate(md_reports[:5], 1):
        console.print(f"  [cyan]{i}[/cyan]. {f.name}")

    console.print()
    console.print("[bold]JSON Reports (raw data):[/bold]")
    for f in json_reports[:5]:
        console.print(f"  [dim]{f.name}[/dim]")

    console.print()
    console.print(f"[dim]Location: {validation_dir}[/dim]")

    wait()


def view_result(path: Path):
    header(f"Result: {path.name}")

    try:
        with open(path) as f:
            data = json.load(f)

        # Config
        if "config" in data:
            cfg = data["config"]
            console.print("[bold]Config:[/bold]")
            console.print(f"  Paradigms: {', '.join(cfg.get('paradigms', []))}")
            ram_levels = cfg.get('ram_levels_mb', [])
            ram_str = ", ".join(f"{r//1024}GB" for r in ram_levels) if ram_levels else "?"
            console.print(f"  RAM: {ram_str}")
            console.print(f"  Runs: {cfg.get('n_runs', '?')}")
            console.print()

        # Summary - RAM Viable
        if "summary" in data:
            console.print("[bold]RAM Viable (min without OOM):[/bold]")
            table = Table(show_header=True, header_style="bold")
            table.add_column("Paradigm")
            table.add_column("RAM", justify="right")

            for p, ram in data["summary"].get("ram_viable", {}).items():
                if ram:
                    table.add_row(p, f"[green]{ram//1024} GB[/green]")
                else:
                    table.add_row(p, "[red]FAIL[/red]")
            console.print(table)

        # Check for validation status
        validation_dir = RESULTS_DIR / "validation"
        validation_json = None
        if validation_dir.exists():
            for v in validation_dir.glob(f"{path.stem}_validation_*.json"):
                validation_json = v
                break

        console.print()

        if validation_json:
            # Show validation summary
            try:
                with open(validation_json) as f:
                    val_data = json.load(f)
                summary = val_data.get("summary", {})

                console.print("[bold]Validation Status:[/bold] [green]✓ Validated[/green]")
                console.print(f"  Equivalent: [green]{summary.get('equivalent', 0)}[/green]")
                console.print(f"  Degraded:   [yellow]{summary.get('degraded', 0)}[/yellow]")
                console.print(f"  Skip:       [dim]{summary.get('skip', 0)}[/dim]")
                console.print(f"  Mismatch:   [red]{summary.get('mismatch', 0)}[/red]")

                if summary.get('mismatch', 0) == 0:
                    console.print("\n[green]All queries validate successfully![/green]")
                else:
                    console.print(f"\n[red]Warning: {summary.get('mismatch', 0)} mismatches found[/red]")
            except Exception:
                console.print("[yellow]Validation report exists but could not be parsed[/yellow]")
        else:
            console.print("[bold]Validation Status:[/bold] [dim]Not validated[/dim]")
            paradigms = cfg.get('paradigms', []) if "config" in data else []
            if len(paradigms) >= 2:
                console.print("[dim]Run validation from Results menu (v)[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

    console.print()
    choice = Prompt.ask("[cyan]v[/cyan]=Validate  [cyan]b[/cyan]=Back", default="b", show_choices=False)
    if choice == "v":
        run_validation(path)
    else:
        return


# =============================================================================
# 4. SYSTEM
# =============================================================================

def get_container_status() -> dict[str, dict]:
    """Get detailed container status for benchmark containers."""
    containers = {}
    compose_file = PROJECT_DIR / "docker" / "docker-compose.yml"

    try:
        # Get container list with detailed info
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "ps", "--format", "json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            import json as json_module
            # Parse JSON output (one JSON object per line)
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    try:
                        info = json_module.loads(line)
                        name = info.get("Name", info.get("Service", "unknown"))
                        containers[name] = {
                            "status": info.get("State", info.get("Status", "unknown")),
                            "health": info.get("Health", ""),
                            "ports": info.get("Publishers", []),
                        }
                    except json_module.JSONDecodeError:
                        pass
    except Exception:
        pass

    # Fallback to simple ps if JSON didn't work
    if not containers:
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "ps", "--format",
                 "table {{.Name}}\t{{.State}}\t{{.Health}}"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n")[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        status = parts[1] if len(parts) > 1 else "unknown"
                        health = parts[2] if len(parts) > 2 else ""
                        containers[name] = {"status": status, "health": health, "ports": []}
        except Exception:
            pass

    return containers


def get_required_services(paradigms: list[str]) -> set[str]:
    """Get the set of required container services for given paradigms."""
    paradigm_to_services = {
        "P1": ["timescale"],
        "P2": ["timescale"],
        "M1": ["memgraph"],
        "M2": ["memgraph", "timescale"],  # Hybrid: graph + timeseries
        # O2 is exploratory only - not included in standard benchmarks
        # "O2": ["oxigraph", "timescale"],  # Hybrid: RDF + timeseries
    }
    required = set()
    for p in paradigms:
        if p in paradigm_to_services:
            required.update(paradigm_to_services[p])
    return required


def ensure_containers_running(paradigms: list[str]) -> bool:
    """Ensure required containers are running for the selected paradigms.

    Auto-starts containers if needed. Returns True if all containers are ready.
    """
    compose_file = PROJECT_DIR / "docker" / "docker-compose.yml"

    # Get required services
    required_services = get_required_services(paradigms)

    if not required_services:
        return True

    # Check current status
    containers = get_container_status()

    # Find services that need starting
    services_to_start = []
    for service in required_services:
        container_name = f"benchmark-{service}"
        status = containers.get(container_name, {})
        state = status.get("status", "").lower()
        health = status.get("health", "").lower()

        # Check if running and healthy
        if "running" not in state or ("unhealthy" in health):
            services_to_start.append(service)

    if not services_to_start:
        return True

    # Auto-start required services
    console.print(f"\n[yellow]Starting required containers: {', '.join(services_to_start)}[/yellow]")

    try:
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "up", "-d"] + services_to_start,
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            console.print(f"[red]Failed to start containers: {result.stderr}[/red]")
            return False
    except subprocess.TimeoutExpired:
        console.print("[red]Timeout starting containers[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Error starting containers: {e}[/red]")
        return False

    # Wait for containers to be healthy
    console.print("[dim]Waiting for containers to be healthy...[/dim]")
    import time
    max_wait = 60  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait:
        containers = get_container_status()
        all_healthy = True

        for service in required_services:
            container_name = f"benchmark-{service}"
            status = containers.get(container_name, {})
            state = status.get("status", "").lower()
            health = status.get("health", "").lower()

            if "running" not in state:
                all_healthy = False
                break
            # Some containers might not have health checks
            if health and "healthy" not in health and "starting" not in health:
                all_healthy = False
                break
            if "starting" in health:
                all_healthy = False
                break

        if all_healthy:
            console.print("[green]All containers ready![/green]")
            return True

        time.sleep(2)

    console.print("[red]Timeout waiting for containers to be healthy[/red]")
    return False


def stop_containers(services: list[str]) -> None:
    """Stop specified containers after benchmark completes."""
    if not services:
        return

    compose_file = PROJECT_DIR / "docker" / "docker-compose.yml"
    console.print(f"\n[dim]Stopping containers: {', '.join(services)}[/dim]")

    try:
        subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "stop"] + list(services),
            capture_output=True, text=True, timeout=30
        )
    except Exception as e:
        console.print(f"[yellow]Warning: Could not stop containers: {e}[/yellow]")


def docker_prune_all() -> bool:
    """Stop all benchmark containers and remove volumes for clean slate.

    Returns True if successful.
    """
    compose_file = PROJECT_DIR / "docker" / "docker-compose.yml"

    console.print("[yellow]Cleaning Docker state...[/yellow]")

    try:
        # Stop all services and remove volumes
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "down", "-v", "--remove-orphans"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0 and result.stderr:
            console.print(f"[yellow]Warning: {result.stderr.strip()}[/yellow]")

        # Also remove any orphan benchmark volumes
        vol_result = subprocess.run(
            ["docker", "volume", "ls", "-q"],
            capture_output=True, text=True
        )
        for vol in vol_result.stdout.strip().split("\n"):
            if vol and ("benchmark" in vol.lower() or "basetype" in vol.lower()):
                subprocess.run(["docker", "volume", "rm", "-f", vol], capture_output=True)

        console.print("[green]Docker state cleaned![/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to clean Docker state: {e}[/red]")
        return False


def get_docker_status_summary() -> tuple[int, int, list[str]]:
    """Get current Docker status for benchmark containers.

    Returns:
        (container_count, volume_count, container_status_list)
    """
    compose_file = PROJECT_DIR / "docker" / "docker-compose.yml"
    container_status = []
    volumes = 0

    try:
        # Get containers with status
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "ps", "-a", "--format", "{{.Name}}:{{.State}}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line:
                    container_status.append(line)

        # Count benchmark volumes
        vol_result = subprocess.run(
            ["docker", "volume", "ls", "-q"],
            capture_output=True, text=True
        )
        for vol in vol_result.stdout.strip().split("\n"):
            if vol and ("benchmark" in vol.lower() or "basetype" in vol.lower()):
                volumes += 1

    except Exception:
        pass

    return len(container_status), volumes, container_status


def get_volume_info() -> dict[str, str]:
    """Get Docker volume sizes for benchmark."""
    volumes = {}
    try:
        result = subprocess.run(
            ["docker", "volume", "ls", "--format", "{{.Name}}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for vol_name in result.stdout.strip().split("\n"):
                if "benchmark" in vol_name.lower() or "basetype" in vol_name.lower():
                    # Get volume size
                    inspect = subprocess.run(
                        ["docker", "system", "df", "-v", "--format", "{{.Name}}\t{{.Size}}"],
                        capture_output=True, text=True, timeout=10
                    )
                    volumes[vol_name] = "?"
    except Exception:
        pass
    return volumes


def menu_system():
    while True:
        header("System / Containers")

        # Docker daemon check
        docker_ok = subprocess.run(["docker", "info"], capture_output=True).returncode == 0

        if not docker_ok:
            console.print("[red]⚠ Docker daemon not running![/red]")
            console.print()
            console.print("[cyan]b[/cyan]. Back")
            console.print()
            if Prompt.ask("", default="b") == "b":
                return
            continue

        # Get container status
        containers = get_container_status()

        # Display container status table
        console.print("[bold]Container Status:[/bold]")
        if containers:
            table = Table(show_header=True, header_style="bold", box=None)
            table.add_column("Container", style="cyan")
            table.add_column("Status")
            table.add_column("Health")
            table.add_column("Schema")

            for name, info in sorted(containers.items()):
                status = info.get("status", "unknown")
                health = info.get("health", "")

                # Status color
                if status in ("running", "Up"):
                    status_str = f"[green]● {status}[/green]"
                elif status in ("exited", "Exit"):
                    status_str = f"[red]○ {status}[/red]"
                else:
                    status_str = f"[yellow]? {status}[/yellow]"

                # Health color
                if health == "healthy":
                    health_str = "[green]healthy[/green]"
                elif health == "unhealthy":
                    health_str = "[red]unhealthy[/red]"
                elif health:
                    health_str = f"[yellow]{health}[/yellow]"
                else:
                    health_str = "[dim]-[/dim]"

                # Schema info (for timescale)
                schema_str = "[dim]-[/dim]"
                if "timescale" in name.lower() and status in ("running", "Up"):
                    schema_str = "[green]p1,p2,ts[/green]"

                table.add_row(name, status_str, health_str, schema_str)

            console.print(table)
        else:
            console.print("  [dim]No containers running[/dim]")

        # RAM info
        console.print()
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        mem_gb = int(line.split()[1]) / 1024 / 1024
                        console.print(f"[bold]RAM available:[/bold] {mem_gb:.0f} GB")
        except:
            pass

        console.print()
        console.print("[bold]Actions:[/bold]")
        console.print("[cyan]1[/cyan]. Start containers      [dim]docker compose up -d[/dim]")
        console.print("[cyan]2[/cyan]. Stop containers       [dim]docker compose down[/dim]")
        console.print("[cyan]3[/cyan]. Restart containers    [dim]down + up[/dim]")
        console.print("[cyan]4[/cyan]. [yellow]Reset volumes[/yellow]        [dim]down -v (deletes data!)[/dim]")
        console.print()
        console.print("[cyan]l[/cyan]. Container logs")
        console.print("[cyan]s[/cyan]. Schema status         [dim]Check DB schemas[/dim]")
        console.print("[cyan]i[/cyan]. Full system info")
        console.print()
        console.print("[cyan]b[/cyan]. Back")
        console.print()

        choice = Prompt.ask("", choices=["1", "2", "3", "4", "l", "s", "i", "b"], default="1", show_choices=False)

        if choice == "b":
            return

        compose = ["docker", "compose", "-f", str(PROJECT_DIR / "docker" / "docker-compose.yml")]

        if choice == "1":
            console.print("\n[cyan]Starting containers...[/cyan]")
            run_cmd(compose + ["up", "-d"])
        elif choice == "2":
            console.print("\n[cyan]Stopping containers...[/cyan]")
            run_cmd(compose + ["down"])
        elif choice == "3":
            console.print("\n[cyan]Restarting containers...[/cyan]")
            run_cmd(compose + ["down"])
            run_cmd(compose + ["up", "-d"])
        elif choice == "4":
            console.print()
            console.print("[bold red]⚠ WARNING: This will delete all container data![/bold red]")
            console.print("[yellow]This includes:[/yellow]")
            console.print("  - PostgreSQL/TimescaleDB data")
            console.print("  - Memgraph data")
            console.print("  - All loaded datasets")
            console.print()
            if Confirm.ask("[red]Are you sure you want to reset volumes?[/red]", default=False):
                console.print("\n[cyan]Removing containers and volumes...[/cyan]")
                run_cmd(compose + ["down", "-v"])
                console.print("[green]Volumes reset. Schema will be recreated on next benchmark.[/green]")
            else:
                console.print("[dim]Cancelled.[/dim]")
        elif choice == "l":
            service = Prompt.ask("Service [dim](timescale/memgraph/oxigraph/all)[/dim]", default="all")
            if service == "all":
                run_cmd(compose + ["logs", "--tail=50"])
            else:
                run_cmd(compose + ["logs", "--tail=50", service])
        elif choice == "s":
            check_schema_status()
        elif choice == "i":
            show_system_info()

        wait()


def check_schema_status():
    """Check database schema status."""
    header("Schema Status")

    console.print("[bold]Checking PostgreSQL schemas...[/bold]")
    console.print()

    try:
        import psycopg

        # Try to connect
        dsn = "postgresql://postgres:postgres@localhost:5432/benchmark"
        with psycopg.connect(dsn, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                # List schemas
                cur.execute("""
                    SELECT schema_name FROM information_schema.schemata
                    WHERE schema_name IN ('p1', 'p2', 'ts', 'public')
                    ORDER BY schema_name
                """)
                schemas = [row[0] for row in cur.fetchall()]

                console.print(f"[green]✓ Connected to PostgreSQL[/green]")
                console.print(f"  Schemas: {', '.join(schemas) if schemas else '[dim]none[/dim]'}")
                console.print()

                # Check P1 tables and columns
                if 'p1' in schemas:
                    console.print("[bold]P1 Schema:[/bold]")
                    cur.execute("""
                        SELECT table_name FROM information_schema.tables
                        WHERE table_schema = 'p1' ORDER BY table_name
                    """)
                    tables = [row[0] for row in cur.fetchall()]
                    console.print(f"  Tables: {', '.join(tables[:8])}{'...' if len(tables) > 8 else ''}")

                    # Check for new columns
                    cur.execute("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_schema = 'p1' AND table_name = 'spaces' AND column_name = 'is_exit'
                    """)
                    has_is_exit = cur.fetchone() is not None

                    cur.execute("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_schema = 'p1' AND table_name = 'equipment' AND column_name = 'critical'
                    """)
                    has_critical = cur.fetchone() is not None

                    cur.execute("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_schema = 'p1' AND table_name = 'edges' AND column_name = 'distance'
                    """)
                    has_distance = cur.fetchone() is not None

                    console.print(f"  spaces.is_exit: {'[green]✓[/green]' if has_is_exit else '[red]✗ missing[/red]'}")
                    console.print(f"  equipment.critical: {'[green]✓[/green]' if has_critical else '[red]✗ missing[/red]'}")
                    console.print(f"  edges.distance: {'[green]✓[/green]' if has_distance else '[red]✗ missing[/red]'}")

                    if not has_is_exit or not has_critical or not has_distance:
                        console.print()
                        console.print("[yellow]⚠ Schema needs migration. Options:[/yellow]")
                        console.print("  1. Run benchmark (auto-migrates)")
                        console.print("  2. Reset volumes (System > Reset volumes)")
                    console.print()

                # Check P2 tables
                if 'p2' in schemas:
                    console.print("[bold]P2 Schema:[/bold]")
                    cur.execute("""
                        SELECT table_name FROM information_schema.tables
                        WHERE table_schema = 'p2' ORDER BY table_name
                    """)
                    tables = [row[0] for row in cur.fetchall()]
                    console.print(f"  Tables: {', '.join(tables)}")
                    console.print()

                # Check timeseries
                if 'ts' in schemas:
                    console.print("[bold]TS Schema (TimescaleDB):[/bold]")
                    cur.execute("SELECT COUNT(*) FROM ts.timeseries")
                    ts_count = cur.fetchone()[0]
                    console.print(f"  Timeseries rows: {ts_count:,}")
                    console.print()

    except ImportError:
        console.print("[yellow]psycopg not installed. Run: pip install psycopg[/yellow]")
    except Exception as e:
        console.print(f"[red]Cannot connect to PostgreSQL: {e}[/red]")
        console.print("[dim]Is TimescaleDB container running?[/dim]")


def show_system_info():
    header("System Info")

    import platform
    console.print(f"OS: {platform.system()} {platform.release()}")
    console.print(f"Python: {platform.python_version()}")
    console.print(f"CPUs: {os.cpu_count()}")

    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    console.print(f"RAM total: {int(line.split()[1])/1024/1024:.0f} GB")
                if line.startswith("MemAvailable:"):
                    console.print(f"RAM free: {int(line.split()[1])/1024/1024:.0f} GB")
    except:
        pass

    try:
        total, used, free = shutil.disk_usage("/")
        console.print(f"Disk: {free/1024**3:.0f} GB free / {total/1024**3:.0f} GB")
    except:
        pass

    console.print()
    console.print(f"Data: {DATA_DIR}")
    console.print(f"cgroups v2: {'OK' if Path('/sys/fs/cgroup/cgroup.controllers').exists() else 'No'}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    args = parse_args()
    if args.version:
        console.print("BaseType Benchmark V3 - 2025.1.0")
        return

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        choice = main_menu()

        if choice == "q":
            console.print("\n[dim]Bye![/dim]")
            break
        elif choice == "h":
            show_help()
            wait()
        elif choice == "1":
            menu_dataset()
        elif choice == "2":
            menu_benchmark()
        elif choice == "3":
            menu_results()
        elif choice == "4":
            menu_system()


if __name__ == "__main__":
    main()
