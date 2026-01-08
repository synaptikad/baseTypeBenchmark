#!/usr/bin/env python3
"""Interactive Benchmark Runner V3.

Complete menu-driven interface for:
- Dataset generation (profile + duration)
- Data export to paradigm formats
- Data loading
- Benchmark execution
- Results management
"""
from __future__ import annotations

import subprocess
import sys
import shutil
import json
import os
from pathlib import Path
from datetime import datetime

# Rich for beautiful menus
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    print("Installing rich...")
    subprocess.run([sys.executable, "-m", "pip", "install", "rich", "-q"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Paths
PROJECT_DIR = Path(__file__).parent
VENV_PYTHON = PROJECT_DIR / ".venv" / "bin" / "python"
VENV_BTB = PROJECT_DIR / ".venv" / "bin" / "btb-runner"
CONFIG_DIR = PROJECT_DIR / "config"
DATA_DIR = Path(os.environ.get("BTB_DATA_DIR", PROJECT_DIR / "data"))
GENERATED_DIR = DATA_DIR / "generated"
EXPORT_DIR = DATA_DIR / "exports"
RESULTS_DIR = DATA_DIR / "results"

# Profiles and durations
PROFILES = ["small", "medium", "large", "xlarge"]
DURATIONS = ["2d", "1w", "1m", "6m", "1y"]
PARADIGMS = ["P1", "P2", "M1", "M2", "O2"]


def run_command(cmd: list[str], capture: bool = False) -> int:
    """Run a command and return exit code."""
    console.print(f"[dim]$ {' '.join(str(c) for c in cmd)}[/dim]\n")
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[red]{result.stderr}[/red]")
        return result.returncode
    return subprocess.run(cmd).returncode


def btb(*args) -> int:
    """Run btb-runner command."""
    cmd = [str(VENV_BTB)] + [str(a) for a in args]
    return run_command(cmd)


def python_module(module: str, *args) -> int:
    """Run a Python module."""
    cmd = [str(VENV_PYTHON), "-m", module] + [str(a) for a in args]
    return run_command(cmd)


def show_header():
    """Show application header."""
    console.clear()
    console.print(Panel.fit(
        "[bold blue]BaseType Benchmark V3[/bold blue]\n"
        "[dim]Interactive Runner - Full Feature Menu[/dim]",
        border_style="blue"
    ))
    console.print()


def show_main_menu() -> str:
    """Show main menu and return choice."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="cyan bold", width=4)
    table.add_column("Action")
    table.add_column("Description", style="dim")

    # Quick actions
    table.add_row("[bold]BENCHMARK[/bold]", "", "")
    table.add_row("r", "Run Benchmark", "Quick/Standard/Custom scenarios")
    table.add_row("g", "RAM Gradient", "Fine-grained RAM testing")
    table.add_row("", "", "")

    # Preparation
    table.add_row("[bold]PREPARATION[/bold]", "", "")
    table.add_row("1", "Generate Dataset", "Create synthetic building data")
    table.add_row("2", "Export Dataset", "Convert to paradigm formats")
    table.add_row("3", "Load Data", "Direct database load")
    table.add_row("", "", "")

    # Validation
    table.add_row("[bold]VALIDATION[/bold]", "", "")
    table.add_row("v", "Validate Queries", "Dry-run and matrix")
    table.add_row("t", "Golden Tests", "Reproducibility validation")
    table.add_row("d", "Debug Query", "Run single query")
    table.add_row("", "", "")

    # Results
    table.add_row("[bold]RESULTS[/bold]", "", "")
    table.add_row("5", "View Results", "Browse benchmark results")
    table.add_row("s", "Summary Report", "Generate summary")
    table.add_row("", "", "")

    # System
    table.add_row("[bold]SYSTEM[/bold]", "", "")
    table.add_row("6", "Docker", "Container management")
    table.add_row("4", "Manage Datasets", "List/delete data")
    table.add_row("i", "System Info", "Check status")
    table.add_row("p", "Profiles Info", "Engine profiles")
    table.add_row("", "", "")

    table.add_row("q", "Quit", "")

    console.print(table)
    console.print()

    return Prompt.ask("Select", choices=["r", "g", "1", "2", "3", "v", "t", "d", "5", "s", "6", "4", "i", "p", "q"], default="r")


# =============================================================================
# 1. GENERATE DATASET
# =============================================================================

def menu_generate():
    """Dataset generation menu."""
    show_header()
    console.print("[bold]1. Generate Dataset[/bold]\n")

    # Show available profiles
    console.print("[cyan]Available profiles:[/cyan]")
    for p in PROFILES:
        profile_path = CONFIG_DIR / "profiles" / f"{p}.yaml"
        if profile_path.exists():
            console.print(f"  - {p}")

    profile = Prompt.ask("\nProfile", choices=PROFILES, default="small")

    # Show durations
    console.print("\n[cyan]Available durations:[/cyan]")
    for d in DURATIONS:
        console.print(f"  - {d}")

    duration = Prompt.ask("\nDuration", choices=DURATIONS, default="1w")

    # Seed
    seed = IntPrompt.ask("Seed (for reproducibility)", default=42)

    # Confirm
    console.print(f"\n[yellow]Will generate:[/yellow]")
    console.print(f"  Profile: {profile}")
    console.print(f"  Duration: {duration}")
    console.print(f"  Seed: {seed}")
    console.print(f"  Output: {GENERATED_DIR / profile}-{duration}")

    if not Confirm.ask("\nProceed?", default=True):
        return

    # Create output directory
    output_dir = GENERATED_DIR / f"{profile}-{duration}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run generator
    console.print("\n[bold]Generating dataset...[/bold]\n")
    python_module(
        "src.basetype_benchmark.dataset.generator",
        "--profile", profile,
        "--duration", duration,
        "--seed", str(seed),
        "--config-dir", str(CONFIG_DIR),
        "--output", str(GENERATED_DIR),
        "--format", "parquet"
    )

    console.print(f"\n[green]Dataset generated: {output_dir}[/green]")
    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


# =============================================================================
# 2. EXPORT DATASET
# =============================================================================

def menu_export():
    """Export dataset to paradigm formats."""
    show_header()
    console.print("[bold]2. Export Dataset[/bold]\n")

    # List available generated datasets
    datasets = list_datasets(GENERATED_DIR)
    if not datasets:
        console.print("[yellow]No generated datasets found. Generate one first.[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    console.print("[cyan]Available datasets:[/cyan]")
    for i, ds in enumerate(datasets, 1):
        console.print(f"  {i}. {ds.name}")

    choice = IntPrompt.ask("\nSelect dataset", default=1)
    if choice < 1 or choice > len(datasets):
        return

    source_dir = datasets[choice - 1]

    # Select paradigms to export
    console.print("\n[cyan]Export to paradigms:[/cyan]")
    for i, p in enumerate(PARADIGMS, 1):
        console.print(f"  {i}. {p}")
    console.print(f"  a. All")

    paradigm_choice = Prompt.ask("\nSelect", choices=[str(i) for i in range(1, 6)] + ["a"], default="a")

    if paradigm_choice == "a":
        selected_paradigms = PARADIGMS
    else:
        selected_paradigms = [PARADIGMS[int(paradigm_choice) - 1]]

    # Confirm
    console.print(f"\n[yellow]Will export {source_dir.name} to: {', '.join(selected_paradigms)}[/yellow]")

    if not Confirm.ask("\nProceed?", default=True):
        return

    # Run exporters
    for paradigm in selected_paradigms:
        console.print(f"\n[bold]Exporting to {paradigm}...[/bold]")
        output_dir = EXPORT_DIR / paradigm.lower() / source_dir.name

        if paradigm in ("P1", "P2"):
            python_module(
                "src.basetype_benchmark.exporters.p1_extractor" if paradigm == "P1" else "src.basetype_benchmark.exporters.p2_extractor",
                "--input", str(source_dir),
                "--output", str(output_dir)
            )
        elif paradigm in ("M1", "M2"):
            python_module(
                "src.basetype_benchmark.exporters.m1m2_extractor",
                "--input", str(source_dir),
                "--output", str(output_dir)
            )
        elif paradigm == "O2":
            python_module(
                "src.basetype_benchmark.exporters.o2_extractor",
                "--input", str(source_dir),
                "--output", str(output_dir)
            )

    console.print(f"\n[green]Export complete![/green]")
    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


# =============================================================================
# 3. RUN BENCHMARK
# =============================================================================

def menu_benchmark():
    """Benchmark execution menu with disk optimization.

    Integrated workflow: Export → Load → Benchmark → Cleanup per paradigm.
    Includes RAM gradient testing as a scenario option.
    """
    show_header()
    console.print("[bold]3. Run Benchmark[/bold]\n")

    console.print("[cyan]Benchmark scenarios:[/cyan]")
    console.print("  1. Quick Test (P1+M1, 3 runs, 32-16-8 GB)")
    console.print("  2. Standard (All paradigms, 10 runs, 128-64-32-16-8 GB)")
    console.print("  3. RAM Gradient (single paradigm, fine-grained RAM levels)")
    console.print("  4. Custom")

    choice = Prompt.ask("\nScenario", choices=["1", "2", "3", "4"], default="1")

    # Get source directory (generated Parquet data)
    console.print("\n[cyan]Select generated dataset (Parquet source):[/cyan]")
    generated_dirs = list(GENERATED_DIR.glob("*"))
    generated_dirs = [d for d in generated_dirs if d.is_dir() and (d / "nodes.parquet").exists()]

    if not generated_dirs:
        console.print("[yellow]No generated datasets found. Generate a dataset first.[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    for i, d in enumerate(generated_dirs, 1):
        console.print(f"  {i}. {d.name}")

    ds_idx = IntPrompt.ask("\nSelect dataset", default=1)
    if ds_idx < 1 or ds_idx > len(generated_dirs):
        console.print("[red]Invalid selection[/red]")
        return

    source_dir = generated_dirs[ds_idx - 1]

    # Output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if choice == "1":
        # Quick
        output = RESULTS_DIR / f"quick_{timestamp}.json"
        paradigms = "P1,M1"
        ram = "32,16,8"
        runs = 3
    elif choice == "2":
        # Standard
        output = RESULTS_DIR / f"standard_{timestamp}.json"
        paradigms = "P1,P2,M1,M2,O2"
        ram = "128,64,32,16,8"
        runs = 10
    elif choice == "3":
        # RAM Gradient - single paradigm with fine-grained RAM
        output = RESULTS_DIR / f"gradient_{timestamp}.json"
        paradigms = Prompt.ask("Paradigm to test", choices=PARADIGMS, default="M1")
        ram = Prompt.ask("RAM levels GB (fine-grained)", default="64,48,32,24,16,12,8,4")
        runs = IntPrompt.ask("Number of runs", default=10)
    else:
        # Custom
        output = RESULTS_DIR / f"custom_{timestamp}.json"
        paradigms = Prompt.ask("Paradigms (comma-separated, or ALL)", default="ALL")
        if paradigms.upper() == "ALL":
            paradigms = ",".join(PARADIGMS)
        ram = Prompt.ask("RAM levels GB (comma-separated)", default="64,32,16,8")
        runs = IntPrompt.ask("Number of runs", default=10)

    # Ask about disk cleanup
    cleanup = Confirm.ask("Cleanup exports after each paradigm (saves disk)?", default=True)

    # Confirm
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[yellow]Benchmark configuration:[/yellow]")
    console.print(f"  Source: {source_dir}")
    console.print(f"  Paradigms: {paradigms}")
    console.print(f"  RAM levels: {ram} GB")
    console.print(f"  Runs: {runs}")
    console.print(f"  Disk mode: {'optimisé (cleanup)' if cleanup else 'persistant'}")
    console.print(f"  Output: {output}")

    if not Confirm.ask("\nStart benchmark?", default=True):
        return

    # Run benchmark with disk optimization
    cleanup_flag = "--cleanup" if cleanup else "--no-cleanup"
    btb("benchmark",
        "-s", str(source_dir),
        "-e", str(EXPORT_DIR),
        "-o", str(output),
        "-p", paradigms,
        "--ram", ram,
        "--runs", str(runs),
        cleanup_flag)

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


# =============================================================================
# 4. MANAGE DATASETS
# =============================================================================

def menu_manage_datasets():
    """Dataset management menu."""
    show_header()
    console.print("[bold]4. Manage Datasets[/bold]\n")

    console.print("[cyan]Options:[/cyan]")
    console.print("  1. List all datasets")
    console.print("  2. Delete generated dataset")
    console.print("  3. Delete exported dataset")
    console.print("  4. Delete all data")
    console.print("  b. Back")

    choice = Prompt.ask("\nSelect", choices=["1", "2", "3", "4", "b"], default="1")

    if choice == "b":
        return

    if choice == "1":
        # List all
        console.print("\n[bold]Generated datasets:[/bold]")
        for ds in list_datasets(GENERATED_DIR):
            size = get_dir_size(ds)
            console.print(f"  {ds.name} ({size})")

        console.print("\n[bold]Exported datasets:[/bold]")
        for p in PARADIGMS:
            p_dir = EXPORT_DIR / p.lower()
            if p_dir.exists():
                for ds in p_dir.glob("*"):
                    size = get_dir_size(ds)
                    console.print(f"  {p}/{ds.name} ({size})")

    elif choice == "2":
        # Delete generated
        datasets = list_datasets(GENERATED_DIR)
        if not datasets:
            console.print("[yellow]No generated datasets.[/yellow]")
        else:
            console.print("\n[cyan]Generated datasets:[/cyan]")
            for i, ds in enumerate(datasets, 1):
                console.print(f"  {i}. {ds.name}")

            idx = IntPrompt.ask("Delete which?", default=1)
            if 1 <= idx <= len(datasets):
                ds = datasets[idx - 1]
                if Confirm.ask(f"[red]Delete {ds.name}?[/red]", default=False):
                    shutil.rmtree(ds)
                    console.print(f"[green]Deleted {ds.name}[/green]")

    elif choice == "3":
        # Delete exported
        console.print("\n[cyan]Select paradigm:[/cyan]")
        for i, p in enumerate(PARADIGMS, 1):
            console.print(f"  {i}. {p}")

        p_idx = IntPrompt.ask("Paradigm", default=1)
        if 1 <= p_idx <= len(PARADIGMS):
            p_dir = EXPORT_DIR / PARADIGMS[p_idx - 1].lower()
            datasets = list(p_dir.glob("*")) if p_dir.exists() else []

            if not datasets:
                console.print("[yellow]No exported datasets.[/yellow]")
            else:
                for i, ds in enumerate(datasets, 1):
                    console.print(f"  {i}. {ds.name}")

                idx = IntPrompt.ask("Delete which?", default=1)
                if 1 <= idx <= len(datasets):
                    ds = datasets[idx - 1]
                    if Confirm.ask(f"[red]Delete {ds.name}?[/red]", default=False):
                        shutil.rmtree(ds)
                        console.print(f"[green]Deleted {ds.name}[/green]")

    elif choice == "4":
        # Delete all
        if Confirm.ask("[red]DELETE ALL DATA? This cannot be undone![/red]", default=False):
            if GENERATED_DIR.exists():
                shutil.rmtree(GENERATED_DIR)
            if EXPORT_DIR.exists():
                shutil.rmtree(EXPORT_DIR)
            console.print("[green]All data deleted.[/green]")

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


# =============================================================================
# 5. VIEW RESULTS
# =============================================================================

def menu_results():
    """View benchmark results."""
    show_header()
    console.print("[bold]5. View Results[/bold]\n")

    if not RESULTS_DIR.exists():
        console.print("[yellow]No results directory.[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    files = sorted(RESULTS_DIR.glob("*.json"), reverse=True)
    if not files:
        console.print("[yellow]No result files.[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    console.print("[cyan]Recent results:[/cyan]")
    for i, f in enumerate(files[:10], 1):
        size = f.stat().st_size / 1024
        console.print(f"  {i}. {f.name} ({size:.1f} KB)")

    choice = Prompt.ask("\nSelect (or 'b' to go back)", default="1")
    if choice == "b":
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            with open(files[idx]) as f:
                data = json.load(f)

            console.print(f"\n[bold]Results: {files[idx].name}[/bold]\n")

            # Config
            if "config" in data:
                cfg = data["config"]
                console.print(f"[cyan]Configuration:[/cyan]")
                console.print(f"  Paradigms: {', '.join(cfg.get('paradigms', []))}")
                console.print(f"  RAM levels: {cfg.get('ram_levels_mb', [])}")
                console.print(f"  Runs: {cfg.get('n_runs', 'N/A')}")

            # Summary
            if "summary" in data:
                console.print(f"\n[cyan]RAM Viable (smallest without OOM):[/cyan]")
                for p, ram in data["summary"].get("ram_viable", {}).items():
                    if ram:
                        console.print(f"  {p}: [green]{ram:,} MB ({ram/1024:.0f} GB)[/green]")
                    else:
                        console.print(f"  {p}: [red]All OOM[/red]")

                console.print(f"\n[cyan]RAM Baseline:[/cyan]")
                for p, ram in data["summary"].get("ram_baseline", {}).items():
                    console.print(f"  {p}: {ram:,.0f} MB")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


# =============================================================================
# 6. DOCKER
# =============================================================================

def menu_docker():
    """Docker management."""
    show_header()
    console.print("[bold]6. Docker Containers[/bold]\n")

    console.print("[cyan]Options:[/cyan]")
    console.print("  1. Status")
    console.print("  2. Start all")
    console.print("  3. Stop all")
    console.print("  4. Restart all")
    console.print("  5. Logs")
    console.print("  6. Stats (live)")
    console.print("  b. Back")

    choice = Prompt.ask("\nSelect", choices=["1", "2", "3", "4", "5", "6", "b"], default="1")

    if choice == "b":
        return

    compose = ["docker", "compose", "-f", str(PROJECT_DIR / "docker" / "docker-compose.yml")]

    if choice == "1":
        run_command(compose + ["ps"])
    elif choice == "2":
        run_command(compose + ["up", "-d"])
    elif choice == "3":
        run_command(compose + ["down"])
    elif choice == "4":
        run_command(compose + ["down"])
        run_command(compose + ["up", "-d"])
    elif choice == "5":
        run_command(compose + ["logs", "-f", "--tail=50"])
    elif choice == "6":
        run_command(["docker", "stats"])

    if choice not in ["5", "6"]:
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")


# =============================================================================
# VALIDATION
# =============================================================================

def menu_validation():
    """Query validation."""
    show_header()
    console.print("[bold]Query Validation[/bold]\n")

    console.print("[cyan]Options:[/cyan]")
    console.print("  1. Paradigm Matrix")
    console.print("  2. Validate all queries")
    console.print("  3. Query info")
    console.print("  b. Back")

    choice = Prompt.ask("\nSelect", choices=["1", "2", "3", "b"], default="1")

    if choice == "b":
        return

    if choice == "1":
        btb("dry-run", "--matrix")
    elif choice == "2":
        btb("dry-run", "--all", "--verbose")
    elif choice == "3":
        qid = Prompt.ask("Query ID", default="Q1")
        btb("info", qid.upper())

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


# =============================================================================
# SYSTEM INFO
# =============================================================================

def show_system_info():
    """Show system information."""
    show_header()
    console.print("[bold]System Information[/bold]\n")

    import platform
    import os

    console.print(f"[cyan]OS:[/cyan] {platform.system()} {platform.release()}")
    console.print(f"[cyan]Python:[/cyan] {platform.python_version()}")
    console.print(f"[cyan]CPUs:[/cyan] {os.cpu_count()}")

    # Memory
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    mem_kb = int(line.split()[1])
                    console.print(f"[cyan]RAM:[/cyan] {mem_kb / 1024 / 1024:.0f} GB")
                if line.startswith("MemAvailable:"):
                    mem_kb = int(line.split()[1])
                    console.print(f"[cyan]RAM Available:[/cyan] {mem_kb / 1024 / 1024:.0f} GB")
    except:
        pass

    # Disk
    try:
        total, used, free = shutil.disk_usage("/")
        console.print(f"[cyan]Disk:[/cyan] {free/1024/1024/1024:.0f} GB free / {total/1024/1024/1024:.0f} GB total")
    except:
        pass

    # Docker
    console.print()
    run_command(["docker", "--version"])

    # cgroups
    console.print()
    if Path("/sys/fs/cgroup/cgroup.controllers").exists():
        console.print("[green]cgroups v2: OK[/green]")
    else:
        console.print("[yellow]cgroups v2: Not detected[/yellow]")

    # Data directories
    console.print(f"\n[cyan]Data paths:[/cyan]")
    console.print(f"  Generated: {GENERATED_DIR}")
    console.print(f"  Exports: {EXPORT_DIR}")
    console.print(f"  Results: {RESULTS_DIR}")

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


# =============================================================================
# NEW MENU FUNCTIONS
# =============================================================================

def menu_run_benchmark():
    """Benchmark with scenario selection."""
    show_header()
    console.print("[bold]Run Benchmark[/bold]\n")

    # Pre-flight checks
    console.print("[cyan]Pre-flight checks:[/cyan]")

    # Check Docker
    docker_ok = False
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        docker_ok = result.returncode == 0
    except:
        pass
    console.print(f"  {'[green]+[/green]' if docker_ok else '[red]x[/red]'} Docker")

    # Check datasets
    datasets = list_datasets(GENERATED_DIR)
    datasets = [d for d in datasets if (d / "nodes.parquet").exists()]
    console.print(f"  {'[green]+[/green]' if datasets else '[yellow]![/yellow]'} Datasets ({len(datasets)} available)")

    if not docker_ok:
        console.print("\n[red]Docker is not running. Start Docker first.[/red]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    if not datasets:
        console.print("\n[yellow]No datasets found. Generate one first (option 1).[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    # Select scenario
    console.print("\n[cyan]Select scenario:[/cyan]")
    console.print("  1. Quick Test       (P1+M1, 3 runs, ~10 min)")
    console.print("  2. Standard         (All paradigms, 10 runs, ~2h)")
    console.print("  3. RAM Gradient     (Single paradigm, fine-grained)")
    console.print("  4. Publication      (High precision, ~8h)")
    console.print("  5. Custom           (Build your own)")
    console.print("  b. Back")

    scenario_choice = Prompt.ask("\nScenario", choices=["1", "2", "3", "4", "5", "b"], default="1")

    if scenario_choice == "b":
        return

    scenario_map = {"1": "quick", "2": "standard", "3": "ram_gradient", "4": "publication"}

    # Select dataset
    console.print("\n[cyan]Select dataset:[/cyan]")
    for i, ds in enumerate(datasets, 1):
        size = get_dir_size(ds)
        console.print(f"  {i}. {ds.name} ({size})")

    ds_idx = IntPrompt.ask("\nDataset", default=1)
    if ds_idx < 1 or ds_idx > len(datasets):
        console.print("[red]Invalid selection[/red]")
        return

    source_dir = datasets[ds_idx - 1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if scenario_choice == "5":
        # Custom scenario
        paradigms = Prompt.ask("Paradigms (comma-separated)", default="P1,M1")
        ram = Prompt.ask("RAM levels GB", default="32,16,8")
        runs = IntPrompt.ask("Number of runs", default=5)
        output = RESULTS_DIR / f"custom_{timestamp}.json"

        btb("benchmark",
            "-s", str(source_dir),
            "-e", str(EXPORT_DIR),
            "-o", str(output),
            "-p", paradigms,
            "--ram", ram,
            "--runs", str(runs))
    else:
        scenario = scenario_map.get(scenario_choice, "quick")
        output = RESULTS_DIR / f"{scenario}_{timestamp}.json"

        # For RAM gradient, ask which paradigm
        extra_args = []
        if scenario == "ram_gradient":
            paradigm = Prompt.ask("Paradigm to test", choices=PARADIGMS, default="M1")
            extra_args = ["-p", paradigm]

        btb("benchmark",
            "-s", str(source_dir),
            "-e", str(EXPORT_DIR),
            "-o", str(output),
            "--scenario", scenario,
            *extra_args)

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def menu_ram_gradient():
    """Direct RAM gradient test."""
    show_header()
    console.print("[bold]RAM Gradient Test[/bold]\n")

    # Select paradigm
    paradigm = Prompt.ask("Paradigm", choices=PARADIGMS, default="M1")

    # Select data directory
    export_dirs = []
    paradigm_dir = EXPORT_DIR / paradigm.lower()
    if paradigm_dir.exists():
        export_dirs = [d for d in paradigm_dir.iterdir() if d.is_dir()]

    if not export_dirs:
        console.print(f"[yellow]No exported data for {paradigm}. Run export first.[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    console.print(f"\n[cyan]Select {paradigm} export:[/cyan]")
    for i, d in enumerate(export_dirs, 1):
        console.print(f"  {i}. {d.name}")

    idx = IntPrompt.ask("\nSelect", default=1)
    if idx < 1 or idx > len(export_dirs):
        return

    data_dir = export_dirs[idx - 1]

    # RAM levels
    ram = Prompt.ask("RAM levels GB (fine-grained)", default="64,48,32,24,16,12,8,4")

    # Query
    query = Prompt.ask("Query to test", default="Q1")

    btb("gradient", paradigm, "-d", str(data_dir), "--ram", ram, "-q", query)

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def menu_load_data():
    """Direct database load."""
    show_header()
    console.print("[bold]Load Data[/bold]\n")

    paradigm = Prompt.ask("Target paradigm", choices=PARADIGMS, default="P1")

    # Find exports
    paradigm_dir = EXPORT_DIR / paradigm.lower()
    if not paradigm_dir.exists():
        console.print(f"[yellow]No exports for {paradigm}[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    exports = [d for d in paradigm_dir.iterdir() if d.is_dir()]
    if not exports:
        console.print(f"[yellow]No exports found for {paradigm}[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    console.print(f"\n[cyan]Select export:[/cyan]")
    for i, e in enumerate(exports, 1):
        console.print(f"  {i}. {e.name}")

    idx = IntPrompt.ask("\nSelect", default=1)
    if idx < 1 or idx > len(exports):
        return

    data_dir = exports[idx - 1]

    clear = Confirm.ask("Clear database before load?", default=False)

    args = ["load", paradigm, "-d", str(data_dir)]
    if clear:
        args.append("--clear")

    btb(*args)

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def menu_golden_tests():
    """Golden validation menu."""
    show_header()
    console.print("[bold]Golden Tests[/bold]\n")

    console.print("[cyan]Options:[/cyan]")
    console.print("  1. Export golden dataset")
    console.print("  2. Run validation")
    console.print("  3. Show report")
    console.print("  b. Back")

    choice = Prompt.ask("\nSelect", choices=["1", "2", "3", "b"], default="2")

    if choice == "b":
        return

    if choice == "1":
        btb("golden", "export")
    elif choice == "2":
        btb("golden", "validate", "--verbose")
    elif choice == "3":
        btb("golden", "report")

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def menu_debug_query():
    """Debug single query."""
    show_header()
    console.print("[bold]Debug Query[/bold]\n")

    paradigm = Prompt.ask("Paradigm", choices=PARADIGMS, default="P1")
    query = Prompt.ask("Query ID", default="Q1")
    params = Prompt.ask("Parameters (JSON or empty)", default="")

    args = ["run-query", query, "-p", paradigm]
    if params:
        args.extend(["--params", params])

    btb(*args)

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def menu_summary_report():
    """Generate summary report from results."""
    show_header()
    console.print("[bold]Summary Report[/bold]\n")

    if not RESULTS_DIR.exists():
        console.print("[yellow]No results directory[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    files = sorted(RESULTS_DIR.glob("*.json"), reverse=True)
    if not files:
        console.print("[yellow]No result files[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    console.print("[cyan]Recent results:[/cyan]")
    for i, f in enumerate(files[:10], 1):
        console.print(f"  {i}. {f.name}")

    choice = IntPrompt.ask("\nSelect result", default=1)
    if choice < 1 or choice > len(files):
        return

    result_file = files[choice - 1]

    try:
        with open(result_file) as f:
            data = json.load(f)

        console.print(f"\n[bold]Summary: {result_file.name}[/bold]\n")

        # Config
        if "config" in data:
            cfg = data["config"]
            console.print(f"[cyan]Configuration:[/cyan]")
            console.print(f"  Paradigms: {', '.join(cfg.get('paradigms', []))}")
            console.print(f"  RAM levels: {cfg.get('ram_levels_mb', [])}")

        # RAM viable
        if "summary" in data:
            console.print(f"\n[cyan]RAM Viable (smallest without OOM):[/cyan]")
            for p, ram in data["summary"].get("ram_viable", {}).items():
                if ram:
                    console.print(f"  {p}: [green]{ram:,} MB ({ram/1024:.0f} GB)[/green]")
                else:
                    console.print(f"  {p}: [red]All OOM[/red]")

        # Generate markdown summary
        if Confirm.ask("\nExport to markdown?", default=False):
            md_path = result_file.with_suffix(".md")
            with open(md_path, "w") as f:
                f.write(f"# Benchmark Results: {result_file.stem}\n\n")
                if "config" in data:
                    f.write("## Configuration\n\n")
                    f.write(f"- Paradigms: {', '.join(cfg.get('paradigms', []))}\n")
                    f.write(f"- RAM levels: {cfg.get('ram_levels_mb', [])}\n\n")
                if "summary" in data:
                    f.write("## RAM Viable\n\n")
                    f.write("| Paradigm | RAM Viable |\n")
                    f.write("|----------|------------|\n")
                    for p, ram in data["summary"].get("ram_viable", {}).items():
                        ram_str = f"{ram:,} MB" if ram else "FAIL"
                        f.write(f"| {p} | {ram_str} |\n")
            console.print(f"[green]Exported to {md_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def menu_profiles_info():
    """Show profiles info."""
    show_header()
    btb("profiles")
    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


# =============================================================================
# UTILITIES
# =============================================================================

def list_datasets(directory: Path) -> list[Path]:
    """List datasets in directory."""
    if not directory.exists():
        return []
    return sorted([d for d in directory.iterdir() if d.is_dir()])


def get_dir_size(path: Path) -> str:
    """Get directory size as human-readable string."""
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    if total < 1024:
        return f"{total} B"
    elif total < 1024 * 1024:
        return f"{total/1024:.1f} KB"
    elif total < 1024 * 1024 * 1024:
        return f"{total/1024/1024:.1f} MB"
    else:
        return f"{total/1024/1024/1024:.1f} GB"


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    # Ensure data directories exist
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        show_header()
        choice = show_main_menu()

        if choice == "q":
            console.print("\n[dim]Goodbye![/dim]")
            break
        # Benchmark
        elif choice == "r":
            menu_run_benchmark()
        elif choice == "g":
            menu_ram_gradient()
        # Preparation
        elif choice == "1":
            menu_generate()
        elif choice == "2":
            menu_export()
        elif choice == "3":
            menu_load_data()
        # Validation
        elif choice == "v":
            menu_validation()
        elif choice == "t":
            menu_golden_tests()
        elif choice == "d":
            menu_debug_query()
        # Results
        elif choice == "5":
            menu_results()
        elif choice == "s":
            menu_summary_report()
        # System
        elif choice == "6":
            menu_docker()
        elif choice == "4":
            menu_manage_datasets()
        elif choice == "i":
            show_system_info()
        elif choice == "p":
            menu_profiles_info()


if __name__ == "__main__":
    main()
