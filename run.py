#!/usr/bin/env python3
"""BaseType Benchmark V3 - Interactive Runner.

Simple, iterative workflow following the natural benchmark process.
"""
from __future__ import annotations

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

# Paths
PROJECT_DIR = Path(__file__).parent
VENV_PYTHON = PROJECT_DIR / ".venv" / "bin" / "python"
VENV_BTB = PROJECT_DIR / ".venv" / "bin" / "btb-runner"
CONFIG_DIR = PROJECT_DIR / "config"
DATA_DIR = Path(os.environ.get("BTB_DATA_DIR", PROJECT_DIR / "data"))
GENERATED_DIR = DATA_DIR / "generated"
RESULTS_DIR = DATA_DIR / "results"
# Note: Exports are now on-demand in temporary directories during benchmark

PROFILES = ["small", "medium", "large", "xlarge"]
DURATIONS = ["2d", "1w", "1m", "6m", "1y"]
PARADIGMS = ["P1", "P2", "M1", "M2", "O2"]
SCENARIOS_DIR = CONFIG_DIR / "scenarios"

# All 23 query IDs for reference
ALL_QUERIES = [f"Q{i}" for i in range(1, 24)]


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
    console.print("[cyan]q[/cyan]. Quit")
    console.print()

    return Prompt.ask("", choices=["1", "2", "3", "4", "q"], default="1", show_choices=False)


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
    console.print("\n[bold]4. Paradigms[/bold]: P1, P2, M1, M2, O2 (or ALL)")
    paradigms = Prompt.ask("Select", default="ALL")
    if paradigms.upper() == "ALL":
        paradigms = "P1,P2,M1,M2,O2"

    # 5. Select RAM
    if bench_mode == "1":
        # Single RAM
        console.print("\n[bold]5. RAM (GB)[/bold]")
        console.print(f"[dim]Available: {', '.join(str(l) for l in RAM_LEVELS)}[/dim]")
        ram = Prompt.ask("Select", default="64")
    else:
        # Gradient
        console.print("\n[bold]5. RAM Range[/bold]")
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

    # 6. For Scenario type, select workload
    workload_name = None
    if bench_type == "2":
        console.print("\n[bold]6. Workload[/bold]")
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
    console.print()
    console.print(Panel.fit(
        f"[bold]Configuration[/bold]\n\n"
        f"Dataset:   {source.name}\n"
        f"Type:      {'Simple' if bench_type == '1' else 'Scenario'}"
        + (f" ({workload_name})" if workload_name else "") + "\n"
        f"Mode:      {'Single RAM' if bench_mode == '1' else 'Gradient'}\n"
        f"Paradigms: {paradigms}\n"
        f"RAM:       {ram} GB",
        border_style="blue"
    ))

    if not Confirm.ask("\nStart?", default=True):
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

            btb("benchmark", "-s", str(source), "-e", str(tmp_export_path), "-o", str(output),
                "-p", paradigms, "--ram", ram, "--runs", "5", "--cleanup")
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

    # Ask for options
    reference = Prompt.ask("Reference paradigm", default="P1")
    verbose = Confirm.ask("Verbose output?", default=False)

    # Build command
    cmd_args = ["validate", str(results_path), "-r", reference]

    if verbose:
        cmd_args.append("-v")

    # Generate reports if requested
    if generate_reports:
        validation_dir = RESULTS_DIR / "validation"
        validation_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = results_path.stem

        json_report = validation_dir / f"{base_name}_validation_{timestamp}.json"
        html_report = validation_dir / f"{base_name}_validation_{timestamp}.html"

        cmd_args.extend(["-o", str(json_report)])
        cmd_args.extend(["--html", str(html_report)])

    console.print()
    btb(*cmd_args)

    if generate_reports:
        console.print()
        console.print(Panel.fit(
            "[bold]Reports Generated:[/bold]\n\n"
            f"JSON: {json_report.name}\n"
            f"HTML: {html_report.name}\n\n"
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
        console.print("[cyan]v[/cyan]. Validate a result")
        console.print("[cyan]r[/cyan]. View validation reports")
        console.print("[cyan]b[/cyan]. Back")
        console.print()

        choice = Prompt.ask("Select result or action", default="1")
        if choice == "b":
            return
        elif choice == "v":
            validate_result_menu(files)
        elif choice == "r":
            view_validation_reports()
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


def view_validation_reports():
    """View available validation reports."""
    header("Validation Reports")

    validation_dir = RESULTS_DIR / "validation"
    if not validation_dir.exists():
        console.print("[yellow]No validation reports yet.[/yellow]")
        wait()
        return

    html_reports = sorted(validation_dir.glob("*.html"), reverse=True)
    json_reports = sorted(validation_dir.glob("*.json"), reverse=True)

    if not html_reports and not json_reports:
        console.print("[yellow]No validation reports yet.[/yellow]")
        wait()
        return

    console.print("[bold]HTML Reports (for publication):[/bold]")
    for i, f in enumerate(html_reports[:5], 1):
        console.print(f"  [cyan]{i}[/cyan]. {f.name}")

    console.print()
    console.print("[bold]JSON Reports (detailed data):[/bold]")
    for f in json_reports[:5]:
        console.print(f"  [dim]{f.name}[/dim]")

    console.print()
    console.print(f"[dim]Location: {validation_dir}[/dim]")
    console.print()

    if html_reports:
        if Confirm.ask("Open latest HTML report in browser?", default=False):
            import webbrowser
            webbrowser.open(f"file://{html_reports[0].absolute()}")

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

def menu_system():
    while True:
        header("System")

        # Quick status
        docker_ok = subprocess.run(["docker", "info"], capture_output=True).returncode == 0
        console.print(f"Docker: {'[green]OK[/green]' if docker_ok else '[red]DOWN[/red]'}")

        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        mem_gb = int(line.split()[1]) / 1024 / 1024
                        console.print(f"RAM free: {mem_gb:.0f} GB")
        except:
            pass

        console.print()
        console.print("[cyan]1[/cyan]. Docker status")
        console.print("[cyan]2[/cyan]. Start containers")
        console.print("[cyan]3[/cyan]. Stop containers")
        console.print("[cyan]4[/cyan]. Container logs")
        console.print()
        console.print("[cyan]i[/cyan]. Full system info")
        console.print()
        console.print("[cyan]b[/cyan]. Back")
        console.print()

        choice = Prompt.ask("", choices=["1", "2", "3", "4", "i", "b"], default="1", show_choices=False)

        if choice == "b":
            return

        compose = ["docker", "compose", "-f", str(PROJECT_DIR / "docker" / "docker-compose.yml")]

        if choice == "1":
            run_cmd(compose + ["ps"])
        elif choice == "2":
            run_cmd(compose + ["up", "-d"])
        elif choice == "3":
            run_cmd(compose + ["down"])
        elif choice == "4":
            run_cmd(compose + ["logs", "--tail=30"])
        elif choice == "i":
            show_system_info()

        wait()


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
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        choice = main_menu()

        if choice == "q":
            console.print("\n[dim]Bye![/dim]")
            break
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
