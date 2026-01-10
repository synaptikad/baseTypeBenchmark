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

    console.print(f"\n[yellow]Generate {profile}-{duration} (seed={seed})?[/yellow]")
    if not Confirm.ask("", default=True):
        return

    output_dir = GENERATED_DIR / f"{profile}-{duration}"
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print()
    run_cmd([
        str(VENV_PYTHON), "-m", "src.basetype_benchmark.dataset.generator",
        "--profile", profile,
        "--duration", duration,
        "--seed", str(seed),
        "--config-dir", str(CONFIG_DIR),
        "--output", str(GENERATED_DIR),
        "--format", "parquet"
    ])

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

        console.print("[cyan]1[/cyan]. Quick test      [dim]P1+M1, 3 queries, ~5min[/dim]")
        console.print("[cyan]2[/cyan]. Standard        [dim]All paradigms, full suite[/dim]")
        console.print("[cyan]3[/cyan]. RAM gradient    [dim]Fine-grained memory test[/dim]")
        console.print("[cyan]4[/cyan]. Custom")
        console.print()
        console.print("[cyan]d[/cyan]. Debug query     [dim]Run single query[/dim]")
        console.print("[cyan]v[/cyan]. Validate        [dim]Check query matrix[/dim]")
        console.print()
        console.print("[cyan]b[/cyan]. Back")
        console.print()

        choice = Prompt.ask("", choices=["1", "2", "3", "4", "d", "v", "b"], default="1", show_choices=False)

        if choice == "b":
            return

        if choice in ["1", "2", "3", "4"]:
            if not docker_ok:
                console.print("\n[red]Start Docker first.[/red]")
                wait()
                continue
            if not datasets:
                console.print("\n[yellow]Generate a dataset first (Dataset > Generate).[/yellow]")
                wait()
                continue
            run_benchmark(choice, datasets)
        elif choice == "d":
            debug_query()
        elif choice == "v":
            btb("dry-run", "--matrix")
            wait()


def run_benchmark(mode: str, datasets: list[Path]):
    header("Run Benchmark")

    # Select dataset
    console.print("[bold]Dataset:[/bold]")
    idx = select_from_list(datasets)
    if idx is None:
        return
    source = datasets[idx]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Use temporary directory for exports (on-demand, cleaned after use)
    import tempfile
    with tempfile.TemporaryDirectory(prefix="btb_export_") as tmp_export:
        tmp_export_path = Path(tmp_export)
        console.print(f"[dim]Temporary export dir: {tmp_export_path}[/dim]\n")

        if mode == "1":
            # Quick
            output = RESULTS_DIR / f"quick_{timestamp}.json"
            console.print(f"\n[yellow]Quick test: P1+M1, 3 runs, 32-16-8 GB[/yellow]")
            if Confirm.ask("Start?", default=True):
                btb("benchmark", "-s", str(source), "-e", str(tmp_export_path), "-o", str(output),
                    "-p", "P1,M1", "--ram", "32,16,8", "--runs", "3", "--cleanup")

        elif mode == "2":
            # Standard
            output = RESULTS_DIR / f"standard_{timestamp}.json"
            console.print(f"\n[yellow]Standard: All paradigms, 10 runs, 64-32-16-8 GB[/yellow]")
            if Confirm.ask("Start?", default=True):
                btb("benchmark", "-s", str(source), "-e", str(tmp_export_path), "-o", str(output),
                    "-p", "P1,P2,M1,M2,O2", "--ram", "64,32,16,8", "--runs", "10", "--cleanup")

        elif mode == "3":
            # RAM gradient
            console.print("\n[bold]Paradigm:[/bold]")
            for i, p in enumerate(PARADIGMS, 1):
                console.print(f"  [cyan]{i}[/cyan]. {p}")
            console.print()
            idx = IntPrompt.ask("Select", default=3)
            paradigm = PARADIGMS[idx - 1] if 1 <= idx <= len(PARADIGMS) else "M1"

            ram = Prompt.ask("RAM levels (GB)", default="64,48,32,24,16,12,8,4")

            output = RESULTS_DIR / f"gradient_{paradigm}_{timestamp}.json"
            console.print(f"\n[yellow]RAM gradient: {paradigm}, levels={ram}[/yellow]")
            if Confirm.ask("Start?", default=True):
                btb("benchmark", "-s", str(source), "-e", str(tmp_export_path), "-o", str(output),
                    "-p", paradigm, "--ram", ram, "--runs", "5", "--cleanup")

        elif mode == "4":
            # Custom
            console.print("\n[bold]Paradigms:[/bold] P1, P2, M1, M2, O2 (or ALL)")
            paradigms = Prompt.ask("Select", default="ALL")
            if paradigms.upper() == "ALL":
                paradigms = "P1,P2,M1,M2,O2"
            console.print("[bold]RAM levels (GB):[/bold] 128, 64, 32, 16, 8, 4, 2, 1, 0.5")
            ram = Prompt.ask("Select", default="128,64,32,16,8,4,2,1,0.5")
            runs = IntPrompt.ask("Runs", default=5)

            output = RESULTS_DIR / f"custom_{timestamp}.json"
            console.print(f"\n[yellow]Custom: {paradigms}, RAM={ram}, runs={runs}[/yellow]")
            if Confirm.ask("Start?", default=True):
                btb("benchmark", "-s", str(source), "-e", str(tmp_export_path), "-o", str(output),
                    "-p", paradigms, "--ram", ram, "--runs", str(runs), "--cleanup")

    # Temporary directory auto-cleaned on exit
    console.print("[dim]Export directory cleaned.[/dim]")
    wait()


def debug_query():
    header("Debug Query")

    paradigm = Prompt.ask("Paradigm", choices=PARADIGMS, default="P1")
    query = Prompt.ask("Query ID", default="Q1")

    btb("run-query", query, "-p", paradigm)
    wait()


# =============================================================================
# 3. RESULTS
# =============================================================================

def menu_results():
    while True:
        header("Results")

        files = sorted(RESULTS_DIR.glob("*.json"), reverse=True) if RESULTS_DIR.exists() else []

        if not files:
            console.print("[yellow]No results yet.[/yellow]")
            wait()
            return

        console.print("[bold]Recent:[/bold]")
        for i, f in enumerate(files[:8], 1):
            size_kb = f.stat().st_size / 1024
            console.print(f"  [cyan]{i}[/cyan]. {f.name} ({size_kb:.0f}KB)")
        console.print()
        console.print("[cyan]b[/cyan]. Back")
        console.print()

        choice = Prompt.ask("", default="1")
        if choice == "b":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                view_result(files[idx])
        except ValueError:
            pass


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
            console.print(f"  RAM: {cfg.get('ram_levels_mb', [])}")
            console.print(f"  Runs: {cfg.get('n_runs', '?')}")
            console.print()

        # Summary
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

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

    wait()


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
