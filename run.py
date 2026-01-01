#!/usr/bin/env python3
"""BaseType Benchmark - Interactive Workflow

Interactive workflow for:
1. Dataset purge
2. Dataset generation (choose scale + duration)
3. Benchmark execution (per scenario)
4. Results publication

Usage:
    python run.py                           # Interactive mode
    python run.py generate small-2d         # CLI: generate dataset
    python run.py P1 --ram 8                # CLI: run scenario
    python run.py ALL --ram 16              # CLI: run all scenarios
"""

import os
import sys
import shutil
from pathlib import Path

# Ensure src/ is in path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_header(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_ok(msg: str):
    print(f"{GREEN}[OK]{RESET} {msg}")


def print_warn(msg: str):
    print(f"{YELLOW}[!]{RESET} {msg}")


def print_info(msg: str):
    print(f"{BLUE}[i]{RESET} {msg}")


def prompt(question: str, default: str = "") -> str:
    if default:
        answer = input(f"{question} [{default}]: ").strip()
        return answer if answer else default
    return input(f"{question}: ").strip()


def get_exports_dir() -> Path:
    return Path(__file__).parent / "src" / "basetype_benchmark" / "dataset" / "exports"


def get_available_datasets() -> list:
    """Get list of available datasets."""
    exports = get_exports_dir()
    if not exports.exists():
        return []
    
    datasets = []
    for d in exports.iterdir():
        if d.is_dir() and (d / "parquet").exists():
            # Calculate size
            size_mb = sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) / (1024 * 1024)
            datasets.append({"name": d.name, "path": d, "size_mb": size_mb})
    return datasets


def workflow_purge():
    """Purge datasets."""
    print_header("PURGE DATASETS")
    
    datasets = get_available_datasets()
    if not datasets:
        print("No datasets to purge.")
        input("\nPress Enter...")
        return
    
    print(f"{YELLOW}WARNING: This will permanently delete dataset files!{RESET}\n")
    print("Exported datasets:\n")
    
    total_mb = 0
    for i, ds in enumerate(datasets, 1):
        print(f"  {i}. {ds['name']}: {ds['size_mb']:.1f} MB")
        total_mb += ds['size_mb']
    
    print(f"\n  Total: {total_mb:.1f} MB\n")
    print("  Options:")
    print("    A. Delete ALL datasets")
    print("    S. Select specific dataset")
    print("    0. Cancel\n")
    
    choice = prompt("Select", "0").upper()
    
    if choice == "0":
        return
    elif choice == "A":
        confirm = input(f"Are you sure you want to delete ALL {len(datasets)} datasets? [y/N]: ").strip().lower()
        if confirm == 'y':
            for ds in datasets:
                shutil.rmtree(ds['path'])
                print(f"  Deleted: {ds['name']}")
            print_ok(f"Deleted {len(datasets)} datasets ({total_mb:.1f} MB freed)")
    elif choice == "S":
        idx = prompt(f"Enter dataset number (1-{len(datasets)})", "1")
        try:
            ds = datasets[int(idx) - 1]
            confirm = input(f"Delete {ds['name']}? [y/N]: ").strip().lower()
            if confirm == 'y':
                shutil.rmtree(ds['path'])
                print_ok(f"Deleted {ds['name']}")
        except (ValueError, IndexError):
            print("Invalid selection.")
    
    input("\nPress Enter...")


def workflow_generate():
    """Generate dataset."""
    print_header("GENERATE DATASET")
    
    from basetype_benchmark.dataset.dataset_manager import DatasetManager
    
    # Scale selection
    print("Select scale:\n")
    print("  1. small  - 1 building, ~50K nodes")
    print("  2. medium - 5 buildings, ~250K nodes")
    print("  3. large  - 25 buildings, ~1.25M nodes\n")
    
    scale_choice = prompt("Select scale", "1")
    scales = {"1": "small", "2": "medium", "3": "large"}
    scale = scales.get(scale_choice, "small")
    
    # Duration selection
    print("\nSelect time window:\n")
    print("  1. 2d  - 2 days (~0.5 GB)")
    print("  2. 1w  - 1 week (~1 GB)")
    print("  3. 1m  - 1 month (~5 GB)")
    print("  4. 6m  - 6 months (~27 GB)")
    print("  5. 1y  - 1 year (~55 GB)\n")
    
    duration_choice = prompt("Select duration", "1")
    durations = {"1": "2d", "2": "1w", "3": "1m", "4": "6m", "5": "1y"}
    duration = durations.get(duration_choice, "2d")
    
    profile = f"{scale}-{duration}"
    
    # Seed
    seed = int(prompt("Random seed", "42"))
    
    # Check if exists
    exports = get_exports_dir()
    target = exports / f"{profile}_seed{seed}"
    if target.exists():
        overwrite = input(f"\nDataset {profile}_seed{seed} already exists. Overwrite? [y/N]: ").strip().lower()
        if overwrite != 'y':
            return
        shutil.rmtree(target)
    
    print(f"\n{BLUE}Generating {profile} with seed {seed}...{RESET}\n")
    
    manager = DatasetManager()
    parquet_dir, fingerprint = manager.generate_parquet_only(profile, seed)
    
    print_ok(f"Dataset generated: {parquet_dir}")
    print(f"  Nodes: {fingerprint.get('nodes_count', 'N/A'):,}")
    print(f"  Edges: {fingerprint.get('edges_count', 'N/A'):,}")
    print(f"  Timeseries: {fingerprint.get('timeseries_count', 'N/A'):,}")
    
    input("\nPress Enter...")


def workflow_benchmark():
    """Run benchmark."""
    print_header("RUN BENCHMARK")
    
    from basetype_benchmark.runner.scenario import run_scenario
    from basetype_benchmark.runner import docker
    
    # Dataset selection
    datasets = get_available_datasets()
    if not datasets:
        print("No datasets available. Generate one first.")
        input("\nPress Enter...")
        return
    
    print("Available datasets:\n")
    for i, ds in enumerate(datasets, 1):
        print(f"  {i}. {ds['name']} ({ds['size_mb']:.0f} MB)")
    
    ds_choice = prompt(f"\nSelect dataset (1-{len(datasets)})", "1")
    try:
        selected_ds = datasets[int(ds_choice) - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return
    
    # Scenario selection
    print("\nSelect scenario:\n")
    print("  1. P1 - PostgreSQL (relational)")
    print("  2. P2 - PostgreSQL (JSONB)")
    print("  3. M1 - Memgraph (standalone)")
    print("  4. M2 - Memgraph + TimescaleDB")
    print("  5. O1 - Oxigraph (standalone)")
    print("  6. O2 - Oxigraph + TimescaleDB")
    print("  A. ALL - Run all 6 scenarios\n")
    
    scenario_map = {"1": ["P1"], "2": ["P2"], "3": ["M1"], "4": ["M2"], "5": ["O1"], "6": ["O2"],
                    "A": ["P1", "P2", "M1", "M2", "O1", "O2"]}
    
    sc_choice = prompt("Select scenario", "A").upper()
    scenarios = scenario_map.get(sc_choice, ["P1"])
    
    # RAM selection
    print("\nSelect RAM limit:\n")
    print("  1. 4 GB")
    print("  2. 8 GB")
    print("  3. 16 GB")
    print("  4. 32 GB")
    print("  5. 64 GB\n")
    
    ram_map = {"1": 4, "2": 8, "3": 16, "4": 32, "5": 64}
    ram_choice = prompt("Select RAM", "2")
    ram_gb = ram_map.get(ram_choice, 8)
    
    # Confirmation
    print(f"\n{BOLD}Configuration:{RESET}")
    print(f"  Dataset:   {selected_ds['name']}")
    print(f"  Scenarios: {', '.join(scenarios)}")
    print(f"  RAM:       {ram_gb} GB\n")
    
    confirm = input("Start benchmark? [Y/n]: ").strip().lower()
    if confirm == 'n':
        return
    
    # Extract profile from dataset name
    profile = selected_ds['name'].split('_seed')[0] if '_seed' in selected_ds['name'] else selected_ds['name']
    export_dir = selected_ds['path'] / "parquet"
    
    # Run benchmarks
    results = []
    for scenario in scenarios:
        result = run_scenario(
            scenario=scenario,
            export_dir=export_dir,
            profile=profile,
            ram_gb=ram_gb,
        )
        results.append(result)
    
    # Summary
    print_header("BENCHMARK COMPLETE")
    for r in results:
        status = f"{GREEN}✓{RESET}" if r.status == "completed" else f"{RED}✗{RESET}"
        print(f"  {status} {r.scenario}: {r.status}")
    
    docker.stop_all()
    input("\nPress Enter...")


def workflow_publish():
    """Publish results."""
    print_header("PUBLISH RESULTS")
    print("Publication to HuggingFace is not yet implemented in the new runner.")
    print("Use the old run_old.py for this feature.")
    input("\nPress Enter...")


def main_interactive():
    """Main interactive menu."""
    while True:
        print_header("BASETYPE BENCHMARK")
        
        # Show available datasets
        datasets = get_available_datasets()
        if datasets:
            names = [d['name'] for d in datasets]
            total_mb = sum(d['size_mb'] for d in datasets)
            print(f"{DIM}Available datasets: {', '.join(names)}{RESET}")
            print(f"{DIM}On disk: {len(datasets)} datasets, {total_mb:.1f} MB{RESET}\n")
        else:
            print(f"{DIM}No datasets generated yet.{RESET}\n")
        
        print(f"  1. {RED}Purge Datasets{RESET}")
        print("  2. Generate Dataset")
        print("  3. Run Benchmark")
        print("  4. Publish Results")
        print("  0. Exit\n")
        
        choice = prompt("Select", "2")
        
        if choice == "1":
            workflow_purge()
        elif choice == "2":
            workflow_generate()
        elif choice == "3":
            workflow_benchmark()
        elif choice == "4":
            workflow_publish()
        elif choice == "0":
            from basetype_benchmark.runner import docker
            docker.stop_all()
            print("Goodbye.")
            break


def cmd_generate(args):
    """Generate a dataset (CLI mode)."""
    from basetype_benchmark.dataset.dataset_manager import DatasetManager
    
    if len(args) < 1:
        print("Usage: python run.py generate <profile> [--seed SEED]")
        print("\nProfiles: small-2d, small-1w, small-1m, medium-2d, etc.")
        sys.exit(1)
    
    profile = args[0]
    seed = 42
    for i, arg in enumerate(args):
        if arg == "--seed" and i + 1 < len(args):
            seed = int(args[i + 1])
    
    print_header("DATASET GENERATION")
    print(f"  Profile: {profile}")
    print(f"  Seed: {seed}\n")
    
    manager = DatasetManager()
    parquet_dir, fingerprint = manager.generate_parquet_only(profile, seed)
    
    print_ok(f"Dataset generated: {parquet_dir}")


def main():
    """Main entry point."""
    # Check for CLI subcommands
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        # Generate subcommand
        if arg == "generate":
            cmd_generate(sys.argv[2:])
            return
        
        # Scenario or --help
        if arg in ["P1", "P2", "M1", "M2", "O1", "O2", "ALL", "--help", "-h"]:
            from basetype_benchmark.runner.cli import main as runner_main
            runner_main()
            return
    
    # Interactive mode
    main_interactive()


if __name__ == "__main__":
    main()
