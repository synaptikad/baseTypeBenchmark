#!/usr/bin/env python3
"""Interactive Benchmark Runner V3.

Menu-driven interface for benchmark operations.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Rich for beautiful menus
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
except ImportError:
    print("Installing rich...")
    subprocess.run([sys.executable, "-m", "pip", "install", "rich", "-q"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table

console = Console()

# Paths
PROJECT_DIR = Path(__file__).parent
VENV_BTB = PROJECT_DIR / ".venv" / "bin" / "btb-runner"
DATA_DIR = Path("/data/benchmark")
EXPORT_DIR = DATA_DIR / "exports"
RESULTS_DIR = DATA_DIR / "results"


def run_command(cmd: list[str], capture: bool = False) -> int:
    """Run a command and return exit code."""
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]\n")
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True)
        console.print(result.stdout)
        if result.stderr:
            console.print(f"[red]{result.stderr}[/red]")
        return result.returncode
    return subprocess.run(cmd).returncode


def btb(*args) -> int:
    """Run btb-runner command."""
    cmd = [str(VENV_BTB)] + list(args)
    return run_command(cmd)


def show_header():
    """Show application header."""
    console.clear()
    console.print(Panel.fit(
        "[bold blue]BaseType Benchmark V3[/bold blue]\n"
        "[dim]Interactive Runner[/dim]",
        border_style="blue"
    ))
    console.print()


def show_main_menu() -> str:
    """Show main menu and return choice."""
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan bold", width=4)
    table.add_column("Action")

    table.add_row("1", "Query Validation (dry-run)")
    table.add_row("2", "Docker Containers")
    table.add_row("3", "Load Data")
    table.add_row("4", "Run Benchmark")
    table.add_row("5", "RAM Gradient Test")
    table.add_row("6", "View Results")
    table.add_row("", "")
    table.add_row("i", "System Info")
    table.add_row("q", "Quit")

    console.print(table)
    console.print()

    return Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6", "i", "q"], default="1")


def menu_validation():
    """Query validation menu."""
    show_header()
    console.print("[bold]Query Validation[/bold]\n")

    choices = {
        "1": ("Paradigm Matrix", lambda: btb("dry-run", "--matrix")),
        "2": ("Validate All Queries", lambda: btb("dry-run", "--all", "--verbose")),
        "3": ("Query Info", lambda: query_info()),
        "b": ("Back", None),
    }

    for key, (label, _) in choices.items():
        console.print(f"  [cyan]{key}[/cyan] - {label}")

    choice = Prompt.ask("\nSelect", choices=list(choices.keys()), default="1")

    if choice != "b" and choices[choice][1]:
        console.print()
        choices[choice][1]()
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def query_info():
    """Show info for a specific query."""
    qid = Prompt.ask("Query ID", default="Q1")
    btb("info", qid.upper())


def menu_docker():
    """Docker management menu."""
    show_header()
    console.print("[bold]Docker Containers[/bold]\n")

    choices = {
        "1": ("Status", lambda: run_command(["docker", "compose", "-f", "docker/docker-compose.yml", "ps"])),
        "2": ("Start All", lambda: run_command(["docker", "compose", "-f", "docker/docker-compose.yml", "up", "-d"])),
        "3": ("Stop All", lambda: run_command(["docker", "compose", "-f", "docker/docker-compose.yml", "down"])),
        "4": ("Logs (follow)", lambda: run_command(["docker", "compose", "-f", "docker/docker-compose.yml", "logs", "-f", "--tail=50"])),
        "5": ("Stats", lambda: run_command(["docker", "stats", "--no-stream"])),
        "b": ("Back", None),
    }

    for key, (label, _) in choices.items():
        console.print(f"  [cyan]{key}[/cyan] - {label}")

    choice = Prompt.ask("\nSelect", choices=list(choices.keys()), default="1")

    if choice != "b" and choices[choice][1]:
        console.print()
        choices[choice][1]()
        if choice != "4":  # Don't wait after logs -f
            Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def menu_load():
    """Data loading menu."""
    show_header()
    console.print("[bold]Load Data[/bold]\n")

    paradigms = ["P1", "P2", "M1", "M2", "O2"]

    for i, p in enumerate(paradigms, 1):
        console.print(f"  [cyan]{i}[/cyan] - Load {p}")
    console.print(f"  [cyan]a[/cyan] - Load All")
    console.print(f"  [cyan]b[/cyan] - Back")

    choice = Prompt.ask("\nSelect", choices=[str(i) for i in range(1, 6)] + ["a", "b"], default="1")

    if choice == "b":
        return

    # Get data directory
    default_dir = str(EXPORT_DIR)
    data_dir = Prompt.ask("Data directory", default=default_dir)

    clear = Confirm.ask("Clear database before loading?", default=True)

    if choice == "a":
        for p in paradigms:
            console.print(f"\n[bold]Loading {p}...[/bold]")
            args = ["load", p, "-d", data_dir]
            if clear:
                args.append("--clear")
            btb(*args)
    else:
        p = paradigms[int(choice) - 1]
        args = ["load", p, "-d", data_dir]
        if clear:
            args.append("--clear")
        btb(*args)

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def menu_benchmark():
    """Benchmark execution menu."""
    show_header()
    console.print("[bold]Run Benchmark[/bold]\n")

    choices = {
        "1": "Quick (P1, M1 - 3 runs)",
        "2": "Standard (All paradigms - 10 runs)",
        "3": "Custom",
        "b": "Back",
    }

    for key, label in choices.items():
        console.print(f"  [cyan]{key}[/cyan] - {label}")

    choice = Prompt.ask("\nSelect", choices=list(choices.keys()), default="1")

    if choice == "b":
        return

    # Get data directory
    default_dir = str(EXPORT_DIR)
    data_dir = Prompt.ask("Data directory", default=default_dir)

    # Output file
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    default_output = str(RESULTS_DIR / f"results_{timestamp}.json")
    output = Prompt.ask("Output file", default=default_output)

    if choice == "1":
        # Quick
        btb("benchmark", "-d", data_dir, "-o", output, "-p", "P1,M1", "--ram", "32,16,8", "--runs", "3")
    elif choice == "2":
        # Standard
        btb("benchmark", "-d", data_dir, "-o", output, "--ram", "128,64,32,16,8")
    else:
        # Custom
        paradigms = Prompt.ask("Paradigms (comma-separated)", default="P1,P2,M1,M2,O2")
        ram = Prompt.ask("RAM levels GB (comma-separated)", default="64,32,16,8")
        runs = Prompt.ask("Number of runs", default="10")
        btb("benchmark", "-d", data_dir, "-o", output, "-p", paradigms, "--ram", ram, "--runs", runs)

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def menu_gradient():
    """RAM gradient test menu."""
    show_header()
    console.print("[bold]RAM Gradient Test[/bold]\n")

    paradigm = Prompt.ask("Paradigm", choices=["P1", "P2", "M1", "M2", "O2"], default="M1")

    default_dir = str(EXPORT_DIR)
    data_dir = Prompt.ask("Data directory", default=default_dir)

    ram = Prompt.ask("RAM levels GB", default="32,16,8")
    query = Prompt.ask("Query to test", default="Q1")

    btb("gradient", paradigm, "-d", data_dir, "--ram", ram, "-q", query)

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def menu_results():
    """View results menu."""
    show_header()
    console.print("[bold]View Results[/bold]\n")

    # List result files
    results_path = RESULTS_DIR
    if not results_path.exists():
        console.print("[yellow]No results directory found[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    files = sorted(results_path.glob("*.json"), reverse=True)

    if not files:
        console.print("[yellow]No result files found[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
        return

    console.print("Recent results:")
    for i, f in enumerate(files[:10], 1):
        size = f.stat().st_size / 1024
        console.print(f"  [cyan]{i}[/cyan] - {f.name} ({size:.1f} KB)")

    choice = Prompt.ask("\nSelect file to view (or 'b' to go back)", default="1")

    if choice == "b":
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            # Show summary
            import json
            with open(files[idx]) as f:
                data = json.load(f)

            console.print(f"\n[bold]Results: {files[idx].name}[/bold]\n")

            if "summary" in data:
                console.print("[cyan]RAM Viable:[/cyan]")
                for p, ram in data["summary"].get("ram_viable", {}).items():
                    if ram:
                        console.print(f"  {p}: {ram:,} MB ({ram/1024:.0f} GB)")
                    else:
                        console.print(f"  {p}: [red]OOM[/red]")
    except (ValueError, IndexError, json.JSONDecodeError) as e:
        console.print(f"[red]Error: {e}[/red]")

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def show_system_info():
    """Show system information."""
    show_header()
    console.print("[bold]System Information[/bold]\n")

    import platform
    import shutil

    # System
    console.print(f"[cyan]OS:[/cyan] {platform.system()} {platform.release()}")
    console.print(f"[cyan]Python:[/cyan] {platform.python_version()}")

    # Memory
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    mem_kb = int(line.split()[1])
                    console.print(f"[cyan]RAM:[/cyan] {mem_kb / 1024 / 1024:.0f} GB")
                    break
    except:
        pass

    # CPU
    try:
        import os
        console.print(f"[cyan]CPUs:[/cyan] {os.cpu_count()}")
    except:
        pass

    # Disk
    total, used, free = shutil.disk_usage("/")
    console.print(f"[cyan]Disk:[/cyan] {free/1024/1024/1024:.0f} GB free / {total/1024/1024/1024:.0f} GB total")

    # Docker
    console.print()
    run_command(["docker", "--version"])

    # cgroups
    console.print()
    cgroup_path = Path("/sys/fs/cgroup")
    if (cgroup_path / "cgroup.controllers").exists():
        console.print("[green]cgroups v2: OK[/green]")
    else:
        console.print("[yellow]cgroups v2: Not detected[/yellow]")

    Prompt.ask("\n[dim]Press Enter to continue[/dim]")


def main():
    """Main entry point."""
    while True:
        show_header()
        choice = show_main_menu()

        if choice == "q":
            console.print("\n[dim]Goodbye![/dim]")
            break
        elif choice == "1":
            menu_validation()
        elif choice == "2":
            menu_docker()
        elif choice == "3":
            menu_load()
        elif choice == "4":
            menu_benchmark()
        elif choice == "5":
            menu_gradient()
        elif choice == "6":
            menu_results()
        elif choice == "i":
            show_system_info()


if __name__ == "__main__":
    main()
