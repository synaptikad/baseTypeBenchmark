#!/usr/bin/env python3
"""CLI interactive unifiée pour le benchmark BOS.

Usage:
    python -m basetype_benchmark.cli

    # Ou via le script installé:
    basetype-cli
"""
from __future__ import annotations

import os
import sys
import time
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from basetype_benchmark.dataset.config import (
    PROFILES, ALIASES, get_profile, get_profile_metrics,
    list_profiles_by_scale, list_profiles_by_duration, SCENARIO_CONFIG
)
from basetype_benchmark.benchmark.ram_config import (
    print_full_feasibility_matrix, estimate_m1_ram_mb, DATASET_ESTIMATES
)


# ANSI colors (Windows compatible via colorama fallback)
try:
    import colorama
    colorama.init()
except ImportError:
    pass

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Print a styled header."""
    width = 60
    print(f"\n{CYAN}{'=' * width}{RESET}")
    print(f"{CYAN}{BOLD}{title.center(width)}{RESET}")
    print(f"{CYAN}{'=' * width}{RESET}\n")


def print_success(msg: str):
    print(f"{GREEN}[OK]{RESET} {msg}")


def print_warning(msg: str):
    print(f"{YELLOW}[!]{RESET} {msg}")


def print_error(msg: str):
    print(f"{RED}[ERROR]{RESET} {msg}")


def print_info(msg: str):
    print(f"{BLUE}[i]{RESET} {msg}")


def prompt(question: str, default: Optional[str] = None) -> str:
    """Prompt user for input with optional default."""
    if default:
        question = f"{question} [{default}]"
    answer = input(f"{question}: ").strip()
    return answer if answer else (default or "")


def prompt_choice(question: str, choices: List[str], default: Optional[str] = None) -> str:
    """Prompt user to choose from a list."""
    print(f"\n{question}")
    for i, choice in enumerate(choices, 1):
        marker = f"{GREEN}*{RESET}" if choice == default else " "
        print(f"  {marker} {i}. {choice}")

    while True:
        answer = prompt("Enter number or name", default)
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return choices[int(answer) - 1]
        if answer in choices:
            return answer
        print_error(f"Invalid choice: {answer}")


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Prompt for yes/no confirmation."""
    suffix = "[Y/n]" if default else "[y/N]"
    answer = prompt(f"{question} {suffix}").lower()
    if not answer:
        return default
    return answer in ('y', 'yes', 'o', 'oui')


def get_storage_info() -> Dict[str, Any]:
    """Get disk storage information."""
    try:
        total, used, free = shutil.disk_usage(Path.cwd())
        return {
            'total_gb': round(total / (1024**3), 1),
            'used_gb': round(used / (1024**3), 1),
            'free_gb': round(free / (1024**3), 1),
            'usage_percent': round((used / total) * 100, 1)
        }
    except Exception as e:
        return {'error': str(e)}


# =============================================================================
# DATASET COMMANDS
# =============================================================================

def cmd_dataset_list():
    """List all available dataset profiles."""
    print_header("DATASET PROFILES")

    by_scale = list_profiles_by_scale()

    for scale, profiles in by_scale.items():
        print(f"\n{BOLD}{scale.upper()}{RESET} (structure):")
        for p in sorted(profiles):
            profile = PROFILES[p]
            metrics = get_profile_metrics(profile)
            size = metrics['estimated_size_gb']
            nodes = metrics['nodes_estimate']
            samples = metrics['timeseries_samples']

            # M1 RAM requirement
            if p in DATASET_ESTIMATES:
                m1_ram = estimate_m1_ram_mb(p)
                m1_info = f", M1 RAM: {m1_ram / 1024:.0f}GB"
            else:
                m1_info = ""

            print(f"  {GREEN}{p:12}{RESET} | {nodes:>8,} nodes | {samples:>12,} samples | ~{size:>5.1f} GB{m1_info}")


def cmd_dataset_info(profile_name: str):
    """Show detailed info about a dataset profile."""
    try:
        profile = get_profile(profile_name)
    except ValueError as e:
        print_error(str(e))
        return

    print_header(f"PROFILE: {profile_name}")

    metrics = get_profile_metrics(profile)

    print(f"{BOLD}Structure:{RESET}")
    print(f"  Floors:     {profile.floors}")
    print(f"  Spaces:     {profile.spaces:,}")
    print(f"  Equipments: {profile.equipments:,}")
    print(f"  Points:     {profile.points:,}")
    print(f"  Meters:     {profile.meters}")
    print(f"  Duration:   {profile.duration_days} days")

    print(f"\n{BOLD}Extended domains:{RESET}")
    print(f"  IT devices:       {profile.it_devices}")
    print(f"  AV systems:       {profile.av_systems}")
    print(f"  Parking spots:    {profile.parking_spots}")
    print(f"  Security devices: {profile.security_devices}")
    print(f"  Persons:          {profile.persons}")
    print(f"  Contracts:        {profile.contracts}")

    print(f"\n{BOLD}Estimated metrics:{RESET}")
    print(f"  Total nodes:      {metrics['nodes_estimate']:,}")
    print(f"  Total edges:      {metrics['edges_estimate']:,}")
    print(f"  TS points:        {metrics['timeseries_points']:,}")
    print(f"  TS samples:       {metrics['timeseries_samples']:,}")
    print(f"  Est. size:        ~{metrics['estimated_size_gb']:.1f} GB")

    # M1 RAM estimate
    if profile_name in DATASET_ESTIMATES:
        m1_ram = estimate_m1_ram_mb(profile_name)
        print(f"\n{BOLD}Memgraph M1 RAM estimate:{RESET}")
        print(f"  Required:         ~{m1_ram / 1024:.1f} GB")
        if m1_ram > 262144:  # > 256GB
            print_warning(f"M1 will OOM - requires {m1_ram / 1024:.0f}GB (max 256GB)")


def cmd_dataset_generate():
    """Interactive dataset generation."""
    print_header("DATASET GENERATION")

    # Show storage
    storage = get_storage_info()
    if 'error' not in storage:
        print(f"Storage: {storage['used_gb']}/{storage['total_gb']} GB ({storage['usage_percent']}% used)")
        print(f"Free: {storage['free_gb']} GB\n")

    # Choose mode
    mode = prompt_choice(
        "Select generation mode:",
        ["test", "full", "custom"],
        default="test"
    )

    if mode == "test":
        profiles = ["small-2d"]
        print_info("Test mode: generating small-2d (quick validation)")

    elif mode == "full":
        # Show matrix
        print("\nFull benchmark requires these profiles:")
        scales = ["small", "medium", "large"]
        durations = ["2d", "1w", "1m"]  # Reasonable subset for full
        profiles = [f"{s}-{d}" for s in scales for d in durations]
        for p in profiles:
            print(f"  - {p}")

        if not prompt_yes_no("\nGenerate all these profiles?"):
            return

    elif mode == "custom":
        print("\nAvailable profiles:")
        all_profiles = sorted(PROFILES.keys())
        for i, p in enumerate(all_profiles, 1):
            print(f"  {i:2}. {p}")

        selection = prompt("Enter profile numbers (comma-separated) or names")
        profiles = []
        for item in selection.split(","):
            item = item.strip()
            if item.isdigit():
                idx = int(item) - 1
                if 0 <= idx < len(all_profiles):
                    profiles.append(all_profiles[idx])
            elif item in PROFILES or item in ALIASES:
                profiles.append(item)

        if not profiles:
            print_error("No valid profiles selected")
            return

        print(f"\nSelected: {', '.join(profiles)}")
        if not prompt_yes_no("Continue?"):
            return

    # Seed
    seed = int(prompt("Random seed", "42"))

    # Generate
    print_header("GENERATING DATASETS")

    for i, profile_name in enumerate(profiles, 1):
        print(f"\n[{i}/{len(profiles)}] Generating {profile_name}...")

        try:
            from basetype_benchmark.dataset.orchestrator import DatasetOrchestrator

            orchestrator = DatasetOrchestrator()
            start = time.time()
            result = orchestrator.generate_profile(profile_name, seed)
            duration = time.time() - start

            if result:
                print_success(f"{profile_name} generated in {duration:.1f}s")
            else:
                print_error(f"Failed to generate {profile_name}")

        except ImportError:
            # Fallback to legacy generator
            print_warning("Using legacy generator...")
            os.environ["SCALE_MODE"] = profile_name
            os.environ["SEED"] = str(seed)
            from basetype_benchmark.dataset.run import main as legacy_main
            legacy_main()
            print_success(f"{profile_name} generated")

    print_success("\nGeneration complete!")


def cmd_dataset_verify():
    """Verify generated dataset integrity."""
    print_header("DATASET VERIFICATION")

    # Find data directories
    data_dirs = []
    base_paths = [
        Path("data"),
        Path("src/basetype_benchmark/dataset/cache"),
        Path("src/basetype_benchmark/dataset/exports"),
    ]

    for base in base_paths:
        if base.exists():
            for d in base.iterdir():
                if d.is_dir():
                    data_dirs.append(d)

    if not data_dirs:
        print_warning("No dataset directories found")
        print_info("Generate a dataset first with: dataset generate")
        return

    print("Found datasets:")
    for d in data_dirs:
        size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        files = list(d.rglob("*"))
        print(f"  {d.name}: {len(files)} files, {size / 1024**2:.1f} MB")

    # Verify selected
    target = prompt_choice(
        "Select dataset to verify:",
        [d.name for d in data_dirs] + ["all"]
    )

    dirs_to_verify = data_dirs if target == "all" else [d for d in data_dirs if d.name == target]

    for d in dirs_to_verify:
        print(f"\n{BOLD}Verifying {d.name}...{RESET}")

        # Check expected files
        expected_files = {
            "PostgreSQL": ["nodes.csv", "edges.csv", "timeseries.jsonl"],
            "Memgraph": ["nodes.csv", "edges.csv"],
            "RDF": ["graph.ttl", "graph.nt"],
        }

        found_files = [f.name for f in d.rglob("*") if f.is_file()]

        for engine, files in expected_files.items():
            found = sum(1 for f in files if f in found_files or any(f in ff for ff in found_files))
            total = len(files)
            status = f"{GREEN}OK{RESET}" if found >= 1 else f"{YELLOW}PARTIAL{RESET}" if found > 0 else f"{RED}MISSING{RESET}"
            print(f"  {engine}: {status} ({found}/{total} files)")

        # Row counts
        for csv_file in d.rglob("*.csv"):
            with open(csv_file, 'r', encoding='utf-8') as f:
                count = sum(1 for _ in f) - 1  # Exclude header
            print(f"    {csv_file.name}: {count:,} rows")


# =============================================================================
# BENCHMARK COMMANDS
# =============================================================================

def cmd_benchmark_matrix():
    """Show RAM feasibility matrix for all engines."""
    print_header("RAM FEASIBILITY MATRIX")
    print_full_feasibility_matrix()


def cmd_benchmark_run():
    """Interactive benchmark runner."""
    print_header("BENCHMARK RUNNER")

    # Check prerequisites
    print("Checking prerequisites...")

    # Docker check
    docker_ok = shutil.which("docker") is not None
    if docker_ok:
        print_success("Docker: installed")
    else:
        print_error("Docker: not found")
        return

    # Storage check
    storage = get_storage_info()
    if 'error' not in storage:
        print_success(f"Storage: {storage['free_gb']:.1f} GB free")

    # Mode selection
    mode = prompt_choice(
        "Select benchmark mode:",
        ["test", "scenario", "full", "custom"],
        default="test"
    )

    if mode == "test":
        print_info("Test mode: quick validation run")
        profiles = ["small-2d"]
        scenarios = ["P1"]  # Just PostgreSQL relational
        ram_levels = [4096]

    elif mode == "scenario":
        print("\nAvailable scenarios:")
        for name, config in SCENARIO_CONFIG.items():
            print(f"  {name}: {config['name']}")

        scenario = prompt_choice(
            "Select scenario:",
            list(SCENARIO_CONFIG.keys()),
            default="P1"
        )
        scenarios = [scenario]
        profiles = [prompt_choice("Select profile:", sorted(PROFILES.keys()), default="small-1w")]
        ram_levels = [4096, 8192, 16384]

    elif mode == "full":
        print_warning("Full mode runs all scenarios x profiles x RAM levels")
        print_warning("This can take 24-48 hours on a large server!")

        if not prompt_yes_no("Continue with full benchmark?", default=False):
            return

        scenarios = list(SCENARIO_CONFIG.keys())
        profiles = ["small-2d", "small-1w", "small-1m", "medium-2d", "medium-1w"]
        ram_levels = [2048, 4096, 8192, 16384, 32768, 65536]

    elif mode == "custom":
        # Custom selection
        print("\nScenarios:")
        for i, (name, config) in enumerate(SCENARIO_CONFIG.items(), 1):
            print(f"  {i}. {name}: {config['name']}")

        scenario_input = prompt("Select scenarios (comma-separated numbers or names)")
        scenarios = []
        all_scenarios = list(SCENARIO_CONFIG.keys())
        for item in scenario_input.split(","):
            item = item.strip()
            if item.isdigit():
                idx = int(item) - 1
                if 0 <= idx < len(all_scenarios):
                    scenarios.append(all_scenarios[idx])
            elif item.upper() in SCENARIO_CONFIG:
                scenarios.append(item.upper())

        if not scenarios:
            scenarios = ["P1"]

        print("\nProfiles:")
        all_profiles = sorted(PROFILES.keys())
        for i, p in enumerate(all_profiles, 1):
            print(f"  {i:2}. {p}")

        profile_input = prompt("Select profiles (comma-separated)", "small-1w")
        profiles = []
        for item in profile_input.split(","):
            item = item.strip()
            if item.isdigit():
                idx = int(item) - 1
                if 0 <= idx < len(all_profiles):
                    profiles.append(all_profiles[idx])
            elif item in PROFILES:
                profiles.append(item)

        if not profiles:
            profiles = ["small-1w"]

        ram_input = prompt("RAM levels in MB (comma-separated)", "4096,8192,16384")
        ram_levels = [int(x.strip()) for x in ram_input.split(",") if x.strip().isdigit()]

    # Summary
    print_header("BENCHMARK CONFIGURATION")
    print(f"Scenarios:  {', '.join(scenarios)}")
    print(f"Profiles:   {', '.join(profiles)}")
    print(f"RAM levels: {', '.join(str(r) for r in ram_levels)} MB")

    total_runs = len(scenarios) * len(profiles) * len(ram_levels)
    print(f"\nTotal runs: {total_runs}")

    if not prompt_yes_no("\nStart benchmark?"):
        return

    # Run benchmark
    print_header("RUNNING BENCHMARK")

    results_dir = Path("benchmark_results") / datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir.mkdir(parents=True, exist_ok=True)
    print_info(f"Results will be saved to: {results_dir}")

    checkpoint_file = results_dir / "checkpoint.json"

    completed = []
    failed = []

    for scenario in scenarios:
        for profile in profiles:
            for ram in ram_levels:
                run_id = f"{scenario}_{profile}_{ram}MB"

                # Check RAM feasibility for M1
                if scenario == "M1" and profile in DATASET_ESTIMATES:
                    required_ram = estimate_m1_ram_mb(profile)
                    if required_ram > ram:
                        print_warning(f"Skipping {run_id}: M1 requires {required_ram/1024:.0f}GB RAM")
                        continue

                print(f"\n{BOLD}[{len(completed)+len(failed)+1}/{total_runs}] {run_id}{RESET}")

                try:
                    # TODO: Actual benchmark execution
                    # For now, placeholder
                    print_info(f"Running {scenario} on {profile} with {ram}MB RAM...")

                    # Simulate benchmark (replace with actual call)
                    # from basetype_benchmark.benchmark.full_orchestrator import BenchmarkOrchestrator
                    # orch = BenchmarkOrchestrator()
                    # result = orch.run_single(scenario, profile, ram)

                    time.sleep(0.5)  # Placeholder

                    completed.append(run_id)
                    print_success(f"Completed: {run_id}")

                except Exception as e:
                    failed.append(run_id)
                    print_error(f"Failed: {run_id} - {e}")

                # Save checkpoint
                with open(checkpoint_file, 'w') as f:
                    json.dump({
                        'completed': completed,
                        'failed': failed,
                        'remaining': total_runs - len(completed) - len(failed)
                    }, f, indent=2)

    # Summary
    print_header("BENCHMARK COMPLETE")
    print(f"Completed: {len(completed)}")
    print(f"Failed:    {len(failed)}")
    print(f"Results:   {results_dir}")

    if failed:
        print(f"\nFailed runs:")
        for f in failed:
            print(f"  - {f}")


def cmd_benchmark_publish():
    """Publish results to HuggingFace Hub."""
    print_header("PUBLISH TO HUGGINGFACE")

    # Check for results
    results_dir = Path("benchmark_results")
    if not results_dir.exists():
        print_error("No benchmark results found")
        return

    result_dirs = sorted([d for d in results_dir.iterdir() if d.is_dir()], reverse=True)
    if not result_dirs:
        print_error("No benchmark result directories found")
        return

    print("Available results:")
    for i, d in enumerate(result_dirs[:10], 1):
        files = list(d.glob("*.json"))
        print(f"  {i}. {d.name} ({len(files)} files)")

    selection = prompt("Select result directory (number)", "1")
    if selection.isdigit():
        idx = int(selection) - 1
        if 0 <= idx < len(result_dirs):
            selected_dir = result_dirs[idx]
        else:
            print_error("Invalid selection")
            return
    else:
        print_error("Invalid selection")
        return

    print(f"\nSelected: {selected_dir.name}")

    # Request HF token interactively
    print("\n" + "=" * 50)
    print("HuggingFace token required for publishing")
    print("Get your token at: https://huggingface.co/settings/tokens")
    print("=" * 50 + "\n")

    import getpass
    hf_token = getpass.getpass("Enter HuggingFace token (hidden): ")

    if not hf_token or not hf_token.startswith("hf_"):
        print_error("Invalid token format (should start with 'hf_')")
        return

    # Confirm
    repo_name = prompt("HuggingFace repo name", "synaptikad/basetype-benchmark-results")

    if not prompt_yes_no(f"\nPublish to {repo_name}?"):
        return

    print_info("Publishing...")

    try:
        from huggingface_hub import HfApi

        api = HfApi(token=hf_token)

        # Upload
        api.upload_folder(
            folder_path=str(selected_dir),
            repo_id=repo_name,
            repo_type="dataset",
            commit_message=f"Benchmark results {selected_dir.name}"
        )

        print_success(f"Published to https://huggingface.co/datasets/{repo_name}")

    except ImportError:
        print_error("huggingface_hub not installed. Run: pip install huggingface_hub")
    except Exception as e:
        print_error(f"Publication failed: {e}")


# =============================================================================
# MAIN MENU
# =============================================================================

def main_menu():
    """Main interactive menu."""
    while True:
        print_header("BASETYPE BENCHMARK CLI")

        print(f"{BOLD}Dataset:{RESET}")
        print("  1. list      - List available profiles")
        print("  2. info      - Profile details")
        print("  3. generate  - Generate dataset")
        print("  4. verify    - Verify dataset integrity")

        print(f"\n{BOLD}Benchmark:{RESET}")
        print("  5. matrix    - Show RAM feasibility matrix")
        print("  6. run       - Run benchmark")
        print("  7. publish   - Publish results to HuggingFace")

        print(f"\n{BOLD}Other:{RESET}")
        print("  8. storage   - Show storage info")
        print("  q. quit      - Exit")

        choice = prompt("\nSelect option").lower()

        if choice in ('1', 'list'):
            cmd_dataset_list()
        elif choice in ('2', 'info'):
            profile = prompt("Profile name", "small-1w")
            cmd_dataset_info(profile)
        elif choice in ('3', 'generate'):
            cmd_dataset_generate()
        elif choice in ('4', 'verify'):
            cmd_dataset_verify()
        elif choice in ('5', 'matrix'):
            cmd_benchmark_matrix()
        elif choice in ('6', 'run'):
            cmd_benchmark_run()
        elif choice in ('7', 'publish'):
            cmd_benchmark_publish()
        elif choice in ('8', 'storage'):
            storage = get_storage_info()
            print_header("STORAGE INFO")
            if 'error' in storage:
                print_error(storage['error'])
            else:
                print(f"Total:  {storage['total_gb']:.1f} GB")
                print(f"Used:   {storage['used_gb']:.1f} GB")
                print(f"Free:   {storage['free_gb']:.1f} GB")
                print(f"Usage:  {storage['usage_percent']:.1f}%")
        elif choice in ('q', 'quit', 'exit'):
            print_info("Goodbye!")
            break
        else:
            print_error(f"Unknown option: {choice}")

        input("\nPress Enter to continue...")


def cli_main():
    """Entry point for CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Basetype Benchmark CLI - Interactive tools for dataset generation and benchmarking"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Dataset commands
    ds_list = subparsers.add_parser("list", help="List dataset profiles")

    ds_info = subparsers.add_parser("info", help="Show profile details")
    ds_info.add_argument("profile", help="Profile name (e.g., small-1w)")

    ds_gen = subparsers.add_parser("generate", help="Generate dataset")
    ds_gen.add_argument("--profile", "-p", help="Profile name")
    ds_gen.add_argument("--seed", "-s", type=int, default=42, help="Random seed")
    ds_gen.add_argument("--mode", "-m", choices=["test", "full", "custom"], help="Generation mode")

    ds_verify = subparsers.add_parser("verify", help="Verify dataset")

    # Benchmark commands
    bm_matrix = subparsers.add_parser("matrix", help="Show RAM feasibility matrix")

    bm_run = subparsers.add_parser("run", help="Run benchmark")
    bm_run.add_argument("--scenario", "-s", help="Scenario (P1, P2, M1, M2, O1, O2)")
    bm_run.add_argument("--profile", "-p", help="Profile name")
    bm_run.add_argument("--ram", "-r", type=int, help="RAM limit in MB")

    bm_publish = subparsers.add_parser("publish", help="Publish to HuggingFace")

    # Interactive mode
    subparsers.add_parser("interactive", help="Start interactive menu")

    args = parser.parse_args()

    if args.command == "list":
        cmd_dataset_list()
    elif args.command == "info":
        cmd_dataset_info(args.profile)
    elif args.command == "generate":
        if args.mode or args.profile:
            # Non-interactive generation
            profile = args.profile or "small-2d"
            print_info(f"Generating {profile} with seed {args.seed}...")
            # TODO: Direct generation
        else:
            cmd_dataset_generate()
    elif args.command == "verify":
        cmd_dataset_verify()
    elif args.command == "matrix":
        cmd_benchmark_matrix()
    elif args.command == "run":
        cmd_benchmark_run()
    elif args.command == "publish":
        cmd_benchmark_publish()
    elif args.command == "interactive" or args.command is None:
        main_menu()
    else:
        parser.print_help()


if __name__ == "__main__":
    cli_main()
