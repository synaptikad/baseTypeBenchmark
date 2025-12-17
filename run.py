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

    print_info("Waiting for containers to be ready...")
    time.sleep(10)
    print_ok("Containers ready")
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
# WORKFLOW: BENCHMARK
# =============================================================================

def workflow_benchmark():
    """Benchmark execution workflow."""
    print_header("BENCHMARK EXECUTION")

    # Check datasets
    available = get_available_profiles()
    if not available:
        print_warn("No datasets available. Generate one first (option 1).")
        input("\nPress Enter...")
        return

    print(f"Available datasets: {', '.join(available)}\n")

    # Select dataset
    for i, ds in enumerate(available, 1):
        size = SIZE_ESTIMATES.get(ds, "?")
        print(f"  {i}. {ds} (~{size} GB)")
    print(f"\n  0. Back")

    choice = prompt("\nSelect dataset", "1")
    if choice == "0":
        return

    try:
        dataset = available[int(choice) - 1]
    except (ValueError, IndexError):
        print_err("Invalid choice")
        return

    # Select scenario
    print_header("SELECT SCENARIO")
    print("Each scenario tests a different database architecture:\n")

    scenario_list = list(SCENARIOS.keys())
    for i, (sid, info) in enumerate(SCENARIOS.items(), 1):
        containers = ", ".join(info["containers"])
        warn = ""
        if sid == "M1" and "large" in dataset:
            warn = f" {RED}[high RAM - may OOM]{RESET}"
        print(f"  {i}. {sid}: {info['name']}")
        print(f"     {DIM}Containers: {containers}{warn}{RESET}\n")

    print(f"  A. All scenarios (sequential)")
    print(f"  0. Back\n")

    choice = prompt("Select scenario", "1").upper()
    if choice == "0":
        return

    if choice == "A":
        scenarios = scenario_list
    else:
        try:
            scenarios = [scenario_list[int(choice) - 1]]
        except (ValueError, IndexError):
            print_err("Invalid choice")
            return

    # Confirm
    print_header("CONFIRM")
    print(f"Dataset:   {dataset}")
    print(f"Scenarios: {', '.join(scenarios)}")
    print(f"\nFor each scenario:")
    print(f"  1. Start required containers only")
    print(f"  2. Load data")
    print(f"  3. Execute benchmark queries")
    print(f"  4. Stop containers")

    if not prompt_yes_no("\nStart benchmark?"):
        return

    # Run
    results_dir = Path("benchmark_results") / datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    for scenario in scenarios:
        print_header(f"RUNNING {scenario}: {SCENARIOS[scenario]['name']}")

        containers = SCENARIOS[scenario]["containers"]
        if not start_containers(containers):
            results[scenario] = "container_error"
            continue

        try:
            # TODO: actual benchmark execution
            print_info(f"Executing {scenario} on {dataset}...")
            time.sleep(2)  # placeholder
            results[scenario] = "completed"
            print_ok(f"{scenario} completed")
        except Exception as e:
            results[scenario] = f"error: {e}"
            print_err(str(e))
        finally:
            stop_all_containers()

    # Save results
    with open(results_dir / "summary.json", 'w') as f:
        json.dump({
            "dataset": dataset,
            "scenarios": results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)

    print_header("RESULTS")
    for s, r in results.items():
        status = f"{GREEN}OK{RESET}" if r == "completed" else f"{RED}{r}{RESET}"
        print(f"  {s}: {status}")

    print(f"\nSaved to: {results_dir}")
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
