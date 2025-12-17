#!/usr/bin/env python3
"""BaseType Benchmark - Main Workflow

Interactive workflow for:
1. Dataset generation (choose scale + duration)
2. Benchmark execution (per scenario, manages containers)
3. Results publication to HuggingFace
"""
from __future__ import annotations

import os
import sys
import subprocess
import time
import json
import getpass
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple

# Setup path
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


def print_err(msg: str):
    print(f"{RED}[ERROR]{RESET} {msg}")


def print_info(msg: str):
    print(f"{BLUE}[i]{RESET} {msg}")


def prompt(question: str, default: str = "") -> str:
    if default:
        answer = input(f"{question} [{default}]: ").strip()
        return answer if answer else default
    return input(f"{question}: ").strip()


def prompt_yes_no(question: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{question} {suffix}: ").strip().lower()
    if not answer:
        return default
    return answer in ('y', 'yes')


def run_cmd(cmd: str, cwd: str = None) -> bool:
    """Run shell command, return success."""
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError:
        return False


# =============================================================================
# CONFIGURATION
# =============================================================================

SCENARIOS = {
    "P1": {"name": "PostgreSQL Relational", "containers": ["timescaledb"]},
    "P2": {"name": "PostgreSQL JSONB", "containers": ["timescaledb"]},
    "M1": {"name": "Memgraph Standalone", "containers": ["memgraph"]},
    "M2": {"name": "Memgraph + TimescaleDB", "containers": ["memgraph", "timescaledb"]},
    "O1": {"name": "Oxigraph Standalone", "containers": ["oxigraph"]},
    "O2": {"name": "Oxigraph + TimescaleDB", "containers": ["oxigraph", "timescaledb"]},
}

# Scale definitions
SCALES = {
    "small": {
        "points": "50k",
        "description": "Standard office building (25 floors, 1250 spaces)",
    },
    "medium": {
        "points": "100k",
        "description": "Large building or small campus (50 floors, 2500 spaces)",
    },
    "large": {
        "points": "500k",
        "description": "University campus or business district (100 floors, 5000 spaces)",
    },
}

# Duration definitions
DURATIONS = {
    "2d": {"days": 2, "description": "Quick tests, in-memory comparison"},
    "1w": {"days": 7, "description": "Daily operations debugging"},
    "1m": {"days": 30, "description": "Monthly analysis"},
    "6m": {"days": 180, "description": "Seasonal patterns"},
    "1y": {"days": 365, "description": "Annual reporting, long-term analytics"},
}

# Estimated sizes (GB) for scale+duration combinations
SIZE_ESTIMATES = {
    "small-2d": 0.5, "small-1w": 1, "small-1m": 5, "small-6m": 27, "small-1y": 55,
    "medium-2d": 1, "medium-1w": 2, "medium-1m": 10, "medium-6m": 54, "medium-1y": 110,
    "large-2d": 5, "large-1w": 11, "large-1m": 45, "large-6m": 270, "large-1y": 550,
}

DOCKER_DIR = Path(__file__).parent / "docker"

# HuggingFace repository for datasets
HF_DATASET_REPO = "synaptikad/basetype-benchmark"


# =============================================================================
# HUGGINGFACE DOWNLOAD
# =============================================================================

def download_from_huggingface(profile: str, seed: int = 42):
    """Download dataset from HuggingFace Hub for exact reproducibility."""
    try:
        from huggingface_hub import hf_hub_download, list_repo_files
    except ImportError:
        print_err("huggingface_hub not installed")
        print_info("Install with: pip install huggingface_hub")
        return False

    print_info(f"Checking HuggingFace repository: {HF_DATASET_REPO}")

    try:
        # Check if dataset exists on HuggingFace
        files = list_repo_files(HF_DATASET_REPO, repo_type="dataset")
        cache_filename = f"{profile}_seed{seed}.pkl.gz"

        if cache_filename not in files:
            print_err(f"Dataset {profile} (seed {seed}) not found on HuggingFace")
            print_info("Available files:")
            for f in files[:10]:
                print(f"  - {f}")
            print_info("\nYou can generate locally instead (option 1)")
            return False

        # Download to cache directory
        cache_dir = Path("src/basetype_benchmark/dataset/cache")
        cache_dir.mkdir(parents=True, exist_ok=True)

        print_info(f"Downloading {cache_filename}...")
        start = time.time()

        downloaded_path = hf_hub_download(
            repo_id=HF_DATASET_REPO,
            filename=cache_filename,
            repo_type="dataset",
            local_dir=cache_dir,
            local_dir_use_symlinks=False
        )

        elapsed = time.time() - start
        size_mb = Path(downloaded_path).stat().st_size / (1024 * 1024)

        print_ok(f"Downloaded in {elapsed:.1f}s ({size_mb:.1f} MB)")
        print_info(f"Cached at: {downloaded_path}")

        # Verify the dataset
        print_info("Verifying dataset integrity...")
        from basetype_benchmark.dataset.dataset_manager import DatasetManager
        manager = DatasetManager()
        dataset, summary = manager.load_dataset(Path(downloaded_path))

        print_ok("Dataset verified")
        print_info(f"Nodes: {summary.node_count:,}")
        print_info(f"Edges: {summary.edge_count:,}")
        print_info(f"Timeseries points: {len(dataset.timeseries):,}")

        return True

    except Exception as e:
        print_err(f"HuggingFace download failed: {e}")
        print_info("You can generate locally instead (option 1)")
        return False


# =============================================================================
# CONTAINER MANAGEMENT
# =============================================================================

def stop_all_containers():
    """Stop all benchmark containers."""
    print_info("Stopping all containers...")
    run_cmd("docker compose down", cwd=str(DOCKER_DIR))


def start_containers(containers: List[str]) -> bool:
    """Start specific containers."""
    stop_all_containers()
    print_info(f"Starting: {', '.join(containers)}")

    if not run_cmd(f"docker compose up -d {' '.join(containers)}", cwd=str(DOCKER_DIR)):
        print_err("Failed to start containers")
        return False

    # Wait longer for containers to be ready (Memgraph needs more time)
    wait_time = 5
    print_info(f"Waiting {wait_time}s for containers to initialize...")
    time.sleep(wait_time)
    print_ok("Containers started (connection retry handled by loaders)")
    return True


def check_dataset(profile: str, seed: int = 42) -> bool:
    """Check if dataset has been exported to disk."""
    export_dir = Path("src/basetype_benchmark/dataset/exports") / f"{profile}_seed{seed}"
    return export_dir.exists() and any(export_dir.glob("*.csv"))


def get_available_profiles() -> List[str]:
    """Get list of profiles that have datasets exported on disk."""
    available = []
    export_dir = Path("src/basetype_benchmark/dataset/exports")
    if export_dir.exists():
        for subdir in export_dir.iterdir():
            if subdir.is_dir() and any(subdir.glob("*.csv")):
                # Extract profile name from directory name (e.g., "small-1w_seed42" -> "small-1w")
                name = subdir.name.rsplit("_seed", 1)[0]
                if name not in available:
                    available.append(name)
    return sorted(available)


# =============================================================================
# WORKFLOW: DATASET
# =============================================================================

def workflow_dataset():
    """Dataset generation workflow."""
    print_header("DATASET GENERATION")

    # Step 1: Choose scale
    print(f"{BOLD}Step 1: Choose graph scale (number of measurement points){RESET}\n")
    print("The scale determines the size of the building/campus model:\n")

    scale_list = list(SCALES.keys())
    for i, (name, info) in enumerate(SCALES.items(), 1):
        print(f"  {i}. {name:8} ({info['points']} points)")
        print(f"     {DIM}{info['description']}{RESET}\n")

    print(f"  0. Back\n")

    choice = prompt("Select scale", "1")
    if choice == "0":
        return

    try:
        idx = int(choice) - 1
        if not (0 <= idx < len(scale_list)):
            raise ValueError()
        scale = scale_list[idx]
    except ValueError:
        print_err("Invalid choice")
        return

    # Step 2: Choose duration
    print_header("TIMESERIES DURATION")
    print(f"{BOLD}Step 2: Choose timeseries duration{RESET}\n")
    print("The duration determines how much historical data is generated.")
    print("Longer durations = more timeseries samples = larger dataset.\n")

    duration_list = list(DURATIONS.keys())
    for i, (name, info) in enumerate(DURATIONS.items(), 1):
        profile = f"{scale}-{name}"
        size = SIZE_ESTIMATES.get(profile, "?")
        status = f"{GREEN}[ready]{RESET}" if check_dataset(profile) else ""
        print(f"  {i}. {name:4} ({info['days']:3} days) - ~{size:>3} GB  {status}")
        print(f"     {DIM}{info['description']}{RESET}\n")

    print(f"  0. Back\n")

    choice = prompt("Select duration", "1")
    if choice == "0":
        return

    try:
        idx = int(choice) - 1
        if not (0 <= idx < len(duration_list)):
            raise ValueError()
        duration = duration_list[idx]
    except ValueError:
        print_err("Invalid choice")
        return

    profile = f"{scale}-{duration}"

    # Confirm
    print_header("CONFIRM GENERATION")
    size = SIZE_ESTIMATES.get(profile, "?")
    print(f"Profile:  {profile}")
    print(f"Scale:    {SCALES[scale]['points']} measurement points")
    print(f"Duration: {DURATIONS[duration]['days']} days of timeseries")
    print(f"Size:     ~{size} GB estimated")

    if check_dataset(profile):
        print(f"\n{YELLOW}Dataset already exists.{RESET}")
        if not prompt_yes_no("Regenerate?", False):
            return

    # Choose source
    print_header("DATA SOURCE")
    print("Choose how to obtain the dataset:\n")
    print(f"  1. {BOLD}Generate locally{RESET} (deterministic, uses seed)")
    print(f"     {DIM}Generates dataset and exports to CSV files on disk{RESET}\n")
    print(f"  2. {BOLD}Download from HuggingFace{RESET} (exact reproduction)")
    print(f"     {DIM}Downloads pre-generated dataset for academic reproducibility{RESET}\n")
    print(f"  0. Back\n")

    source_choice = prompt("Select source", "1")
    if source_choice == "0":
        return

    use_huggingface = source_choice == "2"

    seed = prompt("\nSeed (for reproducibility)", "42")

    action = "Download" if use_huggingface else "Generate"
    if not prompt_yes_no(f"\n{action} {profile}?"):
        return

    # Generate or download
    if use_huggingface:
        print_header(f"DOWNLOADING {profile} FROM HUGGINGFACE")
        try:
            download_from_huggingface(profile, int(seed))
        except Exception as e:
            print_err(f"Download failed: {e}")
    else:
        print_header(f"GENERATING {profile}")
        try:
            from basetype_benchmark.dataset.dataset_manager import DatasetManager

            manager = DatasetManager()
            # Génère et exporte directement sur disque (pas de cache pickle)
            export_path, summary = manager.generate_and_export(profile, int(seed))
            print()
            print_ok(f"Dataset ready at: {export_path}")

        except ImportError as e:
            print_err(f"Import error: {e}")
            print_info("Try: pip install -e . && pip install -r requirements.txt")
        except KeyboardInterrupt:
            print()
            print_warn("Generation interrupted by user")
        except Exception as e:
            import traceback
            print_err(f"Generation failed: {e}")
            traceback.print_exc()

    input("\nPress Enter...")


# =============================================================================
# RAM CONFIGURATION
# =============================================================================

# RAM levels to test (in GB)
RAM_LEVELS = [4, 8, 16, 32, 64, 128]

# Minimum RAM per scale (estimated)
MIN_RAM_BY_SCALE = {
    "small": {"P1": 4, "P2": 4, "M1": 8, "M2": 8, "O1": 4, "O2": 4},
    "medium": {"P1": 8, "P2": 8, "M1": 16, "M2": 16, "O1": 8, "O2": 8},
    "large": {"P1": 16, "P2": 16, "M1": 64, "M2": 64, "O1": 16, "O2": 16},
}

# Performance plateau threshold (if improvement < this %, stop iterating)
PERF_PLATEAU_THRESHOLD = 10  # 10% improvement threshold


def get_scale_from_profile(profile: str) -> str:
    """Extract scale from profile name (e.g., 'small-1w' -> 'small')."""
    return profile.split("-")[0]


def get_duration_from_profile(profile: str) -> str:
    """Extract duration from profile name (e.g., 'small-1w' -> '1w')."""
    return profile.split("-")[1]


def can_extract_subset(source_profile: str, target_scale: str, target_duration: str) -> bool:
    """Check if target subset can be extracted from source profile."""
    source_scale = get_scale_from_profile(source_profile)
    source_duration = get_duration_from_profile(source_profile)

    # Scale hierarchy: large > medium > small
    scale_order = {"small": 0, "medium": 1, "large": 2}
    # Duration hierarchy: 1y > 6m > 1m > 1w > 2d
    duration_order = {"2d": 0, "1w": 1, "1m": 2, "6m": 3, "1y": 4}

    source_scale_idx = scale_order.get(source_scale, -1)
    target_scale_idx = scale_order.get(target_scale, -1)
    source_duration_idx = duration_order.get(source_duration, -1)
    target_duration_idx = duration_order.get(target_duration, -1)

    return source_scale_idx >= target_scale_idx and source_duration_idx >= target_duration_idx


def get_extractable_profiles(source_profile: str) -> List[str]:
    """Get list of profiles that can be extracted from source."""
    source_scale = get_scale_from_profile(source_profile)
    source_duration = get_duration_from_profile(source_profile)

    scale_order = {"small": 0, "medium": 1, "large": 2}
    duration_order = {"2d": 0, "1w": 1, "1m": 2, "6m": 3, "1y": 4}

    source_scale_idx = scale_order.get(source_scale, 0)
    source_duration_idx = duration_order.get(source_duration, 0)

    profiles = []
    for scale, sidx in scale_order.items():
        if sidx <= source_scale_idx:
            for duration, didx in duration_order.items():
                if didx <= source_duration_idx:
                    profile = f"{scale}-{duration}"
                    if profile != source_profile:  # Exclude source itself
                        profiles.append(profile)

    return sorted(profiles)


def select_engines() -> List[str]:
    """Interactive engine selection."""
    print_header("SELECT ENGINES")
    print("Choose which database engines to benchmark:\n")

    print(f"  A. {BOLD}All engines{RESET} (P1, P2, M1, M2, O1, O2)")
    print(f"  S. {BOLD}Select individually{RESET}\n")
    print(f"  0. Back\n")

    choice = prompt("Select", "A").upper()

    if choice == "0":
        return []

    if choice == "A":
        return list(SCENARIOS.keys())

    # Individual selection
    print_header("ENGINE SELECTION")
    print("Answer Y/N for each engine:\n")

    selected = []
    for sid, info in SCENARIOS.items():
        containers = ", ".join(info["containers"])
        print(f"  {sid}: {info['name']}")
        print(f"  {DIM}Containers: {containers}{RESET}")
        if prompt_yes_no(f"  Include {sid}?", True):
            selected.append(sid)
        print()

    return selected


def get_ram_strategy(scenario: str, scale: str) -> Dict:
    """Get RAM testing strategy for a scenario.

    Returns dict with:
        - start_ram: initial RAM to try
        - strategy: 'iterate_up' (P1/P2) or 'escalate_on_oom' (M/O)
        - max_ram: maximum RAM to test
    """
    min_ram = MIN_RAM_BY_SCALE.get(scale, MIN_RAM_BY_SCALE["small"]).get(scenario, 8)

    if scenario.startswith("P"):
        # PostgreSQL: start from minimum, iterate up until plateau
        return {
            "start_ram": min_ram,
            "strategy": "iterate_up",
            "max_ram": 128,
            "description": "Start low, iterate until performance plateau"
        }
    else:
        # Memgraph/Oxigraph: start from minimum, escalate on OOM
        return {
            "start_ram": min_ram,
            "strategy": "escalate_on_oom",
            "max_ram": 128,
            "description": "Start low, escalate on OOM, continue to find plateau"
        }


def start_containers_with_ram(containers: List[str], ram_gb: int) -> bool:
    """Start containers with specific RAM limit."""
    stop_all_containers()
    print_info(f"Starting: {', '.join(containers)} with {ram_gb}GB RAM limit")

    # Build docker compose command with memory limit
    mem_limit = f"{ram_gb}g"
    env_vars = f"MEMORY_LIMIT={mem_limit}"

    cmd = f"{env_vars} docker compose up -d {' '.join(containers)}"
    if not run_cmd(cmd, cwd=str(DOCKER_DIR)):
        print_err("Failed to start containers")
        return False

    # Short wait - actual connection retry is handled by loaders
    wait_time = 5
    print_info(f"Waiting {wait_time}s for containers to initialize...")
    time.sleep(wait_time)
    print_ok(f"Containers started ({ram_gb}GB RAM, connection retry handled by loaders)")
    return True


# =============================================================================
# WORKFLOW: BENCHMARK
# =============================================================================

def workflow_benchmark():
    """Benchmark execution workflow."""
    print_header("BENCHMARK EXECUTION")

    # Check datasets
    available = get_available_profiles()
    if not available:
        print_warn("No datasets available. Generate one first (option 2).")
        input("\nPress Enter...")
        return

    print(f"Available datasets: {', '.join(available)}\n")

    # Select dataset
    for i, ds in enumerate(available, 1):
        size = SIZE_ESTIMATES.get(ds, "?")
        extractable = get_extractable_profiles(ds)
        extract_info = ""
        if extractable:
            extract_info = f" {DIM}(can extract: {', '.join(extractable[:3])}{'...' if len(extractable) > 3 else ''}){RESET}"
        print(f"  {i}. {ds} (~{size} GB){extract_info}")
    print(f"\n  0. Back")

    choice = prompt("\nSelect dataset", "1")
    if choice == "0":
        return

    try:
        source_dataset = available[int(choice) - 1]
    except (ValueError, IndexError):
        print_err("Invalid choice")
        return

    # Check if we can extract subsets
    extractable = get_extractable_profiles(source_dataset)

    if extractable:
        print_header("DATASET SCOPE")
        print(f"Source dataset: {BOLD}{source_dataset}{RESET}\n")
        print("You can benchmark on:\n")
        print(f"  1. {BOLD}Full dataset{RESET} ({source_dataset})")
        print(f"  2. {BOLD}Extract subset{RESET} (smaller scale/duration)\n")
        print(f"  0. Back\n")

        scope_choice = prompt("Select", "1")
        if scope_choice == "0":
            return

        if scope_choice == "2":
            # Select scale
            print_header("SELECT SCALE")
            source_scale = get_scale_from_profile(source_dataset)
            scale_order = ["small", "medium", "large"]
            available_scales = [s for s in scale_order if scale_order.index(s) <= scale_order.index(source_scale)]

            for i, scale in enumerate(available_scales, 1):
                info = SCALES[scale]
                print(f"  {i}. {scale:8} ({info['points']} points)")
                print(f"     {DIM}{info['description']}{RESET}\n")
            print(f"  0. Back\n")

            scale_choice = prompt("Select scale", "1")
            if scale_choice == "0":
                return

            try:
                target_scale = available_scales[int(scale_choice) - 1]
            except (ValueError, IndexError):
                print_err("Invalid choice")
                return

            # Select duration
            print_header("SELECT DURATION")
            source_duration = get_duration_from_profile(source_dataset)
            duration_order = ["2d", "1w", "1m", "6m", "1y"]
            available_durations = [d for d in duration_order if duration_order.index(d) <= duration_order.index(source_duration)]

            for i, duration in enumerate(available_durations, 1):
                info = DURATIONS[duration]
                print(f"  {i}. {duration:4} ({info['days']:3} days)")
                print(f"     {DIM}{info['description']}{RESET}\n")
            print(f"  0. Back\n")

            dur_choice = prompt("Select duration", "1")
            if dur_choice == "0":
                return

            try:
                target_duration = available_durations[int(dur_choice) - 1]
            except (ValueError, IndexError):
                print_err("Invalid choice")
                return

            dataset = f"{target_scale}-{target_duration}"
            print_info(f"Will extract {dataset} from {source_dataset}")
        else:
            dataset = source_dataset
    else:
        dataset = source_dataset

    # Select engines
    scenarios = select_engines()
    if not scenarios:
        return

    # RAM strategy display
    scale = get_scale_from_profile(dataset)
    print_header("RAM STRATEGY")
    print(f"Dataset scale: {BOLD}{scale}{RESET}\n")
    print("RAM testing strategy per engine:\n")

    for scenario in scenarios:
        strategy = get_ram_strategy(scenario, scale)
        print(f"  {scenario}: Start at {strategy['start_ram']}GB")
        print(f"      {DIM}{strategy['description']}{RESET}\n")

    # Confirm
    print_header("CONFIRM")
    print(f"Dataset:   {dataset}")
    if dataset != source_dataset:
        print(f"Source:    {source_dataset} (will extract)")
    print(f"Engines:   {', '.join(scenarios)}")
    print(f"\nProtocol per engine:")
    print(f"  1. Start containers with RAM limit")
    print(f"  2. Load data (detect OOM)")
    print(f"  3. Execute benchmark queries (Q1-Q8)")
    print(f"  4. Check performance delta")
    print(f"  5. Iterate RAM if needed")
    print(f"  6. Stop containers")

    if not prompt_yes_no("\nStart benchmark?"):
        return

    # Run
    results_dir = Path("benchmark_results") / datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    for scenario in scenarios:
        print_header(f"RUNNING {scenario}: {SCENARIOS[scenario]['name']}")

        containers = SCENARIOS[scenario]["containers"]
        strategy = get_ram_strategy(scenario, scale)

        ram_results = []
        current_ram = strategy["start_ram"]
        prev_perf = None

        while current_ram <= strategy["max_ram"]:
            print(f"\n{BOLD}--- Testing with {current_ram}GB RAM ---{RESET}\n")

            if not start_containers_with_ram(containers, current_ram):
                if strategy["strategy"] == "escalate_on_oom":
                    print_warn(f"Container failed at {current_ram}GB, escalating...")
                    current_ram = RAM_LEVELS[RAM_LEVELS.index(current_ram) + 1] if current_ram < max(RAM_LEVELS) else None
                    if current_ram is None:
                        print_err("Max RAM reached, cannot continue")
                        break
                    continue
                else:
                    results[scenario] = "container_error"
                    break

            try:
                # Real benchmark execution
                from basetype_benchmark.benchmark_executor import BenchmarkExecutor, format_detailed_results

                # Get dataset export path
                export_dir = Path("src/basetype_benchmark/dataset/exports") / f"{dataset}_seed42"
                if not export_dir.exists():
                    # Try source dataset if extracting subset
                    export_dir = Path("src/basetype_benchmark/dataset/exports") / f"{source_dataset}_seed42"

                executor = BenchmarkExecutor()

                def progress_callback(phase, message):
                    if phase == "query":
                        print(f"    {message}")
                    elif phase == "query_done":
                        print(f"    {GREEN}[OK]{RESET} {message}")
                    elif phase in ["load", "connect", "schema", "clear"]:
                        print_info(message)
                    elif phase == "load_done":
                        print_ok(message)

                print_info(f"Executing {scenario} on {dataset} with {current_ram}GB RAM...")

                bench_result = executor.run_benchmark(
                    scenario=scenario,
                    dataset_dir=export_dir,
                    ram_gb=current_ram,
                    callback=progress_callback
                )

                if bench_result.status == "oom":
                    raise MemoryError("OOM detected")
                elif bench_result.status == "error":
                    raise Exception(bench_result.error)

                # Convert p95 from ms to seconds for comparison
                current_perf = bench_result.overall_p95 / 1000.0

                ram_results.append({
                    "ram_gb": current_ram,
                    "status": "completed",
                    "p95_latency": current_perf,
                    "p50_latency": bench_result.overall_p50 / 1000.0,
                    "load_time": bench_result.load_time_s,
                    "query_stats": {
                        qid: {
                            "p50": qs.p50,
                            "p95": qs.p95,
                            "min": qs.min_latency,
                            "max": qs.max_latency,
                            "runs": qs.success_count
                        }
                        for qid, qs in bench_result.query_stats.items()
                    }
                })

                # Print detailed results
                print(format_detailed_results(bench_result))
                print_ok(f"{scenario} @ {current_ram}GB completed (p95: {current_perf:.2f}s)")

                # Check for plateau
                if prev_perf is not None:
                    improvement = ((prev_perf - current_perf) / prev_perf) * 100
                    print_info(f"Improvement vs previous: {improvement:.1f}%")

                    if improvement < PERF_PLATEAU_THRESHOLD:
                        print_ok(f"Performance plateau reached at {current_ram}GB")
                        break

                prev_perf = current_perf

                # Move to next RAM level
                try:
                    next_idx = RAM_LEVELS.index(current_ram) + 1
                    current_ram = RAM_LEVELS[next_idx]
                except (ValueError, IndexError):
                    print_info("Max RAM level reached")
                    break

            except Exception as e:
                if "OOM" in str(e) or "out of memory" in str(e).lower():
                    print_warn(f"OOM at {current_ram}GB")
                    ram_results.append({
                        "ram_gb": current_ram,
                        "status": "oom"
                    })
                    # Escalate
                    try:
                        next_idx = RAM_LEVELS.index(current_ram) + 1
                        current_ram = RAM_LEVELS[next_idx]
                    except (ValueError, IndexError):
                        print_err("Max RAM reached after OOM")
                        break
                else:
                    ram_results.append({
                        "ram_gb": current_ram,
                        "status": f"error: {e}"
                    })
                    print_err(str(e))
                    break
            finally:
                stop_all_containers()

        results[scenario] = {
            "ram_tests": ram_results,
            "optimal_ram": ram_results[-1]["ram_gb"] if ram_results and ram_results[-1].get("status") == "completed" else None
        }

    # Save results
    with open(results_dir / "summary.json", 'w') as f:
        json.dump({
            "dataset": dataset,
            "source_dataset": source_dataset,
            "scale": scale,
            "scenarios": results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)

    # Build summary table
    print_header("RESULTS SUMMARY TABLE")

    # Main table header
    print(f"\n{BOLD}RAM Gradient Results:{RESET}")
    header = (
        f"{'Scenario':<8} | {'Status':<6} | {'RAM Min':<8} | {'RAM Opt':<8} | "
        f"{'Load(s)':<8} | {'p50(s)':<8} | {'p95(s)':<8} | {'Queries':<8} | {'OOM':<10}"
    )
    separator = "-" * len(header)

    print(separator)
    print(header)
    print(separator)

    # Table rows
    for s, r in results.items():
        if isinstance(r, dict) and "ram_tests" in r:
            tests = r["ram_tests"]
            completed = [t for t in tests if t.get("status") == "completed"]
            oom_tests = [t for t in tests if t.get("status") == "oom"]

            if completed:
                status = f"{GREEN}OK{RESET}    "
                ram_min = f"{min(t['ram_gb'] for t in completed)}GB"
                ram_opt = f"{r.get('optimal_ram', '?')}GB"
                # Get best run metrics
                best_run = min(completed, key=lambda t: t.get('p95_latency', 999))
                p95_best = f"{best_run.get('p95_latency', 0):.2f}"
                p50_best = f"{best_run.get('p50_latency', 0):.2f}"
                load_time = f"{best_run.get('load_time', 0):.1f}"
                # Count queries
                query_stats = best_run.get('query_stats', {})
                num_queries = len(query_stats)
            else:
                status = f"{RED}FAIL{RESET}  "
                ram_min = "-"
                ram_opt = "-"
                p95_best = "-"
                p50_best = "-"
                load_time = "-"
                num_queries = 0

            oom_str = ", ".join(f"{t['ram_gb']}" for t in oom_tests) if oom_tests else "-"

            print(
                f"{s:<8} | {status} | {ram_min:<8} | {ram_opt:<8} | "
                f"{load_time:<8} | {p50_best:<8} | {p95_best:<8} | {num_queries:<8} | {oom_str:<10}"
            )
        else:
            status = f"{RED}ERR{RESET}   "
            err_msg = str(r)[:10] if r else "-"
            print(
                f"{s:<8} | {status} | {'-':<8} | {'-':<8} | "
                f"{'-':<8} | {'-':<8} | {'-':<8} | {'-':<8} | {err_msg:<10}"
            )

    print(separator)

    # Query breakdown table (for completed scenarios)
    completed_scenarios = {s: r for s, r in results.items()
                          if isinstance(r, dict) and r.get("ram_tests")
                          and any(t.get("status") == "completed" for t in r["ram_tests"])}

    if completed_scenarios:
        print(f"\n{BOLD}Query Performance (best RAM level, ms):{RESET}")

        # Collect all query IDs
        all_queries = set()
        for s, r in completed_scenarios.items():
            best_run = next((t for t in r["ram_tests"] if t.get("status") == "completed"), None)
            if best_run and best_run.get("query_stats"):
                all_queries.update(best_run["query_stats"].keys())

        all_queries = sorted(all_queries)

        if all_queries:
            # Header
            q_header = f"{'Scenario':<8} |" + "".join(f" {q:<8} |" for q in all_queries)
            q_sep = "-" * len(q_header)
            print(q_sep)
            print(q_header)
            print(q_sep)

            # Rows
            for s, r in completed_scenarios.items():
                best_run = min(
                    [t for t in r["ram_tests"] if t.get("status") == "completed"],
                    key=lambda t: t.get('p95_latency', 999)
                )
                query_stats = best_run.get("query_stats", {})

                row = f"{s:<8} |"
                for q in all_queries:
                    if q in query_stats:
                        p95 = query_stats[q].get("p95", 0)
                        row += f" {p95:<8.1f} |"
                    else:
                        row += f" {'N/A':<8} |"
                print(row)

            print(q_sep)

    # Summary stats
    print(f"\n{BOLD}Summary:{RESET}")
    total = len(results)
    ok_count = sum(1 for r in results.values() if isinstance(r, dict) and r.get("optimal_ram"))
    oom_count = sum(1 for r in results.values() if isinstance(r, dict) and any(t.get("status") == "oom" for t in r.get("ram_tests", [])))
    fail_count = total - ok_count

    print(f"  Total scenarios:    {total}")
    print(f"  Completed:          {ok_count} ({ok_count * 100 // total if total else 0}%)")
    if oom_count:
        print(f"  Had OOM:            {oom_count}")
    if fail_count:
        print(f"  Failed:             {fail_count}")

    # Best performers
    if ok_count > 0:
        best_ram = None
        best_perf = None
        fastest_load = None

        for s, r in results.items():
            if isinstance(r, dict) and r.get("optimal_ram"):
                opt_ram = r["optimal_ram"]
                tests = r.get("ram_tests", [])
                completed = [t for t in tests if t.get("status") == "completed"]
                if completed:
                    best_run = min(completed, key=lambda t: t.get('p95_latency', 999))
                    best_p95 = best_run.get("p95_latency", 999)
                    load_t = best_run.get("load_time", 999)

                    if best_ram is None or opt_ram < best_ram[1]:
                        best_ram = (s, opt_ram)
                    if best_perf is None or best_p95 < best_perf[1]:
                        best_perf = (s, best_p95)
                    if fastest_load is None or load_t < fastest_load[1]:
                        fastest_load = (s, load_t)

        print(f"\n{BOLD}Best performers:{RESET}")
        if best_ram:
            print(f"  Lowest RAM needed:  {best_ram[0]} ({best_ram[1]}GB)")
        if best_perf:
            print(f"  Best p95 latency:   {best_perf[0]} ({best_perf[1]:.2f}s)")
        if fastest_load:
            print(f"  Fastest data load:  {fastest_load[0]} ({fastest_load[1]:.1f}s)")

    print(f"\n{DIM}Results saved to: {results_dir}{RESET}")
    input("\nPress Enter...")


# =============================================================================
# WORKFLOW: PUBLISH
# =============================================================================

def workflow_publish():
    """Publish results to HuggingFace."""
    print_header("PUBLISH TO HUGGINGFACE")

    results_dir = Path("benchmark_results")
    if not results_dir.exists():
        print_warn("No results found. Run a benchmark first.")
        input("\nPress Enter...")
        return

    dirs = sorted([d for d in results_dir.iterdir() if d.is_dir()], reverse=True)
    if not dirs:
        print_warn("No result directories found.")
        input("\nPress Enter...")
        return

    print("Available results:\n")
    for i, d in enumerate(dirs[:5], 1):
        # Try to read summary
        summary_file = d / "summary.json"
        info = ""
        if summary_file.exists():
            try:
                with open(summary_file) as f:
                    summary = json.load(f)
                    info = f" - {summary.get('dataset', '?')}"
            except:
                pass
        print(f"  {i}. {d.name}{info}")
    print(f"\n  0. Back")

    choice = prompt("\nSelect results", "1")
    if choice == "0":
        return

    try:
        selected = dirs[int(choice) - 1]
    except (ValueError, IndexError):
        print_err("Invalid choice")
        return

    print_header("HUGGINGFACE TOKEN")
    print("Get your token at: https://huggingface.co/settings/tokens")
    print("Required permission: Write\n")
    print(f"{DIM}The token will not be stored.{RESET}\n")

    token = getpass.getpass("Token (hidden): ")
    if not token:
        print_err("Token required")
        return

    repo = prompt("Repository", "synaptikad/basetype-benchmark-results")

    if not prompt_yes_no(f"\nPublish to {repo}?"):
        return

    try:
        from huggingface_hub import HfApi
        api = HfApi(token=token)
        api.upload_folder(folder_path=str(selected), repo_id=repo, repo_type="dataset")
        print_ok(f"Published to https://huggingface.co/datasets/{repo}")
    except ImportError:
        print_err("Install huggingface_hub: pip install huggingface_hub")
    except Exception as e:
        print_err(f"Failed: {e}")

    input("\nPress Enter...")


# =============================================================================
# MAIN MENU
# =============================================================================

def get_export_size_info() -> Tuple[int, float]:
    """Get number of exported datasets and total size in MB."""
    export_dir = Path("src/basetype_benchmark/dataset/exports")
    if not export_dir.exists():
        return 0, 0.0

    count = 0
    total_size = 0.0

    for subdir in export_dir.iterdir():
        if subdir.is_dir() and any(subdir.glob("*.csv")):
            count += 1
            total_size += sum(f.stat().st_size for f in subdir.rglob('*') if f.is_file()) / (1024 * 1024)

    return count, total_size


def workflow_purge():
    """Dataset purge workflow with double confirmation."""
    print_header("PURGE DATASETS")

    export_dir = Path("src/basetype_benchmark/dataset/exports")

    # List exported datasets (directories with CSV files)
    dataset_items = []

    if export_dir.exists():
        for subdir in export_dir.iterdir():
            if subdir.is_dir() and any(subdir.glob("*.csv")):
                size_mb = sum(f.stat().st_size for f in subdir.rglob('*') if f.is_file()) / (1024 * 1024)
                dataset_items.append({
                    'path': subdir,
                    'name': subdir.name,
                    'size_mb': size_mb,
                })

    dataset_items = sorted(dataset_items, key=lambda x: x['name'])

    if not dataset_items:
        print_info("No datasets found.")
        input("\nPress Enter...")
        return

    print(f"{RED}{BOLD}WARNING: This will permanently delete dataset files!{RESET}\n")
    print(f"Exported datasets ({len(dataset_items)}):\n")

    total_size = 0.0
    for i, item in enumerate(dataset_items, 1):
        total_size += item['size_mb']
        print(f"  {i}. {item['name']}: {item['size_mb']:.1f} MB")

    print(f"\n  {BOLD}Total: {total_size:.1f} MB{RESET}")

    print(f"\n  Options:")
    print(f"    A. Delete ALL datasets")
    print(f"    S. Select specific dataset to delete")
    print(f"    0. Cancel\n")

    choice = prompt("Select", "0").upper()

    if choice == "0":
        return

    if choice == "A":
        # Double confirmation for delete all
        print(f"\n{RED}{BOLD}FIRST CONFIRMATION{RESET}")
        print(f"You are about to delete {len(dataset_items)} datasets ({total_size:.1f} MB)")

        if not prompt_yes_no("Are you sure you want to delete ALL datasets?", False):
            print("Cancelled.")
            input("\nPress Enter...")
            return

        print(f"\n{RED}{BOLD}SECOND CONFIRMATION{RESET}")
        print("This action cannot be undone. The datasets will need to be regenerated.")
        confirm_text = prompt("Type 'DELETE ALL' to confirm", "")

        if confirm_text != "DELETE ALL":
            print("Confirmation failed. Cancelled.")
            input("\nPress Enter...")
            return

        # Delete all
        print()
        deleted_count = 0
        deleted_size = 0.0

        import shutil as shutil_mod
        for item in dataset_items:
            try:
                shutil_mod.rmtree(item['path'])
                deleted_size += item['size_mb']
                deleted_count += 1
                print(f"  Deleted: {item['name']}")
            except Exception as e:
                print_err(f"Failed to delete {item['name']}: {e}")

        print()
        print_ok(f"Deleted {deleted_count} datasets ({deleted_size:.1f} MB freed)")

    elif choice == "S":
        # Select specific dataset
        print("\nEnter the number of the dataset to delete (or 0 to cancel):")
        idx_str = prompt("Dataset number", "0")

        try:
            idx = int(idx_str)
            if idx == 0:
                return
            if not (1 <= idx <= len(dataset_items)):
                print_err("Invalid selection")
                input("\nPress Enter...")
                return

            selected = dataset_items[idx - 1]
            size_mb = selected['size_mb']

            # Double confirmation for single delete
            print(f"\n{YELLOW}You are about to delete:{RESET}")
            print(f"  {selected['name']} ({size_mb:.1f} MB)")

            if not prompt_yes_no("\nFirst confirmation - Delete this dataset?", False):
                print("Cancelled.")
                input("\nPress Enter...")
                return

            if not prompt_yes_no("Second confirmation - Are you absolutely sure?", False):
                print("Cancelled.")
                input("\nPress Enter...")
                return

            import shutil as shutil_mod
            shutil_mod.rmtree(selected['path'])
            print_ok(f"Deleted {selected['name']} ({size_mb:.1f} MB freed)")

        except ValueError:
            print_err("Invalid input")

    input("\nPress Enter...")


def main():
    """Main menu."""
    while True:
        print_header("BASETYPE BENCHMARK")

        # Show available datasets with size
        available = get_available_profiles()
        num_exports, export_size = get_export_size_info()

        if available:
            print(f"{DIM}Available datasets: {', '.join(available)}{RESET}")
            print(f"{DIM}On disk: {num_exports} datasets, {export_size:.1f} MB{RESET}\n")
        else:
            print(f"{DIM}No datasets generated yet.{RESET}\n")

        print(f"  1. {RED}Purge Datasets{RESET}")
        print("  2. Generate Dataset")
        print("  3. Run Benchmark")
        print("  4. Publish Results")
        print("  0. Exit")

        choice = prompt("\nSelect", "2")

        if choice == "1":
            workflow_purge()
        elif choice == "2":
            workflow_dataset()
        elif choice == "3":
            workflow_benchmark()
        elif choice == "4":
            workflow_publish()
        elif choice == "0":
            stop_all_containers()
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()
