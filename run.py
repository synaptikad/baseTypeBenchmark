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


# Detect if we're on Linux for extended monitoring
IS_LINUX = sys.platform.startswith('linux')
CYAN = "\033[96m"


# ============================================================================
# CONSTANTS
# ============================================================================

# Batch sizes for data loading (tuned for performance)
BATCH_SIZES = {
    "postgres_nodes": 1000,
    "postgres_edges": 1000,
    "memgraph_nodes": 5000,
    "memgraph_edges": 1000,
    "memgraph_chunks": 2000,
}

# Docker container names
CONTAINERS = {
    "postgres": "btb_timescaledb",
    "memgraph": "btb_memgraph",
    "oxigraph": "btb_oxigraph",
    "timescaledb": "btb_timescaledb",  # Alias for hybrid scenarios
}


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


def _report_load_progress(label: str, count: int, start_time: float, final: bool = False):
    """Report loading progress with rate calculation.

    Args:
        label: What is being loaded (e.g., "nodes", "edges")
        count: Number of items processed
        start_time: time.time() when loading started
        final: If True, print final summary on new line
    """
    elapsed = time.time() - start_time
    rate = count / elapsed if elapsed > 0 else 0
    if final:
        print(f"\r      Loaded {count:,} {label} in {elapsed:.1f}s ({rate:.0f}/s)          ")
    else:
        print(f"\r      Loading {label}: {count:,} ({rate:.0f}/s)...", end="", flush=True)


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


def get_docker_compose_cmd() -> str:
    """Detect available docker compose command."""
    # Try new syntax first (docker compose)
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return "docker compose"
    except:
        pass

    # Fall back to old syntax (docker-compose)
    try:
        result = subprocess.run(
            ["docker-compose", "version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return "docker-compose"
    except:
        pass

    # Default to new syntax (will fail with clear error)
    return "docker compose"


# Detect docker compose command at startup
DOCKER_COMPOSE_CMD = get_docker_compose_cmd()


# =============================================================================
# CONFIGURATION
# =============================================================================

SCENARIOS = {
    # Order optimized: P1/P2 (pure SQL), then M2/O2 (hybrid with TimescaleDB), then M1/O1 (full-graph)
    "P1": {"name": "PostgreSQL Relational", "containers": ["timescaledb"]},
    "P2": {"name": "PostgreSQL JSONB", "containers": ["timescaledb"]},
    "M2": {"name": "Memgraph + TimescaleDB", "containers": ["memgraph", "timescaledb"]},
    "O2": {"name": "Oxigraph + TimescaleDB", "containers": ["oxigraph", "timescaledb"]},
    "M1": {"name": "Memgraph + Chunks", "containers": ["memgraph"]},  # Timeseries as array nodes
    "O1": {"name": "Oxigraph + Chunks", "containers": ["oxigraph"]},  # Timeseries as RDF chunks
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
    run_cmd(f"{DOCKER_COMPOSE_CMD} down", cwd=str(DOCKER_DIR))


def start_containers(containers: List[str]) -> bool:
    """Start specific containers."""
    stop_all_containers()
    print_info(f"Starting: {', '.join(containers)}")

    if not run_cmd(f"{DOCKER_COMPOSE_CMD} up -d {' '.join(containers)}", cwd=str(DOCKER_DIR)):
        print_err("Failed to start containers")
        return False

    # Wait longer for containers to be ready (Memgraph needs more time)
    wait_time = 5
    print_info(f"Waiting {wait_time}s for containers to initialize...")
    time.sleep(wait_time)
    print_ok("Containers started (connection retry handled by loaders)")
    return True


def check_dataset(profile: str, seed: int = 42) -> bool:
    """Check if dataset has been exported to disk (V2 format)."""
    export_dir = Path("src/basetype_benchmark/dataset/exports") / f"{profile}_seed{seed}"
    # Prefer fingerprint.json (written at the end), but accept partial exports too
    # so interrupted generations still show up in purge/UI.
    parquet_dir = export_dir / "parquet"
    return (
        (export_dir / "fingerprint.json").exists()
        or (parquet_dir / "timeseries.parquet").exists()
        or (parquet_dir / "nodes.parquet").exists()
    )


def _is_export_dir(subdir: Path) -> bool:
    """Return True if subdir looks like a V2 export directory.

    We consider a dataset "present" if either:
    - fingerprint.json exists (complete export)
    - or Parquet pivot exists (partial export, e.g. interrupted before fingerprint)
    """
    if not subdir.is_dir():
        return False
    if (subdir / "fingerprint.json").exists():
        return True
    parquet_dir = subdir / "parquet"
    return (
        (parquet_dir / "timeseries.parquet").exists()
        or (parquet_dir / "nodes.parquet").exists()
    )


def get_available_profiles() -> List[str]:
    """Get list of profiles that have datasets exported on disk."""
    available = []
    export_dir = Path("src/basetype_benchmark/dataset/exports")
    if export_dir.exists():
        for subdir in export_dir.iterdir():
            if _is_export_dir(subdir):
                # Extract profile name from directory name (e.g., "small-1w_seed42" -> "small-1w")
                name = subdir.name.rsplit("_seed", 1)[0]
                if name not in available:
                    available.append(name)
    return sorted(available)


def get_scenario_files(export_dir: Path, scenario: str) -> dict:
    """Get file paths for a specific scenario from V2 export structure.

    V2 export structure:
        exports/{profile}_seed{seed}/
        ├── parquet/          # Pivot format
        ├── p1/               # PostgreSQL relational
        ├── p2/               # PostgreSQL JSONB
        ├── m1/               # Memgraph chunks
        ├── m2/               # Memgraph + TimescaleDB
        ├── o1/               # Oxigraph chunks
        ├── o2/               # Oxigraph + TimescaleDB
        └── fingerprint.json

    Args:
        export_dir: Base export directory (e.g., exports/small-1w_seed42)
        scenario: Scenario code (P1, P2, M1, M2, O1, O2)

    Returns:
        Dict with file paths for nodes, edges, timeseries, etc.
    """
    scenario_lower = scenario.lower()
    scenario_dir = export_dir / scenario_lower

    # V2 structure required - no fallback to V1
    if not scenario_dir.exists():
        available_dirs = [d.name for d in export_dir.iterdir() if d.is_dir()]
        raise FileNotFoundError(
            f"Scenario directory not found: {scenario_dir}\n"
            f"Available directories: {available_dirs}\n"
            f"Dataset may need regeneration with V2 generator.\n"
            f"Run: 1. Purge Datasets -> 2. Generate Dataset"
        )

    # V2 structure by scenario
    if scenario in ("P1",):
        return {
            "nodes": scenario_dir / "pg_nodes.csv",
            "edges": scenario_dir / "pg_edges.csv",
            "timeseries": scenario_dir / "pg_timeseries.csv",
        }
    elif scenario in ("P2",):
        return {
            "nodes": scenario_dir / "pg_jsonb_nodes.csv",
            "edges": scenario_dir / "pg_jsonb_edges.csv",
            "timeseries": scenario_dir / "pg_timeseries.csv",
        }
    elif scenario in ("M1",):
        return {
            "nodes": scenario_dir / "mg_nodes.csv",
            "edges": scenario_dir / "mg_edges.csv",
            "chunks": scenario_dir / "mg_chunks.csv",
        }
    elif scenario in ("M2",):
        return {
            "nodes": scenario_dir / "mg_nodes.csv",
            "edges": scenario_dir / "mg_edges.csv",
            "timeseries": scenario_dir / "timeseries.csv",
        }
    elif scenario in ("O1",):
        return {
            "graph": scenario_dir / "graph.nt",
            "chunks": scenario_dir / "chunks.nt",
            "aggregates": scenario_dir / "aggregates.nt",
        }
    elif scenario in ("O2",):
        return {
            "graph": scenario_dir / "graph.nt",
            "timeseries": scenario_dir / "timeseries.csv",
        }
    else:
        raise ValueError(f"Unknown scenario: {scenario}")


# =============================================================================
# WORKFLOW: DATASET
# =============================================================================

def workflow_dataset():
    """Dataset generation workflow.

    Flow:
    1. Choose source: HuggingFace (default) or local generation
    2. If HuggingFace: list available datasets -> choose -> import
    3. If local generation: choose scale -> duration -> seed -> generate
    """
    print_header("DATASET GENERATION")

    # Step 1: Choose source
    print(f"{BOLD}Step 1: Choose data source{RESET}\n")
    print(f"  1. {BOLD}HuggingFace Hub{RESET} (recommended for reproducibility)")
    print(f"     {DIM}Download pre-generated dataset with verified fingerprint{RESET}\n")
    print(f"  2. {BOLD}Generate locally{RESET}")
    print(f"     {DIM}Generate dataset using deterministic seed (slower){RESET}\n")
    print(f"  0. Back\n")

    source_choice = prompt("Select source", "1")
    if source_choice == "0":
        return

    use_huggingface = source_choice == "1"

    if use_huggingface:
        # HuggingFace flow: list available -> choose -> import
        _workflow_dataset_huggingface()
    else:
        # Local generation flow: scale -> duration -> seed -> generate
        _workflow_dataset_generate()

    input("\nPress Enter...")


def _workflow_dataset_huggingface():
    """HuggingFace import sub-workflow."""
    print_header("HUGGINGFACE IMPORT")

    # Try to list available datasets
    try:
        from huggingface_hub import list_repo_files
    except ImportError:
        print_err("huggingface_hub not installed")
        print_info("Install with: pip install huggingface_hub")
        print_info("Or use local generation instead (option 2)")
        return

    print_info(f"Checking HuggingFace repository: {HF_DATASET_REPO}")

    try:
        files = list_repo_files(HF_DATASET_REPO, repo_type="dataset")
        # Filter for dataset files (*.pkl.gz pattern)
        dataset_files = [f for f in files if f.endswith("_seed42.pkl.gz")]

        if not dataset_files:
            print_warn("No datasets available on HuggingFace yet")
            print_info("Use local generation instead (option 2)")
            return

        # Parse available profiles
        available_profiles = []
        for f in dataset_files:
            # Extract profile from filename like "small-1w_seed42.pkl.gz"
            profile = f.replace("_seed42.pkl.gz", "")
            available_profiles.append(profile)

        print(f"\n{BOLD}Available datasets on HuggingFace:{RESET}\n")
        for i, profile in enumerate(available_profiles, 1):
            size = SIZE_ESTIMATES.get(profile, "?")
            status = f"{GREEN}[already downloaded]{RESET}" if check_dataset(profile) else ""
            print(f"  {i}. {profile:12} (~{size} GB)  {status}")

        print(f"\n  0. Back (use local generation)\n")

        choice = prompt("Select dataset", "1")
        if choice == "0":
            return

        try:
            idx = int(choice) - 1
            if not (0 <= idx < len(available_profiles)):
                raise ValueError()
            profile = available_profiles[idx]
        except ValueError:
            print_err("Invalid choice")
            return

        # Confirm and download
        if check_dataset(profile):
            print(f"\n{YELLOW}Dataset already exists locally.{RESET}")
            if not prompt_yes_no("Re-download and overwrite?", False):
                return

        seed = 42  # HuggingFace datasets use seed=42
        print_header(f"DOWNLOADING {profile} FROM HUGGINGFACE")
        download_from_huggingface(profile, seed)

    except Exception as e:
        print_err(f"Failed to access HuggingFace: {e}")
        print_info("Use local generation instead (option 2)")


def _workflow_dataset_generate():
    """Local generation sub-workflow."""
    print_header("LOCAL GENERATION")

    # Step 2a: Choose scale
    print(f"{BOLD}Step 2a: Choose graph scale{RESET}\n")
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

    # Step 2b: Choose duration
    print_header("TIMESERIES DURATION")
    print(f"{BOLD}Step 2b: Choose timeseries duration{RESET}\n")
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

    seed = prompt("\nSeed (for reproducibility)", "42")

    # Simulation mode: vectorized is the default and recommended (fastest)
    mode = "vectorized"

    if not prompt_yes_no(f"\nGenerate {profile}?"):
        return

    # Generate
    print_header(f"GENERATING {profile}")
    try:
        from basetype_benchmark.dataset.dataset_manager import DatasetManager

        manager = DatasetManager()
        # Génère via V2 (generator_v2 + exporter_v2) et exporte 6 formats
        export_path, summary, fingerprint = manager.generate_and_export(
            profile,
            int(seed),
            mode=mode,
        )
        print()
        print_ok(f"Dataset ready at: {export_path}")
        print_info(f"Fingerprint: {fingerprint['struct_hash'][:8]}...{fingerprint.get('ts_hash', 'N/A')[:8] if fingerprint.get('ts_hash') else 'N/A'}")

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


# =============================================================================
# RAM CONFIGURATION
# =============================================================================

# RAM levels to test (in GB) - up to 256GB for OVH B3-256
RAM_LEVELS = [4, 8, 16, 32, 64, 128, 256]

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

    # Set environment variable for docker-compose
    import os
    env = os.environ.copy()
    env["MEMORY_LIMIT"] = f"{ram_gb}g"

    try:
        result = subprocess.run(
            f"{DOCKER_COMPOSE_CMD} up -d {' '.join(containers)}",
            shell=True,
            cwd=str(DOCKER_DIR),
            env=env,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_err(f"Failed to start containers: {result.stderr}")
            return False
    except Exception as e:
        print_err(f"Failed to start containers: {e}")
        return False

    # Short wait - actual connection retry is handled by loaders
    wait_time = 5
    print_info(f"Waiting {wait_time}s for containers to initialize...")
    time.sleep(wait_time)
    print_ok(f"Containers started ({ram_gb}GB RAM, connection retry handled by loaders)")
    return True


def get_container_stats(container_name: str) -> Optional[Dict]:
    """Get memory and CPU stats for a container."""
    try:
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format",
             "{{.MemUsage}},{{.MemPerc}},{{.CPUPerc}}",
             container_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return None

        parts = result.stdout.strip().split(",")
        if len(parts) < 3:
            return None

        # Parse memory: "1.5GiB / 8GiB" -> extract used
        mem_str = parts[0].split("/")[0].strip()
        mem_mb = 0
        if "GiB" in mem_str:
            mem_mb = float(mem_str.replace("GiB", "").strip()) * 1024
        elif "MiB" in mem_str:
            mem_mb = float(mem_str.replace("MiB", "").strip())
        elif "KiB" in mem_str:
            mem_mb = float(mem_str.replace("KiB", "").strip()) / 1024

        # Parse CPU: "25.5%" -> 25.5
        cpu_pct = float(parts[2].replace("%", "").strip())

        return {"mem_mb": mem_mb, "cpu_pct": cpu_pct}
    except Exception:
        return None


def get_container_cgroup_path(container_name: str) -> Optional[str]:
    """Get the cgroup v2 path for a container (Linux only)."""
    if not IS_LINUX:
        return None
    try:
        # Get container full ID
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.Id}}", container_name],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return None
        container_id = result.stdout.strip()

        # Try systemd driver path first (most common on Ubuntu)
        systemd_path = f"/sys/fs/cgroup/system.slice/docker-{container_id}.scope"
        if os.path.exists(systemd_path):
            return systemd_path

        # Try cgroupfs driver path
        cgroupfs_path = f"/sys/fs/cgroup/docker/{container_id}"
        if os.path.exists(cgroupfs_path):
            return cgroupfs_path

        return None
    except Exception:
        return None


def get_cgroup_metrics(cgroup_path: str) -> Optional[Dict]:
    """Read cgroup v2 metrics from filesystem.

    Returns:
        Dict with:
        - memory_bytes: current memory usage (bytes)
        - memory_peak_bytes: peak memory since container start (bytes)
        - cpu_usage_usec: total CPU time consumed (microseconds)
        - cpu_user_usec: user-space CPU time (microseconds)
        - cpu_system_usec: kernel-space CPU time (microseconds)
    """
    if not cgroup_path or not os.path.exists(cgroup_path):
        return None

    metrics = {}
    try:
        # Memory current
        mem_current = Path(cgroup_path) / "memory.current"
        if mem_current.exists():
            metrics["memory_bytes"] = int(mem_current.read_text().strip())

        # Memory peak
        mem_peak = Path(cgroup_path) / "memory.peak"
        if mem_peak.exists():
            metrics["memory_peak_bytes"] = int(mem_peak.read_text().strip())

        # CPU stats
        cpu_stat = Path(cgroup_path) / "cpu.stat"
        if cpu_stat.exists():
            for line in cpu_stat.read_text().strip().split("\n"):
                parts = line.split()
                if len(parts) == 2:
                    key, value = parts
                    if key == "usage_usec":
                        metrics["cpu_usage_usec"] = int(value)
                    elif key == "user_usec":
                        metrics["cpu_user_usec"] = int(value)
                    elif key == "system_usec":
                        metrics["cpu_system_usec"] = int(value)

        return metrics if metrics else None
    except Exception:
        return None


def reset_memory_peak(cgroup_path: str) -> bool:
    """Reset memory.peak counter to current value (Linux only)."""
    if not cgroup_path:
        return False
    try:
        mem_peak = Path(cgroup_path) / "memory.peak"
        if mem_peak.exists():
            try:
                mem_peak.write_text("0")
                return True
            except PermissionError:
                # Often requires root to write under /sys/fs/cgroup. If the user
                # has passwordless sudo (typical on cloud images), try a
                # non-interactive sudo write.
                try:
                    if not str(mem_peak).startswith("/sys/fs/cgroup/"):
                        return False

                    r = subprocess.run(
                        ["sudo", "-n", "tee", str(mem_peak)],
                        input="0",
                        text=True,
                        capture_output=True,
                    )
                    return r.returncode == 0
                except Exception:
                    return False
    except Exception:
        return False
    return False


class CGroupMetricsSnapshot:
    """Snapshot of cgroup metrics for delta calculations."""

    def __init__(self, container_name: str):
        self.container_name = container_name
        self.cgroup_path = get_container_cgroup_path(container_name)
        self.timestamp = time.time()
        self.metrics = get_cgroup_metrics(self.cgroup_path) if self.cgroup_path else None

        # Fallback to docker stats if cgroup not available
        if not self.metrics:
            stats = get_container_stats(container_name)
            if stats:
                self.metrics = {
                    "memory_bytes": int(stats["mem_mb"] * 1024 * 1024),
                    "cpu_usage_usec": 0,  # Not available via docker stats
                }

    def memory_mb(self) -> float:
        """Current memory in MB."""
        if self.metrics and "memory_bytes" in self.metrics:
            return self.metrics["memory_bytes"] / (1024 * 1024)
        return 0.0

    def memory_peak_mb(self) -> float:
        """Peak memory in MB (since last reset)."""
        if self.metrics and "memory_peak_bytes" in self.metrics:
            return self.metrics["memory_peak_bytes"] / (1024 * 1024)
        return self.memory_mb()

    def cpu_time_sec(self) -> float:
        """Total CPU time in seconds."""
        if self.metrics and "cpu_usage_usec" in self.metrics:
            return self.metrics["cpu_usage_usec"] / 1_000_000
        return 0.0

    @staticmethod
    def compute_delta(before: 'CGroupMetricsSnapshot', after: 'CGroupMetricsSnapshot', num_cpus: int = 1) -> Dict:
        """Compute resource usage between two snapshots.

        Returns:
            Dict with:
            - memory_before_mb: RAM at start
            - memory_after_mb: RAM at end
            - memory_delta_mb: RAM growth (can be negative)
            - memory_peak_mb: Peak RAM during interval (if available)
            - cpu_time_sec: CPU time consumed during interval
            - cpu_percent: CPU utilization as percentage (0-100 per core)
            - wall_time_sec: Elapsed wall-clock time
        """
        wall_time = after.timestamp - before.timestamp

        result = {
            "memory_before_mb": before.memory_mb(),
            "memory_after_mb": after.memory_mb(),
            "memory_delta_mb": after.memory_mb() - before.memory_mb(),
            "memory_peak_mb": after.memory_peak_mb(),
            "wall_time_sec": wall_time,
        }

        # CPU delta
        cpu_before = before.cpu_time_sec()
        cpu_after = after.cpu_time_sec()
        cpu_time = cpu_after - cpu_before
        result["cpu_time_sec"] = cpu_time

        # CPU percentage: (cpu_time / wall_time) * 100
        # For multi-core, this can exceed 100%
        if wall_time > 0:
            result["cpu_percent"] = (cpu_time / wall_time) * 100
        else:
            result["cpu_percent"] = 0.0

        return result


def check_container_oom(container_name: str) -> bool:
    """Check if container was killed by OOM."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.OOMKilled}}", container_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip().lower() == "true"
    except Exception:
        return False


def get_container_logs(container_name: str, tail: int = 50) -> str:
    """Get last N lines of container logs."""
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(tail), container_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Failed to get logs: {e}"


def dump_container_debug(container_name: str):
    """Dump container debug info (logs, stats, state)."""
    print(f"\n{YELLOW}=== DEBUG INFO: {container_name} ==={RESET}")

    # State
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format",
             "Status: {{.State.Status}}, OOMKilled: {{.State.OOMKilled}}, ExitCode: {{.State.ExitCode}}",
             container_name],
            capture_output=True, text=True, timeout=10
        )
        print(f"State: {result.stdout.strip()}")
    except Exception as e:
        print(f"State: Error - {e}")

    # Stats
    stats = get_container_stats(container_name)
    if stats:
        print(f"Memory: {stats['mem_mb']:.1f} MB, CPU: {stats['cpu_pct']:.1f}%")

    # Logs
    print(f"\n--- Last 30 lines of logs ---")
    logs = get_container_logs(container_name, tail=30)
    print(logs)
    print(f"--- End logs ---\n")


def drop_caches() -> bool:
    """Drop system caches (requires root on Linux)."""
    try:
        # This only works on Linux with root privileges
        result = subprocess.run(
            ["sudo", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def get_container_io_stats(container_name: str) -> Optional[Dict]:
    """Get I/O stats for a container using docker stats."""
    try:
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format",
             "{{.BlockIO}},{{.NetIO}}",
             container_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return None

        parts = result.stdout.strip().split(",")
        if len(parts) < 2:
            return None

        # Parse BlockIO: "1.5GB / 500MB" -> read/write bytes
        block_io = parts[0].strip()
        net_io = parts[1].strip()

        def parse_size(s: str) -> float:
            """Parse size string to MB."""
            s = s.strip()
            if "GB" in s or "GiB" in s:
                return float(s.replace("GB", "").replace("GiB", "").strip()) * 1024
            elif "MB" in s or "MiB" in s:
                return float(s.replace("MB", "").replace("MiB", "").strip())
            elif "KB" in s or "KiB" in s or "kB" in s:
                return float(s.replace("KB", "").replace("KiB", "").replace("kB", "").strip()) / 1024
            elif "B" in s:
                return float(s.replace("B", "").strip()) / (1024 * 1024)
            return 0

        # BlockIO format: "read / write"
        block_parts = block_io.split("/")
        block_read_mb = parse_size(block_parts[0]) if len(block_parts) > 0 else 0
        block_write_mb = parse_size(block_parts[1]) if len(block_parts) > 1 else 0

        # NetIO format: "rx / tx"
        net_parts = net_io.split("/")
        net_rx_mb = parse_size(net_parts[0]) if len(net_parts) > 0 else 0
        net_tx_mb = parse_size(net_parts[1]) if len(net_parts) > 1 else 0

        return {
            "block_read_mb": block_read_mb,
            "block_write_mb": block_write_mb,
            "net_rx_mb": net_rx_mb,
            "net_tx_mb": net_tx_mb
        }
    except Exception:
        return None


class ResourceMonitor:
    """Background resource monitor for containers."""

    def __init__(self, container_name: str, interval_s: float = 0.5):
        self.container_name = container_name
        self.interval_s = interval_s
        self.samples: List[Dict] = []
        self._stop_event = None
        self._thread = None
        self._start_time = 0

    def _sample_loop(self):
        """Sampling loop running in background thread."""
        import threading
        while not self._stop_event.is_set():
            sample = {"timestamp": time.time() - self._start_time}

            # CPU/Memory
            stats = get_container_stats(self.container_name)
            if stats:
                sample.update(stats)

            # I/O
            io_stats = get_container_io_stats(self.container_name)
            if io_stats:
                sample.update(io_stats)

            self.samples.append(sample)
            time.sleep(self.interval_s)

    def start(self):
        """Start background monitoring."""
        import threading
        self.samples = []
        self._start_time = time.time()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def stop(self) -> Dict:
        """Stop monitoring and return aggregated metrics."""
        if self._stop_event:
            self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

        return self._aggregate()

    def _aggregate(self) -> Dict:
        """Aggregate collected samples into metrics."""
        if not self.samples:
            return {
                "sample_count": 0,
                "duration_s": 0,
                "mem_mb": {"min": 0, "max": 0, "avg": 0, "median": 0},
                "cpu_pct": {"min": 0, "max": 0, "avg": 0},
                "io": {"block_read_mb": 0, "block_write_mb": 0, "net_rx_mb": 0, "net_tx_mb": 0}
            }

        # Memory stats
        mem_values = [s.get("mem_mb", 0) for s in self.samples if s.get("mem_mb")]
        cpu_values = [s.get("cpu_pct", 0) for s in self.samples if s.get("cpu_pct") is not None]

        # I/O - get delta between first and last sample
        first_io = next((s for s in self.samples if s.get("block_read_mb") is not None), {})
        last_io = next((s for s in reversed(self.samples) if s.get("block_read_mb") is not None), {})

        io_delta = {
            "block_read_mb": last_io.get("block_read_mb", 0) - first_io.get("block_read_mb", 0),
            "block_write_mb": last_io.get("block_write_mb", 0) - first_io.get("block_write_mb", 0),
            "net_rx_mb": last_io.get("net_rx_mb", 0) - first_io.get("net_rx_mb", 0),
            "net_tx_mb": last_io.get("net_tx_mb", 0) - first_io.get("net_tx_mb", 0),
        }

        duration = self.samples[-1].get("timestamp", 0) if self.samples else 0

        return {
            "sample_count": len(self.samples),
            "duration_s": duration,
            "mem_mb": {
                "min": min(mem_values) if mem_values else 0,
                "max": max(mem_values) if mem_values else 0,
                "avg": sum(mem_values) / len(mem_values) if mem_values else 0,
                "median": sorted(mem_values)[len(mem_values) // 2] if mem_values else 0,
            },
            "cpu_pct": {
                "min": min(cpu_values) if cpu_values else 0,
                "max": max(cpu_values) if cpu_values else 0,
                "avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            },
            "io": io_delta,
            "samples": self.samples  # Keep raw samples for detailed analysis
        }


def collect_resource_samples(container_name: str, duration_s: float, interval_s: float = 1.0) -> Dict:
    """Collect resource samples during query execution (legacy function)."""
    samples = []
    start = time.time()
    while time.time() - start < duration_s:
        stats = get_container_stats(container_name)
        if stats:
            samples.append(stats)
        time.sleep(interval_s)

    if not samples:
        return {"steady_mem_mb": 0, "peak_mem_mb": 0, "avg_cpu_pct": 0}

    mem_values = [s["mem_mb"] for s in samples]
    cpu_values = [s["cpu_pct"] for s in samples]

    return {
        "steady_mem_mb": sorted(mem_values)[len(mem_values) // 2],  # median
        "peak_mem_mb": max(mem_values),
        "avg_cpu_pct": sum(cpu_values) / len(cpu_values)
    }


def is_performance_plateau(prev_p95: float, curr_p95: float, threshold_pct: float = 10.0) -> bool:
    """Check if performance improvement is below threshold (plateau reached)."""
    if prev_p95 <= 0:
        return False
    improvement = (prev_p95 - curr_p95) / prev_p95 * 100
    return improvement < threshold_pct


# =============================================================================
# BENCHMARK EXECUTION ENGINE
# =============================================================================

# Queries by scenario - SYMMETRIC: all 13 queries on all 6 configurations
# Q1-Q5: Graph traversal (native for all)
# Q6-Q7: Timeseries aggregation
#   - P1/P2/M2/O2: time_bucket (TimescaleDB)
#   - M1: UNWIND dechunking (stress-test)
#   - O1: Daily aggregates (pre-computed)
# Q8-Q12: Hybrid graph+TS (all scenarios)
# Q13: DOW filter + dechunking (stress-test M1/O1)
QUERIES_BY_SCENARIO = {
    "P1": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13"],
    "P2": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13"],
    "M1": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13"],  # Q6/Q7 via dechunking
    "M2": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13"],  # Hybrid: graph + TimescaleDB
    "O1": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13"],  # Q6/Q7 via daily aggregates
    "O2": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13"],  # Hybrid: graph + TimescaleDB
}

# Query classification for M2/O2 hybrid execution:
# - GRAPH_ONLY: Q1-Q5 - Pure graph traversal, no timeseries
# - TS_DIRECT: Q6 - Timeseries query with point_id parameter (no graph needed)
# - HYBRID: Q7-Q13 - Graph query returns point_ids, then TimescaleDB aggregation
HYBRID_QUERY_TYPE = {
    "Q1": "graph_only",
    "Q2": "graph_only",
    "Q3": "graph_only",
    "Q4": "graph_only",
    "Q5": "graph_only",
    "Q6": "ts_direct",      # point_id provided as parameter
    "Q7": "hybrid",         # graph: get building points → TS: compute drift
    "Q8": "hybrid",         # graph: tenant → points → TS: energy sum
    "Q9": "hybrid",         # graph: tenant → points → TS: carbon calc
    "Q10": "hybrid",        # graph: zone → access points → TS: events
    "Q11": "hybrid",        # graph: building → IT points → TS: stats
    "Q12": "hybrid",        # graph: building → all points → TS: KPIs
    "Q13": "hybrid",        # graph: space → thermostat points → TS: DOW filter
}

# Benchmark protocol - proportional to profile (realistic workload simulation)
# A large building (campus/hospital) receives more queries than a small one
PROTOCOL_CONFIG = {
    "small": {"n_warmup": 3, "n_runs": 10, "n_variants": 3},
    "medium": {"n_warmup": 3, "n_runs": 30, "n_variants": 5},
    "large": {"n_warmup": 3, "n_runs": 100, "n_variants": 10},
}

# Legacy defaults (used when profile not specified)
N_WARMUP = 3
N_RUNS = 10

QUERIES_DIR = Path(__file__).parent / "queries"

# Query parameters specification
QUERY_PARAMS = {
    "Q1": ["meter_id"],
    "Q2": ["equipment_id"],
    "Q3": ["space_id"],
    "Q4": ["floor_id"],
    "Q5": [],  # Global scan, no params
    "Q6": ["point_id", "date_start", "date_end"],
    "Q7": ["building_id", "date_start", "date_end"],
    "Q8": ["tenant_id", "date_start", "date_end"],
    "Q9": ["tenant_id", "date_start", "date_end"],
    "Q10": ["zone_id", "date_start", "date_end"],
    "Q11": ["building_id"],
    "Q12": ["building_id", "date_start", "date_end"],
    "Q13": ["space_type", "date_start", "date_end"],
}


def get_protocol_config(profile: str) -> Dict:
    """Get protocol configuration for a profile."""
    # Extract scale from profile (e.g., 'small-2d' -> 'small')
    scale = profile.split("-")[0] if "-" in profile else profile
    return PROTOCOL_CONFIG.get(scale, PROTOCOL_CONFIG["small"])


def get_query_variants(query_id: str, profile: str, dataset_info: Dict, seed: int = 42, scenario: str = "P1") -> List[Dict]:
    """Generate parameter variants for a query (deterministic).

    Args:
        query_id: Q1, Q2, etc.
        profile: small-2d, medium-1w, etc.
        dataset_info: Dict with available IDs (meters, floors, tenants, etc.)
        seed: Random seed for reproducibility
        scenario: P1/P2 (SQL), M1/M2 (Cypher), O1/O2 (SPARQL) - affects date format

    Returns:
        List of parameter dicts for each variant
    """
    import random
    rng = random.Random(seed + hash(query_id))

    config = get_protocol_config(profile)
    n_variants = config["n_variants"]
    params = QUERY_PARAMS.get(query_id, [])

    # Determine date format based on scenario
    # P1/P2 (SQL): ISO 8601 for ::timestamptz
    # M1/M2 (Cypher): Unix timestamp (integer)
    # O1/O2 (SPARQL): xsd:date format (YYYY-MM-DD)
    scenario_upper = scenario.upper()
    if scenario_upper in ("P1", "P2"):
        date_format = "iso"  # 2024-01-15T00:00:00+00:00
    elif scenario_upper in ("M1", "M2"):
        date_format = "unix"  # 1705276800
    elif scenario_upper in ("O1", "O2"):
        date_format = "xsd_date"  # 2024-01-15
    else:
        date_format = "iso"  # Default to ISO

    # No params = single empty variant
    if not params:
        return [{}]

    variants = []

    # Generate date ranges (sliding windows)
    ts_end = dataset_info.get("ts_end", int(time.time()))

    for i in range(n_variants):
        variant = {}

        for param in params:
            if param == "meter_id":
                meters = dataset_info.get("meters", ["meter_default"])
                variant[param] = rng.choice(meters) if meters else "meter_default"

            elif param == "equipment_id":
                equipment = dataset_info.get("equipment", ["eq_default"])
                variant[param] = rng.choice(equipment) if equipment else "eq_default"

            elif param == "space_id":
                spaces = dataset_info.get("spaces", ["space_default"])
                variant[param] = rng.choice(spaces) if spaces else "space_default"

            elif param == "floor_id":
                floors = dataset_info.get("floors", ["floor_default"])
                variant[param] = rng.choice(floors) if floors else "floor_default"

            elif param == "building_id":
                buildings = dataset_info.get("buildings", ["bldg_default"])
                variant[param] = rng.choice(buildings) if buildings else "bldg_default"

            elif param == "tenant_id":
                tenants = dataset_info.get("tenants", ["tenant_default"])
                variant[param] = rng.choice(tenants) if tenants else "tenant_default"

            elif param == "zone_id":
                zones = dataset_info.get("zones", ["zone_default"])
                variant[param] = rng.choice(zones) if zones else "zone_default"

            elif param == "point_id":
                points = dataset_info.get("points", ["point_default"])
                variant[param] = rng.choice(points) if points else "point_default"

            elif param == "space_type":
                space_types = ["office_open", "office_closed", "meeting_large", "conference"]
                variant[param] = rng.choice(space_types)

            elif param == "date_start":
                # Sliding window: offset by variant index
                from datetime import datetime, timezone
                window_days = 7 if query_id in ["Q7"] else 1 if query_id in ["Q6", "Q12"] else 30
                offset_days = i * 7  # Each variant shifts by 1 week
                ts = ts_end - (window_days + offset_days) * 86400
                # Format based on scenario
                if date_format == "unix":
                    variant[param] = ts  # Integer for Cypher
                elif date_format == "xsd_date":
                    variant[param] = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                else:  # iso
                    variant[param] = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

            elif param == "date_end":
                from datetime import datetime, timezone
                offset_days = i * 7
                ts = ts_end - offset_days * 86400
                # Format based on scenario
                if date_format == "unix":
                    variant[param] = ts  # Integer for Cypher
                elif date_format == "xsd_date":
                    variant[param] = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                else:  # iso
                    variant[param] = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

        variants.append(variant)

    return variants


def substitute_params(query_text: str, params: Dict) -> str:
    """Substitute $PARAM placeholders in query text.

    Args:
        query_text: Query with $PARAM placeholders
        params: Dict of param_name -> value

    Returns:
        Query with substituted values
    """
    result = query_text
    for key, value in params.items():
        placeholder = f"${key.upper()}"
        if isinstance(value, str):
            # String values: replace placeholder directly (quotes already in query)
            result = result.replace(placeholder, value)
        else:
            result = result.replace(placeholder, str(value))

    # Also handle $CURRENT_TS for Cypher/SPARQL
    if "$CURRENT_TS" in result:
        result = result.replace("$CURRENT_TS", str(int(time.time())))
    if "$CURRENT_DATE" in result:
        from datetime import datetime
        result = result.replace("$CURRENT_DATE", datetime.now().strftime("%Y-%m-%d"))

    return result


def load_query(scenario: str, query_id: str, params: Optional[Dict] = None) -> Optional[str]:
    """Load query text for a scenario, optionally substituting parameters.

    New folder structure:
        queries/
        ├── p1_p2/          # PostgreSQL (SQL) - P1 and P2 use same queries
        ├── m1/             # Memgraph standalone (Cypher with chunks)
        ├── m2/graph/       # Memgraph hybrid - graph part (Cypher)
        ├── o1/             # Oxigraph standalone (SPARQL with chunks)
        └── o2/graph/       # Oxigraph hybrid - graph part (SPARQL)

    Args:
        scenario: P1, P2, M1, M2, O1, O2
        query_id: Q1, Q2, ..., Q13
        params: Optional dict of parameters to substitute

    Returns:
        Query text with parameters substituted, or None if not found
    """
    scenario_upper = scenario.upper()

    if scenario_upper in ("P1", "P2"):
        query_dir = QUERIES_DIR / "p1_p2"
        ext = "sql"
    elif scenario_upper == "M1":
        query_dir = QUERIES_DIR / "m1"
        ext = "cypher"
    elif scenario_upper == "M2":
        query_dir = QUERIES_DIR / "m2" / "graph"
        ext = "cypher"
    elif scenario_upper == "O1":
        query_dir = QUERIES_DIR / "o1"
        ext = "sparql"
    elif scenario_upper == "O2":
        query_dir = QUERIES_DIR / "o2" / "graph"
        ext = "sparql"
    else:
        return None

    # Find query file
    for f in query_dir.glob(f"{query_id}_*.{ext}"):
        query_text = f.read_text(encoding="utf-8")
        if params:
            query_text = substitute_params(query_text, params)
        return query_text
    return None


def load_ts_query(scenario: str, query_id: str, params: Optional[Dict] = None) -> Optional[str]:
    """Load TimescaleDB query for M2/O2 hybrid execution.

    Folder structure:
        queries/
        ├── m2/ts/          # Memgraph hybrid - TimescaleDB part (SQL)
        └── o2/ts/          # Oxigraph hybrid - TimescaleDB part (SQL)

    Args:
        scenario: M2 or O2
        query_id: Q6, Q7, ..., Q13
        params: Optional dict of parameters to substitute

    Returns:
        SQL query text for TimescaleDB, or None if not found
    """
    scenario_upper = scenario.upper()

    if scenario_upper == "M2":
        query_dir = QUERIES_DIR / "m2" / "ts"
    elif scenario_upper == "O2":
        query_dir = QUERIES_DIR / "o2" / "ts"
    else:
        return None

    for f in query_dir.glob(f"{query_id}_*.sql"):
        query_text = f.read_text(encoding="utf-8")
        if params:
            query_text = substitute_params(query_text, params)
        return query_text
    return None


def extract_point_ids_from_graph_result(records: List, scenario: str) -> List[str]:
    """Extract point_ids from graph query results for hybrid execution.

    Args:
        records: Query result records from Memgraph or Oxigraph
        scenario: M2 or O2

    Returns:
        List of point_id strings
    """
    point_ids = []
    for record in records:
        if scenario == "M2":
            # Memgraph returns dict-like records
            if "point_ids" in record:
                # collect() returns a list
                ids = record["point_ids"]
                if isinstance(ids, list):
                    point_ids.extend(ids)
                else:
                    point_ids.append(str(ids))
            elif "point_id" in record:
                point_ids.append(str(record["point_id"]))
        else:  # O2 - SPARQL
            # SPARQL returns bindings with ?point_ids as comma-separated string
            if "point_ids" in record:
                ids_str = str(record["point_ids"].get("value", ""))
                if ids_str:
                    point_ids.extend(ids_str.split(","))
            elif "point_id" in record:
                point_ids.append(str(record["point_id"].get("value", "")))
    return [pid.strip() for pid in point_ids if pid.strip()]


def compute_stats(latencies: List[float]) -> Dict:
    """Compute latency statistics."""
    import statistics
    if not latencies:
        return {"p50": 0, "p95": 0, "min": 0, "max": 0, "avg": 0}

    sorted_lat = sorted(latencies)
    p95_idx = int(len(sorted_lat) * 0.95)

    return {
        "p50": statistics.median(latencies),
        "p95": sorted_lat[min(p95_idx, len(sorted_lat) - 1)],
        "min": min(latencies),
        "max": max(latencies),
        "avg": statistics.mean(latencies)
    }


def print_query_result(query_id: str, query_result: Dict, query_type: str = "graph") -> None:
    """Print result for a single query after execution.

    Args:
        query_id: Query identifier (e.g., "Q1")
        query_result: Dict with stats, latencies, etc.
        query_type: Type of query for display (graph, hybrid, ts_direct)
    """
    if not query_result or "stats" not in query_result:
        print(f"    {RED}✗ {query_id}: FAILED{RESET}")
        return

    stats = query_result["stats"]
    p50 = stats.get("p50", 0)
    p95 = stats.get("p95", 0)
    n_runs = len(query_result.get("latencies_ms", []))
    rows = query_result.get("rows", 0)

    # Format type indicator
    type_indicator = ""
    if query_type == "hybrid":
        breakdown = query_result.get("breakdown", {})
        graph_ms = breakdown.get("graph_ms", {}).get("avg", 0)
        ts_ms = breakdown.get("ts_ms", {}).get("avg", 0)
        type_indicator = f" {DIM}[graph:{graph_ms:.0f}ms + ts:{ts_ms:.0f}ms]{RESET}"
    elif query_type == "ts_direct":
        type_indicator = f" {DIM}[ts_direct]{RESET}"

    # Color based on p95 performance
    if p95 < 100:
        color = GREEN
    elif p95 < 1000:
        color = YELLOW
    else:
        color = RED

    print(f"    {color}✓ {query_id}{RESET}: p50={p50:>7.1f}ms  p95={p95:>7.1f}ms  "
          f"({n_runs} runs, {rows} rows){type_indicator}")


def print_benchmark_summary(scenario: str, result: Dict) -> None:
    """Print summary table after all queries complete.

    Args:
        scenario: Scenario code (P1, P2, M1, M2, O1, O2)
        result: Complete benchmark result dict
    """
    queries = result.get("queries", {})
    if not queries:
        return

    print(f"\n    {BOLD}{'─' * 60}{RESET}")
    print(f"    {BOLD}Summary: {scenario}{RESET}")
    print(f"    {BOLD}{'─' * 60}{RESET}")

    # Header
    print(f"    {'Query':<6} {'p50':>10} {'p95':>10} {'min':>10} {'max':>10} {'runs':>6}")
    print(f"    {'─' * 6} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 6}")

    all_p50 = []
    all_p95 = []

    for qid in sorted(queries.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
        q = queries[qid]
        stats = q.get("stats", {})
        p50 = stats.get("p50", 0)
        p95 = stats.get("p95", 0)
        min_lat = stats.get("min", 0)
        max_lat = stats.get("max", 0)
        n_runs = len(q.get("latencies_ms", []))

        all_p50.append(p50)
        all_p95.append(p95)

        # Format with units
        def fmt_ms(v):
            if v >= 1000:
                return f"{v/1000:>7.2f}s"
            return f"{v:>7.1f}ms"

        print(f"    {qid:<6} {fmt_ms(p50):>10} {fmt_ms(p95):>10} {fmt_ms(min_lat):>10} {fmt_ms(max_lat):>10} {n_runs:>6}")

    # Footer with averages
    print(f"    {'─' * 6} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 6}")
    if all_p50:
        avg_p50 = sum(all_p50) / len(all_p50)
        avg_p95 = sum(all_p95) / len(all_p95)

        def fmt_ms(v):
            if v >= 1000:
                return f"{v/1000:>7.2f}s"
            return f"{v:>7.1f}ms"

        print(f"    {'AVG':<6} {fmt_ms(avg_p50):>10} {fmt_ms(avg_p95):>10}")

    # Resource metrics
    query_metrics = result.get("query_metrics", {})
    if query_metrics:
        print(f"\n    {BOLD}Resources (query phase):{RESET}")
        peak_mb = query_metrics.get("memory_peak_mb", 0)
        cpu_sec = query_metrics.get("cpu_time_sec", 0)

        if "total_memory_peak_mb" in query_metrics:
            # Hybrid scenario
            graph_peak = query_metrics.get("memory_peak_mb", 0)
            ts_peak = query_metrics.get("ts_memory_peak_mb", 0)
            total_peak = query_metrics.get("total_memory_peak_mb", 0)
            print(f"    RAM peak: {total_peak:.0f} MB (graph: {graph_peak:.0f} MB + TS: {ts_peak:.0f} MB)")
        else:
            print(f"    RAM peak: {peak_mb:.0f} MB")
        print(f"    CPU time: {cpu_sec:.2f}s")

    print(f"    {BOLD}{'─' * 60}{RESET}\n")


def _extract_oxigraph_dataset_info(endpoint: str = "http://localhost:7878") -> Dict:
    """Extract dataset info from Oxigraph via SPARQL.

    For O1/O2 scenarios, we query the loaded RDF data directly since
    there's no CSV nodes file.

    Args:
        endpoint: Oxigraph HTTP endpoint

    Returns:
        Dict with lists of available IDs by type
    """
    import requests

    info = {
        "meters": [],
        "equipment": [],
        "spaces": [],
        "floors": [],
        "buildings": [],
        "tenants": [],
        "zones": [],
        "points": [],
        "ts_end": int(time.time()),
    }

    # SPARQL queries to get balanced samples of each node type
    # We query each type separately to avoid Point nodes dominating
    type_queries = {
        "equipment": """
            PREFIX btb: <http://basetype.benchmark/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?id WHERE { ?id rdf:type btb:Equipment } LIMIT 100
        """,
        "spaces": """
            PREFIX btb: <http://basetype.benchmark/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?id WHERE { ?id rdf:type btb:Space } LIMIT 100
        """,
        "floors": """
            PREFIX btb: <http://basetype.benchmark/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?id WHERE { ?id rdf:type btb:Floor } LIMIT 50
        """,
        "buildings": """
            PREFIX btb: <http://basetype.benchmark/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?id WHERE { ?id rdf:type btb:Building } LIMIT 20
        """,
        "tenants": """
            PREFIX btb: <http://basetype.benchmark/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?id WHERE { ?id rdf:type btb:Tenant } LIMIT 20
        """,
        "points": """
            PREFIX btb: <http://basetype.benchmark/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?id WHERE { ?id rdf:type btb:Point } LIMIT 100
        """,
        "meters": """
            PREFIX btb: <http://basetype.benchmark/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?id WHERE {
                ?id rdf:type btb:Equipment .
                ?id btb:equipment_type ?type .
                FILTER(CONTAINS(?type, "Meter"))
            } LIMIT 50
        """,
    }

    try:
        # Query each type separately for balanced sampling
        for info_key, query in type_queries.items():
            resp = requests.get(
                f"{endpoint}/query",
                params={"query": query},
                headers={"Accept": "application/sparql-results+json"},
                timeout=30
            )
            if resp.status_code != 200:
                continue

            data = resp.json()
            bindings = data.get("results", {}).get("bindings", [])

            for binding in bindings:
                node_uri = binding.get("id", {}).get("value", "")
                if node_uri:
                    # Extract local ID from URI (http://basetype.benchmark/equip_001 -> equip_001)
                    # Queries use $METER_ID etc. which gets substituted into URI template
                    if node_uri.startswith("http://basetype.benchmark/"):
                        node_id = node_uri.replace("http://basetype.benchmark/", "")
                    else:
                        # Fallback: take last segment after /
                        node_id = node_uri.rsplit("/", 1)[-1]
                    info[info_key].append(node_id)

        # Log what we found
        counts = {k: len(v) for k, v in info.items() if isinstance(v, list)}
        print_info(f"Dataset info from SPARQL: {counts}")

    except Exception as e:
        print_warn(f"Error extracting Oxigraph dataset info: {e}")

    return info


def extract_dataset_info(export_dir: Path, scenario: str) -> Dict:
    """Extract available IDs from dataset for query parameterization.

    Reads the nodes file to extract meters, equipment, spaces, floors, etc.
    for generating query variants with realistic parameters.

    For O1/O2 scenarios, queries Oxigraph directly via SPARQL since
    there's no CSV nodes file.

    Args:
        export_dir: Base export directory
        scenario: Scenario code (P1, P2, M1, M2, O1, O2)

    Returns:
        Dict with lists of available IDs by type
    """
    import csv

    # O1/O2: Query Oxigraph directly (no CSV nodes file)
    if scenario.upper() in ("O1", "O2"):
        return _extract_oxigraph_dataset_info()

    files = get_scenario_files(export_dir, scenario)
    nodes_file = files.get("nodes")

    info = {
        "meters": [],
        "equipment": [],
        "spaces": [],
        "floors": [],
        "buildings": [],
        "tenants": [],
        "zones": [],
        "points": [],
        "ts_end": int(time.time()),
    }

    if not nodes_file or not nodes_file.exists():
        print_warn(f"Nodes file not found for dataset info extraction")
        return info

    try:
        with open(nodes_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_id = row.get("id", row.get("node_id", ""))
                node_type = row.get("type", row.get("node_type", "")).lower()
                # Equipment type (for Brick Schema: Equipment with equipment_type property)
                equipment_type = row.get("equipment_type", "").lower()

                # Meters: check both type and equipment_type (Brick Schema uses Equipment + equipment_type)
                if "meter" in node_type or "meter" in equipment_type:
                    info["meters"].append(node_id)
                elif "equipment" in node_type or "ahu" in node_type or "vav" in node_type:
                    info["equipment"].append(node_id)
                elif "space" in node_type or "room" in node_type:
                    info["spaces"].append(node_id)
                elif "floor" in node_type:
                    info["floors"].append(node_id)
                elif "building" in node_type:
                    info["buildings"].append(node_id)
                elif "tenant" in node_type or "organization" in node_type:
                    info["tenants"].append(node_id)
                elif "zone" in node_type:
                    info["zones"].append(node_id)
                elif "point" in node_type or "sensor" in node_type:
                    info["points"].append(node_id)

        # Limit to avoid too many options
        for key in info:
            if isinstance(info[key], list) and len(info[key]) > 100:
                info[key] = info[key][:100]

    except Exception as e:
        print_warn(f"Error extracting dataset info: {e}")

    return info


def run_query_benchmark(
    query_id: str,
    query_text: str,
    execute_fn,
    container_name: str,
    n_warmup: int,
    n_runs: int,
    variant_idx: int = 0,
    total_variants: int = 1,
    params: Dict = None,
    extended_metrics: bool = True
) -> Dict:
    """Run benchmark for a single query with warmup, measured runs, and resource monitoring.

    This is a helper to reduce duplication across P/M/O benchmark functions.

    Args:
        query_id: Query identifier (e.g., "Q1")
        query_text: The query string to execute
        execute_fn: Callable that executes the query and returns row count
                   Signature: execute_fn(query_text) -> int (row count)
        container_name: Docker container name for resource monitoring
        n_warmup: Number of warmup iterations
        n_runs: Number of measured runs
        variant_idx: Current variant index (for display)
        total_variants: Total number of variants (for display)
        params: Parameters used for this variant (for logging)
        extended_metrics: If True and on Linux, collect extended metrics (CPU breakdown, energy)

    Returns:
        Dict with latencies_ms, rows, stats, resources, params
    """
    # Display progress with variant info
    if total_variants > 1:
        print(f"    {query_id} [{variant_idx+1}/{total_variants}]...", end=" ", flush=True)
    else:
        print(f"    {query_id}...", end=" ", flush=True)

    # Drop caches before query
    drop_caches()

    # Warmup (ignore results)
    for _ in range(n_warmup):
        try:
            execute_fn(query_text)
        except Exception:
            pass

    # Take snapshot of container stats BEFORE runs
    # For fast queries, continuous sampling doesn't work (interval > query time)
    stats_before = get_container_stats(container_name)

    latencies = []
    rows = 0
    for run_idx in range(n_runs):
        try:
            t0 = time.perf_counter()
            rows = execute_fn(query_text)
            latencies.append((time.perf_counter() - t0) * 1000)  # ms
        except Exception as e:
            print_warn(f"Query error: {e}")

    # Take snapshot AFTER runs
    stats_after = get_container_stats(container_name)

    # Build resource metrics from snapshots
    # For fast queries, we report the steady-state container memory/CPU
    mem_mb = 0
    cpu_pct = 0
    if stats_after:
        mem_mb = stats_after.get("mem_mb", 0)
        cpu_pct = stats_after.get("cpu_pct", 0)
    elif stats_before:
        mem_mb = stats_before.get("mem_mb", 0)
        cpu_pct = stats_before.get("cpu_pct", 0)

    query_resources = {
        "mem_mb": {"min": mem_mb, "max": mem_mb, "avg": mem_mb},
        "cpu_pct": {"min": cpu_pct, "max": cpu_pct, "avg": cpu_pct},
        "sample_count": 2,
    }

    stats = compute_stats(latencies)

    # Build result
    result = {
        "latencies_ms": latencies,
        "rows": rows,
        "stats": stats,
        "resources": query_resources,
        "params": params or {}
    }

    # Display result
    print(f"p50={stats['p50']:.1f}ms p95={stats['p95']:.1f}ms rows={rows} "
          f"(RAM:{mem_mb:.0f}MB CPU:{cpu_pct:.1f}%)")

    return result


def run_query_with_variants(
    query_id: str,
    scenario: str,
    execute_fn,
    container_name: str,
    n_warmup: int,
    n_runs: int,
    profile: str,
    dataset_info: Dict,
    seed: int = 42
) -> Dict:
    """Run benchmark for a query with multiple parameter variants.

    For queries with parameters (Q1-Q4, Q6-Q13), generates n_variants different
    parameter sets based on the profile (small=3, medium=5, large=10).

    Args:
        query_id: Query identifier (e.g., "Q1")
        scenario: Scenario code for query loading
        execute_fn: Query execution function
        container_name: Docker container for monitoring
        n_warmup: Warmup iterations per variant
        n_runs: Measured runs per variant
        profile: Profile name for protocol config
        dataset_info: Dict with available IDs for parameterization
        seed: Random seed for reproducibility

    Returns:
        Dict with aggregated results across all variants
    """
    # Get variants for this query (pass scenario for correct date format)
    variants = get_query_variants(query_id, profile, dataset_info, seed, scenario)
    n_variants = len(variants)

    # Get base query text
    base_query = load_query(scenario, query_id)
    if not base_query:
        print_warn(f"Query {query_id} not found, skipping")
        return None

    # Check if query has parameters
    has_params = bool(QUERY_PARAMS.get(query_id, []))

    if has_params and n_variants > 1:
        protocol = get_protocol_config(profile)
        print(f"\n    {CYAN}{query_id}{RESET}: {n_variants} variants × {n_runs} runs × {n_warmup} warmup")

    all_results = []

    for i, params in enumerate(variants):
        # Substitute parameters in query
        query_text = substitute_params(base_query, params) if params else base_query

        result = run_query_benchmark(
            query_id=query_id,
            query_text=query_text,
            execute_fn=execute_fn,
            container_name=container_name,
            n_warmup=n_warmup,
            n_runs=n_runs,
            variant_idx=i,
            total_variants=n_variants if has_params else 1,
            params=params
        )
        all_results.append(result)

    # Aggregate results across variants
    if len(all_results) == 1:
        return all_results[0]

    # Combine latencies from all variants
    all_latencies = []
    total_rows = 0
    for r in all_results:
        all_latencies.extend(r["latencies_ms"])
        total_rows += r["rows"]

    # Aggregate resource usage (max of maxes, avg of avgs)
    combined_resources = {
        "mem_mb": {
            "max": max(r["resources"]["mem_mb"]["max"] for r in all_results),
            "avg": sum(r["resources"]["mem_mb"]["avg"] for r in all_results) / len(all_results),
        },
        "cpu_pct": {
            "max": max(r["resources"]["cpu_pct"]["max"] for r in all_results),
            "avg": sum(r["resources"]["cpu_pct"]["avg"] for r in all_results) / len(all_results),
        }
    }

    combined_stats = compute_stats(all_latencies)

    # Print summary for multi-variant queries
    print(f"    {GREEN}→ {query_id} combined{RESET}: p50={combined_stats['p50']:.1f}ms "
          f"p95={combined_stats['p95']:.1f}ms ({n_variants} variants, {len(all_latencies)} total runs)")

    return {
        "latencies_ms": all_latencies,
        "rows": total_rows,
        "stats": combined_stats,
        "resources": combined_resources,
        "variants": all_results,
        "n_variants": n_variants
    }


def run_scenario_benchmark(scenario: str, export_dir: Path, profile: str = "small") -> Dict:
    """Run benchmark for a single scenario using existing loaders.

    Args:
        scenario: P1, P2, M1, M2, O1, O2
        export_dir: Path to exported dataset
        profile: Profile name (e.g., 'small-2d') for protocol config

    Returns:
        Dict with benchmark results
    """
    # Get protocol config based on profile scale
    protocol = get_protocol_config(profile)
    n_warmup = protocol["n_warmup"]
    n_runs = protocol["n_runs"]
    n_variants = protocol["n_variants"]

    # Display benchmark protocol info
    print_info(f"Benchmark Protocol: {n_variants} variants × {n_runs} runs + {n_warmup} warmup per query")

    # Collect system info for benchmark context (on Linux)
    system_info = {}
    if IS_LINUX:
        try:
            from basetype_benchmark.benchmark.resource_monitor import get_system_info
            system_info = get_system_info()
            if system_info.get("cloud", {}).get("is_cloud"):
                provider = system_info["cloud"].get("provider", "unknown")
                ram_gb = system_info["cloud"].get("ram_gb", "?")
                print_info(f"Running on cloud: {provider} ({ram_gb} GB RAM)")
        except ImportError:
            pass

    result = {
        "scenario": scenario,
        "profile": profile,
        "protocol": {"n_warmup": n_warmup, "n_runs": n_runs, "n_variants": n_variants},
        "system_info": system_info,
        "status": "pending",
        "load_time_s": 0.0,
        "queries": {},
        "error": None
    }

    start_total = time.time()

    try:
        if scenario in ["P1", "P2"]:
            result = _run_postgres_benchmark(scenario, export_dir, result, n_warmup, n_runs, profile)
        elif scenario in ["M1", "M2"]:
            result = _run_memgraph_benchmark(scenario, export_dir, result, n_warmup, n_runs, profile)
        elif scenario in ["O1", "O2"]:
            result = _run_oxigraph_benchmark(scenario, export_dir, result, n_warmup, n_runs, profile)
        else:
            result["status"] = "error"
            result["error"] = f"Unknown scenario: {scenario}"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        import traceback
        traceback.print_exc()

    result["total_time_s"] = time.time() - start_total
    return result


def _ensure_timescaledb_timeseries(export_dir: Path, scenario: str) -> bool:
    """Ensure TimescaleDB has timeseries data for hybrid scenarios (M2/O2).

    Returns True if timeseries are already loaded or successfully loaded.
    Returns False if loading failed.
    """
    from basetype_benchmark.loaders.postgres.load import get_connection

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Check if timeseries table exists and has data
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'timeseries'
            )
        """)
        table_exists = cur.fetchone()[0]

        if table_exists:
            cur.execute("SELECT COUNT(*) FROM timeseries")
            count = cur.fetchone()[0]
            if count > 0:
                print_info(f"TimescaleDB timeseries already loaded ({count:,} rows)")
                cur.close()
                conn.close()
                return True

        # Need to load timeseries - get the file
        files = get_scenario_files(export_dir, scenario)
        ts_file = files.get("timeseries")

        if not ts_file or not ts_file.exists():
            print_warn(f"Timeseries file not found: {ts_file}")
            cur.close()
            conn.close()
            return False

        # Create table if not exists
        if not table_exists:
            print_info("Creating timeseries table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS timeseries (
                    time TIMESTAMPTZ NOT NULL,
                    point_id TEXT NOT NULL,
                    value DOUBLE PRECISION
                )
            """)
            try:
                cur.execute("SELECT create_hypertable('timeseries', 'time', if_not_exists => TRUE)")
            except Exception:
                pass
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ts_point_time ON timeseries(point_id, time DESC)")
            conn.commit()

        # Load timeseries via COPY
        ts_size_mb = ts_file.stat().st_size / (1024 * 1024)
        print_info(f"Loading timeseries for {scenario} ({ts_size_mb:.0f} MB)...")
        t0 = time.time()

        with open(ts_file, 'r', encoding='utf-8') as f:
            cur.copy_expert(
                "COPY timeseries (point_id, time, value) FROM STDIN WITH CSV HEADER",
                f
            )
        conn.commit()

        elapsed = time.time() - t0
        cur.execute("SELECT COUNT(*) FROM timeseries")
        ts_count = cur.fetchone()[0]
        rate = ts_count / elapsed if elapsed > 0 else 0
        print_ok(f"Loaded {ts_count:,} timeseries rows in {elapsed:.1f}s ({rate:.0f}/s)")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        print_err(f"Failed to ensure TimescaleDB timeseries: {e}")
        return False


def _run_postgres_benchmark(scenario: str, export_dir: Path, result: Dict,
                            n_warmup: int = N_WARMUP, n_runs: int = N_RUNS,
                            profile: str = "small") -> Dict:
    """Run PostgreSQL benchmark (P1 or P2)."""
    from basetype_benchmark.loaders.postgres.load import (
        get_connection, clear_database, load_p1, load_p2
    )

    container_name = "btb_timescaledb"
    print_info(f"Connecting to PostgreSQL...")
    conn = get_connection()

    try:
        # Clear and load with resource monitoring
        print_info("Clearing database...")
        clear_database(conn)

        print_info(f"Loading data ({scenario} schema)...")

        # Get and display file paths for debugging
        files = get_scenario_files(export_dir, scenario)
        print_info(f"Export dir: {export_dir}")
        print_info(f"Files to load:")
        for key, path in files.items():
            exists = "OK" if path.exists() else "MISSING"
            print(f"          - {key}: {path.name} [{exists}]")

        load_monitor = ResourceMonitor(container_name, interval_s=1.0)
        load_monitor.start()
        load_start = time.time()

        # Load using V2 file structure
        load_result = _load_postgres_from_csv(conn, export_dir, scenario)

        result["load_time_s"] = time.time() - load_start
        result["load_resources"] = load_monitor.stop()
        # Remove raw samples to reduce result size
        if "samples" in result["load_resources"]:
            del result["load_resources"]["samples"]

        print_ok(f"Data loaded in {result['load_time_s']:.1f}s "
                 f"(peak RAM: {result['load_resources']['mem_mb']['max']:.0f}MB, "
                 f"avg CPU: {result['load_resources']['cpu_pct']['avg']:.1f}%)")

        # Reset memory.peak after ingestion to measure query impact only
        cgroup_path = get_container_cgroup_path(container_name)
        if cgroup_path:
            reset_memory_peak(cgroup_path)

        # Define executor for PostgreSQL queries
        def pg_execute(query: str) -> int:
            try:
                with conn.cursor() as cur:
                    cur.execute(query)
                    data = cur.fetchall()
                    conn.commit()
                    return len(data)
            except Exception:
                conn.rollback()
                raise

        # Extract dataset info for query parameterization
        dataset_info = extract_dataset_info(export_dir, scenario)
        print_info(f"Dataset info: {len(dataset_info['meters'])} meters, "
                   f"{len(dataset_info['equipment'])} equipment, "
                   f"{len(dataset_info['spaces'])} spaces")

        # Execute queries with variants
        queries_to_run = QUERIES_BY_SCENARIO.get(scenario, [])
        total_queries = len(queries_to_run)
        query_start_time = time.time()
        errors_count = 0

        # Snapshot before queries (for CPU delta calculation)
        metrics_before = CGroupMetricsSnapshot(container_name)

        print(f"\n    {BOLD}Running {total_queries} queries...{RESET}")

        for qi, query_id in enumerate(queries_to_run):
            query_result = run_query_with_variants(
                query_id=query_id,
                scenario=scenario,
                execute_fn=pg_execute,
                container_name=container_name,
                n_warmup=n_warmup,
                n_runs=n_runs,
                profile=profile,
                dataset_info=dataset_info
            )
            if query_result:
                result["queries"][query_id] = query_result
                print_query_result(query_id, query_result, "graph")
            else:
                errors_count += 1
                print(f"    {RED}✗ {query_id}: FAILED{RESET}")

        # Snapshot after queries
        metrics_after = CGroupMetricsSnapshot(container_name)
        query_metrics = CGroupMetricsSnapshot.compute_delta(metrics_before, metrics_after)

        # Store query phase metrics
        result["query_metrics"] = query_metrics

        # Total elapsed time
        total_elapsed = time.time() - query_start_time
        result["query_elapsed_s"] = total_elapsed

        if errors_count > 0:
            print_warn(f"{errors_count} query errors")

        # Print summary table
        print_benchmark_summary(scenario, result)

        result["status"] = "completed"

    finally:
        conn.close()

    return result


def _load_postgres_from_csv(conn, export_dir: Path, scenario: str) -> Dict:
    """Load PostgreSQL from CSV files (V2 format).

    Args:
        conn: Database connection
        export_dir: Base export directory (e.g., exports/small-1w_seed42)
        scenario: Scenario code (P1 or P2)
    """
    import csv
    from psycopg2.extras import execute_batch

    # Get file paths for this scenario
    files = get_scenario_files(export_dir, scenario)

    cur = conn.cursor()

    # Create schema
    cur.execute("DROP TABLE IF EXISTS timeseries CASCADE")
    cur.execute("DROP TABLE IF EXISTS edges CASCADE")
    cur.execute("DROP TABLE IF EXISTS nodes CASCADE")

    # Nodes table - schema depends on P1 (relational) vs P2 (JSONB)
    if scenario == "P1":
        cur.execute("""
            CREATE TABLE nodes (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT,
                domain TEXT,
                equipment_type TEXT,
                space_type TEXT,
                building_id TEXT,
                floor_id TEXT,
                space_id TEXT,
                data JSONB DEFAULT '{}'
            )
        """)
    else:  # P2 - JSONB schema (with building_id extracted for filtering)
        cur.execute("""
            CREATE TABLE nodes (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT,
                building_id TEXT,
                properties JSONB DEFAULT '{}'
            )
        """)

    # Edges table (no FK for performance)
    cur.execute("""
        CREATE TABLE edges (
            src_id TEXT NOT NULL,
            dst_id TEXT NOT NULL,
            rel_type TEXT NOT NULL,
            PRIMARY KEY (src_id, dst_id, rel_type)
        )
    """)

    # Timeseries table
    cur.execute("""
        CREATE TABLE timeseries (
            time TIMESTAMPTZ NOT NULL,
            point_id TEXT NOT NULL,
            value DOUBLE PRECISION
        )
    """)

    # Try to create hypertable
    try:
        cur.execute("SELECT create_hypertable('timeseries', 'time', if_not_exists => TRUE)")
    except Exception:
        pass

    # Create indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_building ON nodes(building_id)")
    if scenario == "P1":
        cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_domain ON nodes(domain)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, rel_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, rel_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ts_point_time ON timeseries(point_id, time DESC)")

    conn.commit()

    # Load nodes from CSV
    nodes_file = files["nodes"]
    total_nodes = 0
    t0 = time.time()
    if nodes_file.exists():
        with open(nodes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                if scenario == "P1":
                    batch.append((
                        row['id'],
                        row['type'],
                        row.get('name', ''),
                        row.get('domain', ''),
                        row.get('equipment_type', ''),
                        row.get('space_type', ''),
                        row.get('building_id', ''),
                        row.get('floor_id', ''),
                        row.get('space_id', ''),
                        row.get('data', '{}')
                    ))
                else:  # P2
                    batch.append((
                        row['id'],
                        row['type'],
                        row.get('name', ''),
                        row.get('building_id', ''),
                        row.get('properties', '{}')
                    ))
                if len(batch) >= 1000:
                    if scenario == "P1":
                        execute_batch(cur, """
                            INSERT INTO nodes (id, type, name, domain, equipment_type, space_type,
                                             building_id, floor_id, space_id, data)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO NOTHING
                        """, batch)
                    else:
                        execute_batch(cur, """
                            INSERT INTO nodes (id, type, name, building_id, properties)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO NOTHING
                        """, batch)
                    conn.commit()
                    total_nodes += len(batch)
                    elapsed = time.time() - t0
                    rate = total_nodes / elapsed if elapsed > 0 else 0
                    print(f"\r      Loading nodes: {total_nodes:,} ({rate:.0f}/s)...", end="", flush=True)
                    batch.clear()
            if batch:
                if scenario == "P1":
                    execute_batch(cur, """
                        INSERT INTO nodes (id, type, name, domain, equipment_type, space_type,
                                         building_id, floor_id, space_id, data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, batch)
                else:
                    execute_batch(cur, """
                        INSERT INTO nodes (id, type, name, building_id, properties)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, batch)
                conn.commit()
                total_nodes += len(batch)
        elapsed = time.time() - t0
        rate = total_nodes / elapsed if elapsed > 0 else 0
        print(f"\r      Loaded {total_nodes:,} nodes in {elapsed:.1f}s ({rate:.0f}/s)          ")

    # Load edges from CSV
    edges_file = files["edges"]
    total_edges = 0
    t0 = time.time()
    if edges_file.exists():
        with open(edges_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                batch.append((row['src_id'], row['dst_id'], row['rel_type']))
                if len(batch) >= 1000:
                    execute_batch(cur, """
                        INSERT INTO edges (src_id, dst_id, rel_type)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, batch)
                    conn.commit()
                    total_edges += len(batch)
                    elapsed = time.time() - t0
                    rate = total_edges / elapsed if elapsed > 0 else 0
                    print(f"\r      Loading edges: {total_edges:,} ({rate:.0f}/s)...", end="", flush=True)
                    batch.clear()
            if batch:
                execute_batch(cur, """
                    INSERT INTO edges (src_id, dst_id, rel_type)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, batch)
                conn.commit()
                total_edges += len(batch)
        elapsed = time.time() - t0
        rate = total_edges / elapsed if elapsed > 0 else 0
        print(f"\r      Loaded {total_edges:,} edges in {elapsed:.1f}s ({rate:.0f}/s)          ")

    # Load timeseries from CSV (use COPY for performance)
    # CSV format from exporter_v2: point_id, time, value
    ts_file = files["timeseries"]
    if ts_file.exists():
        ts_size_mb = ts_file.stat().st_size / (1024 * 1024)
        print(f"      Loading timeseries ({ts_size_mb:.0f} MB, COPY in progress)...", end="", flush=True)
        t0 = time.time()
        with open(ts_file, 'r', encoding='utf-8') as f:
            cur.copy_expert(
                "COPY timeseries (point_id, time, value) FROM STDIN WITH CSV HEADER",
                f
            )
        conn.commit()
        elapsed = time.time() - t0
        # Get row count
        cur.execute("SELECT COUNT(*) FROM timeseries")
        ts_count = cur.fetchone()[0]
        rate = ts_count / elapsed if elapsed > 0 else 0
        print(f"\r      Loaded {ts_count:,} timeseries in {elapsed:.1f}s ({rate:.0f}/s)          ")

    cur.close()
    return {"nodes": total_nodes, "edges": total_edges, "timeseries": True}


# =============================================================================
# MEMGRAPH CSV LOADERS (V2 FORMAT)
# =============================================================================

def _load_memgraph_nodes_csv(session, nodes_file: Path) -> int:
    """Load nodes from CSV into Memgraph using batched Cypher.

    CSV format (V2): id,type,name,properties
    """
    import csv
    import json

    batch = []
    total = 0
    batch_size = 5000
    t0 = time.time()

    with open(nodes_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            node = {
                'id': row['id'],
                'type': row['type'],
                'name': row.get('name', ''),
                'equipment_type': row.get('equipment_type', '')
            }
            # Parse properties if present (may override equipment_type)
            if row.get('properties'):
                try:
                    props = json.loads(row['properties'])
                    node.update(props)
                except (json.JSONDecodeError, TypeError):
                    pass

            batch.append(node)

            if len(batch) >= batch_size:
                session.run(
                    "UNWIND $batch AS row "
                    "CREATE (n:Node {id: row.id, type: row.type, name: row.name, equipment_type: row.equipment_type})",
                    batch=batch
                )
                total += len(batch)
                elapsed = time.time() - t0
                rate = total / elapsed if elapsed > 0 else 0
                print(f"\r      Loading nodes: {total:,} ({rate:.0f}/s)...", end="", flush=True)
                batch.clear()

        if batch:
            session.run(
                "UNWIND $batch AS row "
                "CREATE (n:Node {id: row.id, type: row.type, name: row.name, equipment_type: row.equipment_type})",
                batch=batch
            )
            total += len(batch)

    elapsed = time.time() - t0
    rate = total / elapsed if elapsed > 0 else 0
    print(f"\r      Loaded {total:,} nodes in {elapsed:.1f}s ({rate:.0f}/s)          ")
    return total


def _load_memgraph_edges_csv(session, edges_file: Path) -> int:
    """Load edges from CSV into Memgraph using batched Cypher.

    CSV format (V2): src_id,dst_id,rel_type
    """
    import csv

    # Group edges by relationship type for efficient loading
    edges_by_type = {}
    total = 0
    batch_size = 1000  # Smaller batch for edges (MATCH is expensive)
    t0 = time.time()

    with open(edges_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel_type = row['rel_type']
            if rel_type not in edges_by_type:
                edges_by_type[rel_type] = []
            edges_by_type[rel_type].append({
                'src': row['src_id'],
                'dst': row['dst_id']
            })

    # Load each relationship type
    for rel_type, edges in edges_by_type.items():
        for i in range(0, len(edges), batch_size):
            batch = edges[i:i + batch_size]
            session.run(
                "UNWIND $batch AS row "
                "MATCH (s:Node {id: row.src}) "
                "MATCH (d:Node {id: row.dst}) "
                f"CREATE (s)-[:{rel_type}]->(d)",
                batch=batch
            )
            total += len(batch)
            elapsed = time.time() - t0
            rate = total / elapsed if elapsed > 0 else 0
            print(f"\r      Loading edges: {total:,} ({rate:.0f}/s)...", end="", flush=True)

    elapsed = time.time() - t0
    rate = total / elapsed if elapsed > 0 else 0
    print(f"\r      Loaded {total:,} edges in {elapsed:.1f}s ({rate:.0f}/s)          ")
    return total


def _load_memgraph_chunks_csv(session, chunks_file: Path) -> int:
    """Load daily timeseries chunks from CSV into Memgraph.

    CSV format (V2.1): point_id,date_day,timestamps,values
    One chunk per (point, day) pair (standard BOS daily archive pattern).
    Creates ArchiveDay nodes linked to Point nodes via HAS_TIMESERIES.
    """
    import csv
    import json

    batch_nodes = []
    batch_edges = []
    total = 0
    batch_size = 2000
    t0 = time.time()

    with open(chunks_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Use date_day for unique chunk ID
            date_day = row.get('date_day', row.get('chunk_idx', '0'))
            chunk_id = f"archive_{row['point_id']}_{date_day}"

            # Parse timestamps and values arrays
            try:
                timestamps = json.loads(row['timestamps'])
            except (json.JSONDecodeError, TypeError):
                timestamps = []

            try:
                values = json.loads(row['values'])
            except (json.JSONDecodeError, TypeError):
                values = []

            batch_nodes.append({
                'id': chunk_id,
                'point_id': row['point_id'],
                'date_day': date_day,
                'timestamps': timestamps,
                'values': values
            })
            batch_edges.append({
                'src': row['point_id'],
                'dst': chunk_id
            })

            if len(batch_nodes) >= batch_size:
                # Create ArchiveDay nodes with explicit timestamps
                session.run(
                    "UNWIND $batch AS row "
                    "CREATE (c:ArchiveDay {id: row.id, point_id: row.point_id, "
                    "date_day: row.date_day, timestamps: row.timestamps, values: row.values})",
                    batch=batch_nodes
                )
                # Create HAS_TIMESERIES edges
                session.run(
                    "UNWIND $batch AS row "
                    "MATCH (p:Node {id: row.src}) "
                    "MATCH (c:ArchiveDay {id: row.dst}) "
                    "CREATE (p)-[:HAS_TIMESERIES]->(c)",
                    batch=batch_edges
                )
                total += len(batch_nodes)
                elapsed = time.time() - t0
                rate = total / elapsed if elapsed > 0 else 0
                print(f"\r      Loading daily archives: {total:,} ({rate:.0f}/s)...", end="", flush=True)
                batch_nodes.clear()
                batch_edges.clear()

        if batch_nodes:
            session.run(
                "UNWIND $batch AS row "
                "CREATE (c:ArchiveDay {id: row.id, point_id: row.point_id, "
                "date_day: row.date_day, timestamps: row.timestamps, values: row.values})",
                batch=batch_nodes
            )
            session.run(
                "UNWIND $batch AS row "
                "MATCH (p:Node {id: row.src}) "
                "MATCH (c:ArchiveDay {id: row.dst}) "
                "CREATE (p)-[:HAS_TIMESERIES]->(c)",
                batch=batch_edges
            )
            total += len(batch_nodes)

    elapsed = time.time() - t0
    rate = total / elapsed if elapsed > 0 else 0
    print(f"\r      Loaded {total:,} daily archives in {elapsed:.1f}s ({rate:.0f}/s)          ")
    return total


def run_hybrid_query(
    query_id: str,
    scenario: str,
    graph_execute_raw,
    ts_conn,
    container_name: str,
    ts_container: str,
    n_warmup: int,
    n_runs: int,
    profile: str,
    dataset_info: Dict,
    seed: int = 42
) -> Dict:
    """Run hybrid query: Graph (Cypher/SPARQL) → TimescaleDB.

    For hybrid queries:
    1. Execute graph query to get point_ids
    2. Execute TimescaleDB query with those point_ids
    3. Measure combined latency

    Args:
        query_id: Q6-Q13
        scenario: M2 or O2
        graph_execute_raw: Function to execute graph query (Cypher or SPARQL)
        ts_conn: TimescaleDB connection
        container_name: Graph container name (Memgraph or Oxigraph)
        ts_container: TimescaleDB container name
        n_warmup: Warmup iterations
        n_runs: Measured runs
        profile: small/medium/large
        dataset_info: Dataset info for parameterization

    Returns:
        Dict with latencies, stats, and breakdown (graph_ms, ts_ms)
    """
    # PROTOCOL_CONFIG is defined at module level (line ~1282)
    config = PROTOCOL_CONFIG.get(profile, PROTOCOL_CONFIG["small"])
    n_variants = config.get("n_variants", 3)

    variants = get_query_variants(query_id, profile, dataset_info, seed, scenario)
    if not variants:
        variants = [{}]

    all_latencies = []
    all_graph_latencies = []
    all_ts_latencies = []
    total_rows = 0

    query_type = HYBRID_QUERY_TYPE.get(query_id, "graph_only")

    for params in variants[:n_variants]:
        graph_query = load_query(scenario, query_id, params)
        if not graph_query:
            continue

        ts_query_template = load_ts_query(scenario, query_id, params)

        # Warmup
        for _ in range(n_warmup):
            try:
                if query_type == "ts_direct":
                    with ts_conn.cursor() as cur:
                        cur.execute(ts_query_template)
                        cur.fetchall()
                        ts_conn.commit()
                elif query_type == "hybrid":
                    graph_result = graph_execute_raw(graph_query)
                    point_ids = extract_point_ids_from_graph_result(graph_result, scenario)
                    if point_ids and ts_query_template:
                        ts_query = ts_query_template.replace("$POINT_IDS", f"ARRAY{point_ids}")
                        with ts_conn.cursor() as cur:
                            cur.execute(ts_query)
                            cur.fetchall()
                            ts_conn.commit()
            except Exception:
                # Rollback to recover from transaction abort state
                try:
                    ts_conn.rollback()
                except Exception:
                    pass

        # Measured runs
        for _ in range(n_runs):
            try:
                if query_type == "ts_direct":
                    t0 = time.perf_counter()
                    with ts_conn.cursor() as cur:
                        cur.execute(ts_query_template)
                        rows = cur.fetchall()
                        ts_conn.commit()
                    total_ms = (time.perf_counter() - t0) * 1000
                    all_latencies.append(total_ms)
                    all_ts_latencies.append(total_ms)
                    all_graph_latencies.append(0)
                    total_rows = len(rows)

                elif query_type == "hybrid":
                    # Step 1: Graph query
                    t0 = time.perf_counter()
                    graph_result = graph_execute_raw(graph_query)
                    graph_ms = (time.perf_counter() - t0) * 1000

                    # Extract point_ids from result
                    point_ids = extract_point_ids_from_graph_result(graph_result, scenario)

                    # Step 2: TimescaleDB query
                    ts_ms = 0
                    if point_ids and ts_query_template:
                        ts_query = ts_query_template.replace("$POINT_IDS", f"ARRAY{point_ids}")
                        t1 = time.perf_counter()
                        with ts_conn.cursor() as cur:
                            cur.execute(ts_query)
                            rows = cur.fetchall()
                            ts_conn.commit()
                        ts_ms = (time.perf_counter() - t1) * 1000
                        total_rows = len(rows)

                    total_ms = graph_ms + ts_ms
                    all_latencies.append(total_ms)
                    all_graph_latencies.append(graph_ms)
                    all_ts_latencies.append(ts_ms)

            except Exception as e:
                print_warn(f"Hybrid query error: {e}")
                # Rollback to recover from transaction abort state
                try:
                    ts_conn.rollback()
                except Exception:
                    pass

    if not all_latencies:
        return None

    stats = compute_stats(all_latencies)

    return {
        "latencies_ms": all_latencies,
        "rows": total_rows,
        "stats": stats,
        "hybrid": True,
        "breakdown": {
            "graph_ms": compute_stats(all_graph_latencies),
            "ts_ms": compute_stats(all_ts_latencies),
        }
    }


def _run_memgraph_benchmark(scenario: str, export_dir: Path, result: Dict,
                            n_warmup: int = N_WARMUP, n_runs: int = N_RUNS,
                            profile: str = "small") -> Dict:
    """Run Memgraph benchmark (M1 or M2).

    Uses CSV loading via driver for V2 format.
    M1: Graph + timeseries chunks as array nodes
    M2: Graph + TimescaleDB for timeseries
    """
    from basetype_benchmark.loaders.memgraph.load import (
        get_driver, load_constraints, LoadingTimeout, LoadingStalled
    )

    container_name = "btb_memgraph"
    print_info("Connecting to Memgraph...")
    try:
        driver = get_driver()
    except Exception as e:
        print_err(f"Failed to connect to Memgraph: {e}")
        dump_container_debug(container_name)
        result["status"] = "error"
        result["error"] = f"Connection failed: {e}"
        return result

    # Get file paths for this scenario (V2 format)
    files = get_scenario_files(export_dir, scenario)
    print_info(f"Export dir: {export_dir}")
    print_info(f"Files to load:")
    for key, path in files.items():
        exists = "OK" if path.exists() else "MISSING"
        print(f"          - {key}: {path.name} [{exists}]")

    try:
        # Clear and load with resource monitoring
        print_info("Clearing database...")
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

        print_info(f"Loading data ({scenario})...")
        load_monitor = ResourceMonitor(container_name, interval_s=1.0)
        load_monitor.start()
        load_start = time.time()

        # Get file paths
        nodes_file = files.get("nodes")
        edges_file = files.get("edges")
        chunks_file = files.get("chunks")

        with driver.session() as session:
            load_constraints(session)

            # Load nodes from CSV
            if nodes_file and nodes_file.exists():
                _load_memgraph_nodes_csv(session, nodes_file)
            else:
                load_monitor.stop()
                print_warn(f"Nodes file not found: {nodes_file}")
                result["status"] = "error"
                result["error"] = f"Nodes file not found - regenerate dataset"
                return result

            # Load edges from CSV
            if edges_file and edges_file.exists():
                _load_memgraph_edges_csv(session, edges_file)

            # M1: Load timeseries chunks as graph nodes
            if scenario == "M1" and chunks_file and chunks_file.exists():
                _load_memgraph_chunks_csv(session, chunks_file)

        result["load_time_s"] = time.time() - load_start
        result["load_resources"] = load_monitor.stop()
        if "samples" in result["load_resources"]:
            del result["load_resources"]["samples"]

        print_ok(f"Data loaded in {result['load_time_s']:.1f}s "
                 f"(peak RAM: {result['load_resources']['mem_mb']['max']:.0f}MB, "
                 f"avg CPU: {result['load_resources']['cpu_pct']['avg']:.1f}%)")

        # Reset memory.peak after ingestion to measure query impact only
        cgroup_path = get_container_cgroup_path(container_name)
        if cgroup_path:
            reset_memory_peak(cgroup_path)

    except LoadingStalled as e:
        load_monitor.stop()
        print_err(f"Memgraph loading STALLED (memory pressure): {e}")
        dump_container_debug(container_name)
        result["status"] = "stalled"
        result["error"] = str(e)
        result["error_type"] = "memory_pressure"
        driver.close()
        return result

    except LoadingTimeout as e:
        load_monitor.stop()
        print_err(f"Memgraph loading TIMEOUT: {e}")
        dump_container_debug(container_name)
        result["status"] = "timeout"
        result["error"] = str(e)
        result["error_type"] = "timeout"
        driver.close()
        return result

    except Exception as e:
        load_monitor.stop()
        print_err(f"Memgraph load error: {e}")
        dump_container_debug(container_name)
        result["status"] = "error"
        result["error"] = str(e)
        driver.close()
        return result

    # Define executor for Memgraph queries
    def mg_execute(query: str) -> int:
        with driver.session() as session:
            records = list(session.run(query))
            return len(records)

    def mg_execute_raw(query: str) -> List:
        """Execute and return raw records for hybrid queries."""
        with driver.session() as session:
            return list(session.run(query))

    # For M2: Connect to TimescaleDB for hybrid queries
    ts_conn = None
    ts_container = "btb_timescaledb"
    if scenario == "M2":
        try:
            from basetype_benchmark.loaders.postgres.load import get_connection
            print_info("Connecting to TimescaleDB for hybrid queries...")

            # Ensure timeseries data is loaded (idempotent)
            if not _ensure_timescaledb_timeseries(export_dir, scenario):
                print_warn("TimescaleDB timeseries not available - Q6 will fail")

            ts_conn = get_connection()
            # Reset memory.peak on TimescaleDB container too
            ts_cgroup = get_container_cgroup_path(ts_container)
            if ts_cgroup:
                reset_memory_peak(ts_cgroup)
        except Exception as e:
            print_warn(f"Failed to connect to TimescaleDB: {e}")

    # Extract dataset info for query parameterization
    dataset_info = extract_dataset_info(export_dir, scenario)
    print_info(f"Dataset info: {len(dataset_info['meters'])} meters, "
               f"{len(dataset_info['equipment'])} equipment, "
               f"{len(dataset_info['spaces'])} spaces")

    # Execute queries with variants
    queries_to_run = QUERIES_BY_SCENARIO.get(scenario, [])
    total_queries = len(queries_to_run)
    query_start_time = time.time()
    errors_count = 0

    # Snapshot before queries (for CPU delta calculation)
    metrics_before_graph = CGroupMetricsSnapshot(container_name)
    metrics_before_ts = CGroupMetricsSnapshot(ts_container) if scenario == "M2" else None

    print(f"\n    {BOLD}Running {total_queries} queries...{RESET}")

    for qi, query_id in enumerate(queries_to_run):
        query_type = HYBRID_QUERY_TYPE.get(query_id, "graph_only")

        # M2 hybrid execution for timeseries queries
        if scenario == "M2" and ts_conn and query_type in ("ts_direct", "hybrid"):
            query_result = run_hybrid_query(
                query_id=query_id,
                scenario=scenario,
                graph_execute_raw=mg_execute_raw,
                ts_conn=ts_conn,
                container_name=container_name,
                ts_container=ts_container,
                n_warmup=n_warmup,
                n_runs=n_runs,
                profile=profile,
                dataset_info=dataset_info
            )
        else:
            # M1 or M2 graph-only queries
            query_result = run_query_with_variants(
                query_id=query_id,
                scenario=scenario,
                execute_fn=mg_execute,
                container_name=container_name,
                n_warmup=n_warmup,
                n_runs=n_runs,
                profile=profile,
                dataset_info=dataset_info
            )
            query_type = "graph"

        if query_result:
            result["queries"][query_id] = query_result
            print_query_result(query_id, query_result, query_type)
        else:
            errors_count += 1
            print(f"    {RED}✗ {query_id}: FAILED{RESET}")

    # Snapshot after queries
    metrics_after_graph = CGroupMetricsSnapshot(container_name)
    query_metrics = CGroupMetricsSnapshot.compute_delta(metrics_before_graph, metrics_after_graph)

    # For M2, also capture TimescaleDB metrics
    if scenario == "M2" and metrics_before_ts:
        metrics_after_ts = CGroupMetricsSnapshot(ts_container)
        ts_metrics = CGroupMetricsSnapshot.compute_delta(metrics_before_ts, metrics_after_ts)
        query_metrics["ts_memory_peak_mb"] = ts_metrics["memory_peak_mb"]
        query_metrics["ts_cpu_time_sec"] = ts_metrics["cpu_time_sec"]
        query_metrics["total_memory_peak_mb"] = query_metrics["memory_peak_mb"] + ts_metrics["memory_peak_mb"]
        query_metrics["total_cpu_time_sec"] = query_metrics["cpu_time_sec"] + ts_metrics["cpu_time_sec"]

    # Store query phase metrics
    result["query_metrics"] = query_metrics

    # Total elapsed time
    total_elapsed = time.time() - query_start_time
    result["query_elapsed_s"] = total_elapsed

    if errors_count > 0:
        print_warn(f"{errors_count} query errors")

    # Print summary table
    print_benchmark_summary(scenario, result)

    result["status"] = "completed"
    driver.close()
    if ts_conn:
        ts_conn.close()

    return result


def _run_oxigraph_benchmark(scenario: str, export_dir: Path, result: Dict,
                            n_warmup: int = N_WARMUP, n_runs: int = N_RUNS,
                            profile: str = "small") -> Dict:
    """Run Oxigraph benchmark (O1 or O2).

    V2 format uses N-Triples instead of JSON-LD:
    - O1: graph.nt + chunks.nt + aggregates.nt (all timeseries in RDF)
    - O2: graph.nt + TimescaleDB for timeseries
    """
    from basetype_benchmark.loaders.oxigraph.load import (
        wait_for_oxigraph, clear_store, load_ntriples, load_ntriples_streaming, count_triples
    )
    import requests

    container_name = "btb_oxigraph"
    endpoint = "http://localhost:7878"

    print_info("Connecting to Oxigraph...")
    wait_for_oxigraph(endpoint)

    try:
        # Get V2 file paths for this scenario
        files = get_scenario_files(export_dir, scenario)
        print_info(f"Export dir: {export_dir}")
        print_info(f"Files to load:")
        for key, path in files.items():
            exists = "OK" if path.exists() else "MISSING"
            print(f"          - {key}: {path.name} [{exists}]")

        # Clear and load with resource monitoring
        print_info("Clearing store...")
        clear_store(endpoint)

        print_info("Loading data...")
        load_monitor = ResourceMonitor(container_name, interval_s=1.0)
        load_monitor.start()
        load_start = time.time()

        # V2 format: N-Triples files
        graph_file = files.get("graph")
        if not graph_file or not graph_file.exists():
            # Fallback: check for V1 JSON-LD format
            jsonld_file = export_dir / "graph.jsonld"
            if jsonld_file.exists():
                from basetype_benchmark.loaders.oxigraph.load import load_jsonld
                print_info("Using legacy JSON-LD format...")
                load_jsonld(endpoint, jsonld_file)
            else:
                load_monitor.stop()
                print_warn("graph.nt not found - need to regenerate dataset")
                result["status"] = "error"
                result["error"] = "graph.nt not found - regenerate dataset with V2 exporter"
                return result
        else:
            # V2: Load N-Triples (use streaming for large files > 100MB)
            file_size_mb = graph_file.stat().st_size / (1024 * 1024)
            if file_size_mb > 100:
                print_info(f"Loading graph.nt ({file_size_mb:.1f} MB) with streaming...")
                load_ntriples_streaming(endpoint, graph_file)
            else:
                load_ntriples(endpoint, graph_file)

            # O1 scenario: also load chunks and aggregates
            if scenario == "O1":
                chunks_file = files.get("chunks")
                if chunks_file and chunks_file.exists():
                    print_info("Loading chunks.nt...")
                    chunks_size_mb = chunks_file.stat().st_size / (1024 * 1024)
                    if chunks_size_mb > 100:
                        load_ntriples_streaming(endpoint, chunks_file)
                    else:
                        load_ntriples(endpoint, chunks_file)

                aggregates_file = files.get("aggregates")
                if aggregates_file and aggregates_file.exists():
                    print_info("Loading aggregates.nt...")
                    load_ntriples(endpoint, aggregates_file)

        result["load_time_s"] = time.time() - load_start
        result["load_resources"] = load_monitor.stop()
        if "samples" in result["load_resources"]:
            del result["load_resources"]["samples"]

        triples = count_triples(endpoint)
        print_ok(f"Data loaded in {result['load_time_s']:.1f}s ({triples} triples) "
                 f"(peak RAM: {result['load_resources']['mem_mb']['max']:.0f}MB, "
                 f"avg CPU: {result['load_resources']['cpu_pct']['avg']:.1f}%)")

        # Reset memory.peak after ingestion to measure query impact only
        cgroup_path = get_container_cgroup_path(container_name)
        if cgroup_path:
            reset_memory_peak(cgroup_path)

        # Define executor for SPARQL queries
        def sparql_execute(query: str) -> int:
            resp = requests.get(
                f"{endpoint}/query",
                params={"query": query},
                headers={"Accept": "application/sparql-results+json"},
                timeout=60
            )
            if resp.status_code == 200:
                data = resp.json()
                return len(data.get("results", {}).get("bindings", []))
            return 0

        def sparql_execute_raw(query: str) -> List:
            """Execute and return raw bindings for hybrid queries."""
            resp = requests.get(
                f"{endpoint}/query",
                params={"query": query},
                headers={"Accept": "application/sparql-results+json"},
                timeout=60
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("results", {}).get("bindings", [])
            return []

        # For O2: Connect to TimescaleDB for hybrid queries
        ts_conn = None
        ts_container = "btb_timescaledb"
        if scenario == "O2":
            try:
                from basetype_benchmark.loaders.postgres.load import get_connection
                print_info("Connecting to TimescaleDB for hybrid queries...")

                # Ensure timeseries data is loaded (idempotent)
                if not _ensure_timescaledb_timeseries(export_dir, scenario):
                    print_warn("TimescaleDB timeseries not available - Q6 will fail")

                ts_conn = get_connection()
                # Reset memory.peak on TimescaleDB container too
                ts_cgroup = get_container_cgroup_path(ts_container)
                if ts_cgroup:
                    reset_memory_peak(ts_cgroup)
            except Exception as e:
                print_warn(f"Failed to connect to TimescaleDB: {e}")

        # Extract dataset info for query parameterization
        dataset_info = extract_dataset_info(export_dir, scenario)
        print_info(f"Dataset info: {len(dataset_info['meters'])} meters, "
                   f"{len(dataset_info['equipment'])} equipment, "
                   f"{len(dataset_info['spaces'])} spaces")

        # Execute queries with variants
        queries_to_run = QUERIES_BY_SCENARIO.get(scenario, [])
        total_queries = len(queries_to_run)
        query_start_time = time.time()
        errors_count = 0

        # Snapshot before queries (for CPU delta calculation)
        metrics_before_graph = CGroupMetricsSnapshot(container_name)
        metrics_before_ts = CGroupMetricsSnapshot(ts_container) if scenario == "O2" else None

        print(f"\n    {BOLD}Running {total_queries} queries...{RESET}")

        for qi, query_id in enumerate(queries_to_run):
            query_type = HYBRID_QUERY_TYPE.get(query_id, "graph_only")

            # O2 hybrid execution for timeseries queries
            if scenario == "O2" and ts_conn and query_type in ("ts_direct", "hybrid"):
                query_result = run_hybrid_query(
                    query_id=query_id,
                    scenario=scenario,
                    graph_execute_raw=sparql_execute_raw,
                    ts_conn=ts_conn,
                    container_name=container_name,
                    ts_container=ts_container,
                    n_warmup=n_warmup,
                    n_runs=n_runs,
                    profile=profile,
                    dataset_info=dataset_info
                )
            else:
                # O1 or O2 graph-only queries
                query_result = run_query_with_variants(
                    query_id=query_id,
                    scenario=scenario,
                    execute_fn=sparql_execute,
                    container_name=container_name,
                    n_warmup=n_warmup,
                    n_runs=n_runs,
                    profile=profile,
                    dataset_info=dataset_info
                )
                query_type = "graph"

            if query_result:
                result["queries"][query_id] = query_result
                print_query_result(query_id, query_result, query_type)
            else:
                errors_count += 1
                print(f"    {RED}✗ {query_id}: FAILED{RESET}")

        # Snapshot after queries
        metrics_after_graph = CGroupMetricsSnapshot(container_name)
        query_metrics = CGroupMetricsSnapshot.compute_delta(metrics_before_graph, metrics_after_graph)

        # For O2, also capture TimescaleDB metrics
        if scenario == "O2" and metrics_before_ts:
            metrics_after_ts = CGroupMetricsSnapshot(ts_container)
            ts_metrics = CGroupMetricsSnapshot.compute_delta(metrics_before_ts, metrics_after_ts)
            query_metrics["ts_memory_peak_mb"] = ts_metrics["memory_peak_mb"]
            query_metrics["ts_cpu_time_sec"] = ts_metrics["cpu_time_sec"]
            query_metrics["total_memory_peak_mb"] = query_metrics["memory_peak_mb"] + ts_metrics["memory_peak_mb"]
            query_metrics["total_cpu_time_sec"] = query_metrics["cpu_time_sec"] + ts_metrics["cpu_time_sec"]

        # Store query phase metrics
        result["query_metrics"] = query_metrics

        # Total elapsed time
        total_elapsed = time.time() - query_start_time
        result["query_elapsed_s"] = total_elapsed

        if errors_count > 0:
            print_warn(f"{errors_count} query errors")

        # Print summary table
        print_benchmark_summary(scenario, result)

        result["status"] = "completed"

        if ts_conn:
            ts_conn.close()

    except Exception as e:
        print_err(f"Oxigraph error: {e}")
        result["status"] = "error"
        result["error"] = str(e)

    return result


# =============================================================================
# WORKFLOW: BENCHMARK (RAM-Gradient Protocol)
# =============================================================================

def run_ram_gradient_benchmark(scenario: str, export_dir: Path, profile: str, results_dir: Path) -> Dict:
    """Run RAM-Gradient benchmark for a scenario.

    Protocol:
    - P1/P2: Start from min RAM, iterate up until performance plateau
    - M/O: Start from min RAM, escalate on OOM, continue to plateau

    Args:
        scenario: P1, P2, M1, M2, O1, O2
        export_dir: Path to exported dataset
        profile: Profile name (e.g., 'small-2d') for protocol config and RAM strategy
        results_dir: Directory for results

    Returns dict with results per RAM level.
    """
    # Extract scale from profile (e.g., 'small-2d' -> 'small')
    scale = profile.split("-")[0] if "-" in profile else profile
    strategy = get_ram_strategy(scenario, scale)
    containers = SCENARIOS[scenario]["containers"]
    main_container = f"btb_{containers[0]}"

    ram_results = {}
    prev_p95 = float('inf')
    current_ram = strategy["start_ram"]

    print_info(f"RAM Strategy: {strategy['description']}")
    print_info(f"Starting RAM: {current_ram}GB, Max: {strategy['max_ram']}GB")

    while current_ram <= strategy["max_ram"]:
        print(f"\n{BOLD}--- Testing {scenario} @ {current_ram}GB RAM ---{RESET}")

        # Start containers with RAM limit
        if not start_containers_with_ram(containers, current_ram):
            ram_results[current_ram] = {"status": "container_failed"}
            current_ram = _next_ram_level(current_ram)
            continue

        try:
            # Run benchmark at this RAM level
            bench_result = run_scenario_benchmark(scenario, export_dir, profile)

            # Check for OOM (kernel kill)
            if check_container_oom(main_container):
                print_warn(f"OOM detected at {current_ram}GB")
                ram_results[current_ram] = {"status": "oom", "ram_gb": current_ram}
                current_ram = _next_ram_level(current_ram)
                stop_all_containers()
                continue

            # Check for stalled/timeout (memory pressure without OOM kill)
            if bench_result["status"] in ("stalled", "timeout"):
                print_warn(f"Loading {bench_result['status']} at {current_ram}GB - likely insufficient RAM")
                ram_results[current_ram] = {
                    "status": bench_result["status"],
                    "error": bench_result.get("error"),
                    "error_type": bench_result.get("error_type", "memory_pressure"),
                    "ram_gb": current_ram
                }
                # Escalate to next RAM level
                current_ram = _next_ram_level(current_ram)
                stop_all_containers()
                continue

            if bench_result["status"] != "completed":
                print_err(f"Benchmark failed: {bench_result.get('error', 'unknown')}")
                ram_results[current_ram] = {
                    "status": "error",
                    "error": bench_result.get("error"),
                    "ram_gb": current_ram
                }
                # For M/O, connection errors might indicate memory issues
                if scenario.startswith(("M", "O")):
                    current_ram = _next_ram_level(current_ram)
                    stop_all_containers()
                    continue
                break

            # Collect resource metrics
            resources = get_container_stats(main_container)
            bench_result["resources"] = resources
            bench_result["ram_gb"] = current_ram

            # Calculate avg p95
            all_p95 = [q["stats"]["p95"] for q in bench_result["queries"].values()
                       if q.get("stats") and q["stats"].get("p95")]
            avg_p95 = sum(all_p95) / len(all_p95) if all_p95 else 0

            ram_results[current_ram] = bench_result
            print_ok(f"{scenario} @ {current_ram}GB: avg p95={avg_p95:.1f}ms")

            # Check for plateau
            if is_performance_plateau(prev_p95, avg_p95, PERF_PLATEAU_THRESHOLD):
                print_info(f"Performance plateau reached at {current_ram}GB (improvement < {PERF_PLATEAU_THRESHOLD}%)")
                break

            prev_p95 = avg_p95

        except Exception as e:
            print_err(f"Error at {current_ram}GB: {e}")
            ram_results[current_ram] = {"status": "error", "error": str(e), "ram_gb": current_ram}
            import traceback
            traceback.print_exc()

        finally:
            stop_all_containers()

        current_ram = _next_ram_level(current_ram)

    return ram_results


def _next_ram_level(current: int) -> int:
    """Get next RAM level to test."""
    for level in RAM_LEVELS:
        if level > current:
            return level
    return current * 2  # Beyond defined levels, double


def get_master_dataset() -> Optional[Tuple[str, Path]]:
    """Find the largest available dataset (master for extraction).

    Returns:
        Tuple (profile_name, export_path) or None
    """
    available = get_available_profiles()
    if not available:
        return None

    # Order by scale then duration (largest first)
    scale_order = {"large": 2, "medium": 1, "small": 0}
    duration_order = {"1y": 4, "6m": 3, "1m": 2, "1w": 1, "2d": 0}

    def score(profile):
        scale = get_scale_from_profile(profile)
        duration = get_duration_from_profile(profile)
        return (scale_order.get(scale, 0), duration_order.get(duration, 0))

    sorted_profiles = sorted(available, key=score, reverse=True)
    master = sorted_profiles[0]
    export_dir = Path("src/basetype_benchmark/dataset/exports") / f"{master}_seed42"

    return master, export_dir


def get_extractable_configs(master_profile: str) -> Dict:
    """Get all extractable configurations from master dataset.

    Returns:
        Dict with scales, durations, and full profile list
    """
    from basetype_benchmark.dataset.subset_extractor import (
        get_available_scales, get_available_durations, get_extractable_profiles
    )

    scales = get_available_scales(master_profile)
    durations = get_available_durations(master_profile)
    profiles = [master_profile] + get_extractable_profiles(master_profile)

    return {
        "scales": scales,
        "durations": durations,
        "profiles": profiles,
        "master": master_profile
    }


def ensure_dataset_extracted(master_dir: Path, target_profile: str) -> Path:
    """Ensure target profile is extracted from master, return path.

    Args:
        master_dir: Path to master dataset
        target_profile: Target profile to extract (e.g., 'small-1m')

    Returns:
        Path to extracted dataset
    """
    from basetype_benchmark.dataset.subset_extractor import SubsetExtractor, can_extract

    # Parse master profile from directory name
    master_name = master_dir.name.rsplit("_seed", 1)[0]

    # If target is same as master, return master dir
    if target_profile == master_name:
        return master_dir

    # Check if already extracted
    target_dir = master_dir.parent / f"{target_profile}_seed42"
    if target_dir.exists() and (target_dir / "nodes.csv").exists():
        print_info(f"Using existing extraction: {target_profile}")
        return target_dir

    # Extract
    if not can_extract(master_name, target_profile):
        raise ValueError(f"Cannot extract {target_profile} from {master_name}")

    print_info(f"Extracting {target_profile} from {master_name}...")
    extractor = SubsetExtractor(master_dir)
    return extractor.extract(target_profile)


# =============================================================================
# ON-DEMAND EXPORT WORKFLOW (Disk-Efficient)
# =============================================================================

def run_scenario_with_ondemand_export(
    scenario: str,
    export_dir: Path,
    profile: str,
    ram_gb: int = 8,
    cleanup_after: bool = True,
) -> Dict:
    """Run benchmark with on-demand export and cleanup.

    This workflow minimizes disk usage by:
    1. Exporting timeseries.csv ONCE (shared by P1/P2/M2/O2)
    2. Exporting scenario-specific files just before loading
    3. Running the benchmark
    4. Cleaning up scenario files after (optional)

    For gros datasets (e.g., medium-1w with 8GB parquet), this keeps
    disk usage around 10-15GB instead of 40GB+.

    Args:
        scenario: P1, P2, M1, M2, O1, O2
        export_dir: Base export directory (e.g., exports/small-1w_seed42)
        profile: Profile name for protocol config
        ram_gb: RAM limit for containers
        cleanup_after: If True, delete scenario files after benchmark

    Returns:
        Benchmark result dict
    """
    from basetype_benchmark.dataset.dataset_manager import DatasetManager
    from basetype_benchmark.dataset import exporter_v2

    parquet_dir = export_dir / "parquet"
    scenario_upper = scenario.upper()
    scenario_lower = scenario.lower()
    scenario_dir = export_dir / scenario_lower

    # Step 1: Export shared timeseries.csv if needed (for P1/P2/M2/O2)
    needs_timeseries = scenario_upper in ("P1", "P2", "M2", "O2")
    shared_ts_path = export_dir / "timeseries.csv"

    if needs_timeseries and not shared_ts_path.exists():
        print_info("Exporting shared timeseries.csv...")
        exporter_v2.export_timeseries_csv_shared(parquet_dir, shared_ts_path)

    # Step 2: Export scenario-specific files on-demand
    print_info(f"Exporting {scenario_upper} format on-demand...")
    manager = DatasetManager()

    # Use the scenario export from DatasetManager
    try:
        # Get profile from export_dir name
        profile_name = export_dir.name.rsplit("_seed", 1)[0]
        seed = 42
        manager.export_scenario_only(profile_name, scenario, seed)
    except Exception as e:
        print_err(f"On-demand export failed: {e}")
        raise

    # For scenarios that need shared timeseries, symlink/copy it
    if needs_timeseries and shared_ts_path.exists():
        if scenario_upper in ("P1", "P2"):
            ts_filename = "pg_timeseries.csv"
        else:
            ts_filename = "timeseries.csv"
        exporter_v2.symlink_or_copy_timeseries(shared_ts_path, scenario_dir, ts_filename)

    # Step 3: Start containers and run benchmark
    if not start_containers_with_ram(SCENARIOS[scenario_upper]["containers"], ram_gb):
        return {"status": "container_failed", "error": "Failed to start containers"}

    try:
        result = run_scenario_benchmark(scenario_upper, export_dir, profile)
        result["ram_gb"] = ram_gb
        result["ondemand_export"] = True
    finally:
        stop_all_containers()

    # Step 4: Cleanup scenario files (optional)
    if cleanup_after:
        print_info(f"Cleaning up {scenario_upper} files...")
        # Keep shared timeseries.csv, delete scenario-specific files
        manager.prune_scenario(profile_name, scenario, seed, keep_shared_timeseries=True)

    return result


def run_all_scenarios_ondemand(
    export_dir: Path,
    profile: str,
    ram_gb: int = 8,
    scenarios: List[str] = None,
    cleanup_between: bool = True,
) -> Dict[str, Dict]:
    """Run all scenarios with on-demand export workflow.

    Optimal order for disk efficiency:
    1. P1, P2, M2, O2 (share timeseries.csv)
    2. M1, O1 (need chunks, different format)

    Args:
        export_dir: Base export directory
        profile: Profile name
        ram_gb: RAM limit
        scenarios: List of scenarios to run (default: all in optimal order)
        cleanup_between: If True, cleanup each scenario after running

    Returns:
        Dict of scenario -> result
    """
    if scenarios is None:
        # Optimal order: shared timeseries first, then chunks
        scenarios = ["P1", "P2", "M2", "O2", "M1", "O1"]

    results = {}

    for scenario in scenarios:
        print_header(f"{scenario} ({SCENARIOS[scenario]['name']})")

        try:
            result = run_scenario_with_ondemand_export(
                scenario=scenario,
                export_dir=export_dir,
                profile=profile,
                ram_gb=ram_gb,
                cleanup_after=cleanup_between,
            )
            results[scenario] = result
        except Exception as e:
            print_err(f"Scenario {scenario} failed: {e}")
            results[scenario] = {"status": "error", "error": str(e)}

    # Final cleanup: remove shared timeseries.csv
    if cleanup_between:
        shared_ts_path = export_dir / "timeseries.csv"
        if shared_ts_path.exists():
            print_info("Cleaning up shared timeseries.csv...")
            shared_ts_path.unlink()

    return results


def select_ram_levels() -> List[int]:
    """Interactive RAM level selection."""
    print_header("SELECT RAM LEVELS")
    print("Choose which RAM levels to test:\n")

    print(f"  A. {BOLD}All levels{RESET} ({RAM_LEVELS} GB)")
    print(f"  D. {BOLD}Default gradient{RESET} (4, 8, 16, 32 GB)")
    print(f"  S. {BOLD}Select specific levels{RESET}")
    print(f"  C. {BOLD}Custom single level{RESET}\n")
    print(f"  0. Back\n")

    choice = prompt("Select", "D").upper()

    if choice == "0":
        return []
    elif choice == "A":
        return RAM_LEVELS.copy()
    elif choice == "D":
        return [4, 8, 16, 32]
    elif choice == "C":
        try:
            level = int(prompt("RAM level (GB)", "8"))
            return [level]
        except ValueError:
            print_err("Invalid RAM level")
            return []
    elif choice == "S":
        print("\nAvailable levels:", RAM_LEVELS)
        levels_str = prompt("Enter levels separated by commas", "4,8,16")
        try:
            return [int(x.strip()) for x in levels_str.split(",")]
        except ValueError:
            print_err("Invalid input")
            return []

    return RAM_LEVELS.copy()


def workflow_benchmark():
    """Benchmark execution workflow with full multi-criteria selection."""
    print_header("BENCHMARK EXECUTION")

    # Check for master dataset
    master_info = get_master_dataset()
    if not master_info:
        print_warn("No datasets available. Generate one first (option 2).")
        input("\nPress Enter...")
        return

    master_profile, master_dir = master_info
    configs = get_extractable_configs(master_profile)

    print(f"Master dataset: {BOLD}{master_profile}{RESET}")
    print(f"Available scales: {', '.join(configs['scales'])}")
    print(f"Available durations: {', '.join(configs['durations'])}")
    print(f"Total configurations: {len(configs['profiles'])}\n")

    # Check for resumable campaigns
    resumable = _find_resumable_campaigns()

    # Mode selection
    print(f"  {BOLD}F{RESET}. FULL CAMPAIGN - All configurations automatically")
    print(f"     {DIM}{len(configs['profiles'])} profiles x 6 scenarios x {len(RAM_LEVELS)} RAM levels = {len(configs['profiles']) * 6 * len(RAM_LEVELS)} runs{RESET}")
    print(f"  {BOLD}S{RESET}. SELECT - Choose profiles, scenarios, RAM levels")
    print(f"  {BOLD}Q{RESET}. QUICK TEST - Single profile, all scenarios, single RAM")
    if resumable:
        print(f"  {BOLD}R{RESET}. RESUME - Continue interrupted campaign ({len(resumable)} found)")
    print(f"\n  0. Back\n")

    mode = prompt("Select mode", "S").upper()

    if mode == "0":
        return
    elif mode == "F":
        _run_full_benchmark(master_dir, configs)
    elif mode == "Q":
        _run_quick_benchmark(master_dir, configs)
    elif mode == "R" and resumable:
        _run_resume_benchmark(resumable)
    else:
        _run_selective_benchmark(master_dir, configs)


def _run_full_benchmark(master_dir: Path, configs: Dict):
    """Run FULL benchmark: all profiles x all engines x RAM gradient."""
    print_header("FULL BENCHMARK MODE")

    total_configs = len(configs['profiles']) * len(SCENARIOS) * len(RAM_LEVELS)
    print(f"{YELLOW}WARNING: This will run {total_configs} benchmark configurations!{RESET}")
    print(f"\nProfiles: {len(configs['profiles'])}")
    print(f"Engines: {len(SCENARIOS)} (P1, P2, M1, M2, O1, O2)")
    print(f"RAM levels: {len(RAM_LEVELS)} ({RAM_LEVELS})")
    print(f"\nEstimated time: Several hours to days depending on hardware\n")

    if not prompt_yes_no("Are you SURE you want to run FULL benchmark?", False):
        return

    # Create results directory
    results_dir = Path("benchmark_results") / f"full_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results_dir.mkdir(parents=True, exist_ok=True)

    all_results = {"profiles": {}}
    engines = list(SCENARIOS.keys())

    for i, profile in enumerate(configs['profiles'], 1):
        print_header(f"PROFILE {i}/{len(configs['profiles'])}: {profile}")

        try:
            export_dir = ensure_dataset_extracted(master_dir, profile)
            scale = get_scale_from_profile(profile)

            profile_results = {}
            for engine in engines:
                print(f"\n{BOLD}Engine: {engine} ({SCENARIOS[engine]['name']}){RESET}")
                ram_results = run_ram_gradient_benchmark(engine, export_dir, profile, results_dir)
                profile_results[engine] = ram_results

                # Save intermediate
                with open(results_dir / f"{profile}_{engine}.json", 'w') as f:
                    json.dump(ram_results, f, indent=2, default=str)

            all_results["profiles"][profile] = profile_results

        except Exception as e:
            print_err(f"Failed on {profile}: {e}")
            all_results["profiles"][profile] = {"error": str(e)}

    # Save final summary
    _save_full_results(results_dir, all_results, configs)
    print_header("FULL BENCHMARK COMPLETE")
    print(f"Results saved to: {results_dir}")
    input("\nPress Enter...")


def _run_quick_benchmark(master_dir: Path, configs: Dict):
    """Run QUICK benchmark: single profile, all engines, single RAM."""
    print_header("QUICK BENCHMARK MODE")

    # Select profile
    print("Select profile:\n")
    for i, profile in enumerate(configs['profiles'], 1):
        size = SIZE_ESTIMATES.get(profile, "?")
        marker = " (master)" if profile == configs['master'] else ""
        print(f"  {i}. {profile} (~{size} GB){marker}")
    print(f"\n  0. Back")

    choice = prompt("\nProfile", "1")
    if choice == "0":
        return

    try:
        profile = configs['profiles'][int(choice) - 1]
    except (ValueError, IndexError):
        print_err("Invalid choice")
        return

    # Select RAM level
    ram_level = int(prompt("RAM level (GB)", "8"))

    # Ask about on-demand export mode
    estimated_size = SIZE_ESTIMATES.get(profile, 10)
    use_ondemand = False
    if estimated_size >= 2:  # Recommend for datasets >= 2GB
        print(f"\n{YELLOW}Disk-efficient mode available:{RESET}")
        print(f"  - Standard: Export all formats upfront (~{estimated_size * 4:.0f} GB disk)")
        print(f"  - On-demand: Export per scenario, cleanup after (~{estimated_size * 1.5:.0f} GB max)")
        use_ondemand = prompt_yes_no("Use disk-efficient on-demand mode?", True)

    # Confirm
    print_header("CONFIRM QUICK BENCHMARK")
    print(f"Profile: {profile}")
    print(f"Engines: ALL (P1, P2, M1, M2, O1, O2)")
    print(f"RAM: {ram_level} GB (fixed)")
    print(f"Mode: {'On-demand (disk-efficient)' if use_ondemand else 'Standard'}")

    if not prompt_yes_no("\nStart quick benchmark?"):
        return

    # Prepare dataset
    try:
        export_dir = ensure_dataset_extracted(master_dir, profile)
        scale = get_scale_from_profile(profile)
    except Exception as e:
        print_err(f"Dataset preparation failed: {e}")
        input("\nPress Enter...")
        return

    results_dir = Path("benchmark_results") / f"quick_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Run benchmarks
    if use_ondemand:
        # Use on-demand export workflow
        all_results = run_all_scenarios_ondemand(
            export_dir=export_dir,
            profile=profile,
            ram_gb=ram_level,
            scenarios=list(SCENARIOS.keys()),
            cleanup_between=True,
        )
        # Save individual results
        for engine, result in all_results.items():
            with open(results_dir / f"{engine}.json", 'w') as f:
                json.dump(result, f, indent=2, default=str)
    else:
        # Standard mode (all exports upfront)
        all_results = {}
        for engine in SCENARIOS.keys():
            print_header(f"{engine} ({SCENARIOS[engine]['name']})")

            if not start_containers_with_ram(SCENARIOS[engine]["containers"], ram_level):
                all_results[engine] = {"status": "container_failed"}
                continue

            try:
                result = run_scenario_benchmark(engine, export_dir, profile)
                result["ram_gb"] = ram_level
                all_results[engine] = result

                with open(results_dir / f"{engine}.json", 'w') as f:
                    json.dump(result, f, indent=2, default=str)
            finally:
                stop_all_containers()

    # Summary
    with open(results_dir / "summary.json", 'w') as f:
        json.dump({
            "mode": "quick",
            "profile": profile,
            "ram_gb": ram_level,
            "ondemand": use_ondemand,
            "results": all_results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, default=str)

    _print_quick_summary(all_results)
    print(f"\n{DIM}Results saved to: {results_dir}{RESET}")
    input("\nPress Enter...")


def _run_selective_benchmark(master_dir: Path, configs: Dict):
    """Run SELECTIVE benchmark: user chooses all parameters."""
    print_header("SELECTIVE BENCHMARK MODE")

    # Step 1: Select scales
    print(f"{BOLD}Step 1: Select scales{RESET}\n")
    print(f"  A. All ({', '.join(configs['scales'])})")
    for i, scale in enumerate(configs['scales'], 1):
        print(f"  {i}. {scale} only")
    print(f"\n  0. Back")

    choice = prompt("Scales", "A").upper()
    if choice == "0":
        return
    elif choice == "A":
        selected_scales = configs['scales']
    else:
        try:
            selected_scales = [configs['scales'][int(choice) - 1]]
        except (ValueError, IndexError):
            print_err("Invalid choice")
            return

    # Step 2: Select durations
    print_header("SELECT DURATIONS")
    print(f"{BOLD}Step 2: Select time windows{RESET}\n")
    print(f"  A. All ({', '.join(configs['durations'])})")
    for i, duration in enumerate(configs['durations'], 1):
        print(f"  {i}. {duration} only")
    print(f"\n  0. Back")

    choice = prompt("Durations", "A").upper()
    if choice == "0":
        return
    elif choice == "A":
        selected_durations = configs['durations']
    else:
        try:
            selected_durations = [configs['durations'][int(choice) - 1]]
        except (ValueError, IndexError):
            print_err("Invalid choice")
            return

    # Build profile list
    selected_profiles = []
    for scale in selected_scales:
        for duration in selected_durations:
            profile = f"{scale}-{duration}"
            if profile in configs['profiles']:
                selected_profiles.append(profile)

    if not selected_profiles:
        print_err("No valid profiles selected")
        return

    # Step 3: Select engines
    engines = select_engines()
    if not engines:
        return

    # Step 4: Select RAM levels
    ram_levels = select_ram_levels()
    if not ram_levels:
        return

    # Confirm
    print_header("CONFIRM SELECTIVE BENCHMARK")
    print(f"Profiles: {', '.join(selected_profiles)}")
    print(f"Engines: {', '.join(engines)}")
    print(f"RAM levels: {ram_levels} GB")

    total = len(selected_profiles) * len(engines) * len(ram_levels)
    print(f"\n{BOLD}Total configurations: {total}{RESET}")

    if not prompt_yes_no("\nStart benchmark?"):
        return

    # Run
    results_dir = Path("benchmark_results") / f"selective_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results_dir.mkdir(parents=True, exist_ok=True)

    all_results = {"profiles": {}}

    for profile in selected_profiles:
        print_header(f"PROFILE: {profile}")

        try:
            export_dir = ensure_dataset_extracted(master_dir, profile)
            scale = get_scale_from_profile(profile)

            profile_results = {}
            for engine in engines:
                print(f"\n{BOLD}Engine: {engine}{RESET}")

                # Custom RAM gradient with selected levels
                ram_results = _run_custom_ram_gradient(
                    engine, export_dir, profile, ram_levels, results_dir
                )
                profile_results[engine] = ram_results

                with open(results_dir / f"{profile}_{engine}.json", 'w') as f:
                    json.dump(ram_results, f, indent=2, default=str)

            all_results["profiles"][profile] = profile_results

        except Exception as e:
            print_err(f"Failed on {profile}: {e}")
            all_results["profiles"][profile] = {"error": str(e)}

    # Save summary
    with open(results_dir / "summary.json", 'w') as f:
        json.dump({
            "mode": "selective",
            "profiles": selected_profiles,
            "engines": engines,
            "ram_levels": ram_levels,
            "results": all_results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, default=str)

    print_header("SELECTIVE BENCHMARK COMPLETE")
    print(f"Results saved to: {results_dir}")
    input("\nPress Enter...")


def _find_resumable_campaigns() -> List[Dict]:
    """Find incomplete benchmark campaigns that can be resumed.

    Returns:
        List of campaign info dicts with path, mode, completed, total
    """
    results_base = Path("benchmark_results")
    if not results_base.exists():
        return []

    resumable = []

    for campaign_dir in sorted(results_base.iterdir(), reverse=True):
        if not campaign_dir.is_dir():
            continue

        summary_file = campaign_dir / "summary.json"
        if not summary_file.exists():
            # Check for partial results (individual JSON files)
            json_files = list(campaign_dir.glob("*.json"))
            if json_files:
                # Incomplete campaign without summary
                resumable.append({
                    "path": campaign_dir,
                    "mode": campaign_dir.name.split("_")[0],  # full, selective, quick
                    "completed_files": len(json_files),
                    "status": "incomplete",
                    "timestamp": campaign_dir.name
                })
        else:
            # Has summary - check if complete
            try:
                with open(summary_file) as f:
                    summary = json.load(f)

                # Check for missing results
                if "results" in summary and "profiles" in summary.get("results", {}):
                    profiles = summary.get("profiles", [])
                    engines = summary.get("engines", list(SCENARIOS.keys()))
                    ram_levels = summary.get("ram_levels", RAM_LEVELS)

                    expected = len(profiles) * len(engines)
                    actual = len(list(campaign_dir.glob("*_*.json"))) - 1  # -1 for summary

                    if actual < expected:
                        resumable.append({
                            "path": campaign_dir,
                            "mode": summary.get("mode", "unknown"),
                            "profiles": profiles,
                            "engines": engines,
                            "ram_levels": ram_levels,
                            "completed": actual,
                            "total": expected,
                            "status": "partial",
                            "timestamp": summary.get("timestamp", "")
                        })
            except (json.JSONDecodeError, KeyError):
                pass

    return resumable[:5]  # Return last 5 resumable campaigns


def _run_resume_benchmark(resumable: List[Dict]):
    """Resume an interrupted benchmark campaign."""
    print_header("RESUME BENCHMARK")

    print("Found incomplete campaigns:\n")
    for i, campaign in enumerate(resumable, 1):
        path = campaign["path"]
        mode = campaign["mode"]
        status = campaign["status"]

        if status == "partial":
            progress = f"{campaign['completed']}/{campaign['total']} complete"
        else:
            progress = f"{campaign['completed_files']} files found"

        print(f"  {i}. {path.name}")
        print(f"     Mode: {mode}, Status: {status}, Progress: {progress}")

    print(f"\n  0. Back\n")

    choice = prompt("Select campaign to resume", "1")
    if choice == "0":
        return

    try:
        campaign = resumable[int(choice) - 1]
    except (ValueError, IndexError):
        print_err("Invalid choice")
        return

    campaign_dir = campaign["path"]

    # Detect what's already done
    completed = set()
    for json_file in campaign_dir.glob("*_*.json"):
        if json_file.name == "summary.json":
            continue
        # Parse filename: profile_engine.json
        parts = json_file.stem.rsplit("_", 1)
        if len(parts) == 2:
            completed.add((parts[0], parts[1]))  # (profile, engine)

    print(f"\nAlready completed: {len(completed)} configurations")

    # Load campaign config
    summary_file = campaign_dir / "summary.json"
    if summary_file.exists():
        with open(summary_file) as f:
            summary = json.load(f)
        profiles = summary.get("profiles", [])
        engines = summary.get("engines", list(SCENARIOS.keys()))
        ram_levels = summary.get("ram_levels", RAM_LEVELS)
    else:
        print_warn("No summary found, using defaults")
        profiles = []
        engines = list(SCENARIOS.keys())
        ram_levels = RAM_LEVELS

    # Find what's missing
    missing = []
    for profile in profiles:
        for engine in engines:
            if (profile, engine) not in completed:
                missing.append((profile, engine))

    if not missing:
        print_ok("Campaign is complete!")
        input("\nPress Enter...")
        return

    print(f"Remaining: {len(missing)} configurations")
    print(f"  Profiles: {set(p for p, e in missing)}")
    print(f"  Engines: {set(e for p, e in missing)}")

    if not prompt_yes_no("\nContinue campaign?"):
        return

    # Get master dataset
    master_info = get_master_dataset()
    if not master_info:
        print_err("No master dataset found")
        return

    master_profile, master_dir = master_info

    # Resume execution
    for profile, engine in missing:
        print_header(f"RESUMING: {profile} x {engine}")

        try:
            export_dir = ensure_dataset_extracted(master_dir, profile)

            ram_results = _run_custom_ram_gradient(
                engine, export_dir, profile, ram_levels, campaign_dir
            )

            with open(campaign_dir / f"{profile}_{engine}.json", 'w') as f:
                json.dump(ram_results, f, indent=2, default=str)

            print_ok(f"Completed: {profile} x {engine}")

        except Exception as e:
            print_err(f"Failed: {profile} x {engine}: {e}")

    # Update summary
    print_header("RESUME COMPLETE")
    print(f"Results in: {campaign_dir}")
    input("\nPress Enter...")


def _run_custom_ram_gradient(scenario: str, export_dir: Path, profile: str,
                             ram_levels: List[int], results_dir: Path) -> Dict:
    """Run benchmark with custom RAM levels (not auto-escalation).

    Args:
        scenario: P1, P2, M1, M2, O1, O2
        export_dir: Path to exported dataset
        profile: Profile name (e.g., 'small-2d') for protocol config
        ram_levels: List of RAM sizes to test (in GB)
        results_dir: Directory for results
    """
    containers = SCENARIOS[scenario]["containers"]
    main_container = f"btb_{containers[0]}"

    ram_results = {}

    for ram_gb in ram_levels:
        print(f"\n--- {scenario} @ {ram_gb}GB RAM ---")

        if not start_containers_with_ram(containers, ram_gb):
            ram_results[ram_gb] = {"status": "container_failed"}
            continue

        try:
            result = run_scenario_benchmark(scenario, export_dir, profile)

            if check_container_oom(main_container):
                print_warn(f"OOM at {ram_gb}GB")
                ram_results[ram_gb] = {"status": "oom", "ram_gb": ram_gb}
            else:
                result["ram_gb"] = ram_gb
                ram_results[ram_gb] = result

                if result["status"] == "completed":
                    queries = result.get("queries", {})
                    all_p95 = [q["stats"]["p95"] for q in queries.values()
                               if q.get("stats") and q["stats"].get("p95")]
                    avg_p95 = sum(all_p95) / len(all_p95) if all_p95 else 0
                    print_ok(f"{scenario} @ {ram_gb}GB: avg p95={avg_p95:.1f}ms")

        except Exception as e:
            print_err(f"Error at {ram_gb}GB: {e}")
            ram_results[ram_gb] = {"status": "error", "error": str(e)}

        finally:
            stop_all_containers()

    return ram_results


def _save_full_results(results_dir: Path, all_results: Dict, configs: Dict):
    """Save full benchmark results with summary."""
    with open(results_dir / "summary.json", 'w') as f:
        json.dump({
            "mode": "full",
            "master": configs["master"],
            "profiles": list(all_results["profiles"].keys()),
            "engines": list(SCENARIOS.keys()),
            "ram_levels": RAM_LEVELS,
            "results": all_results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, default=str)


def _print_quick_summary(results: Dict):
    """Print summary for quick benchmark."""
    print_header("QUICK BENCHMARK RESULTS")

    print(f"\n{'Engine':<15} {'Status':<12} {'Load(s)':<10} {'Avg p95(ms)':<12}")
    print("-" * 50)

    for engine, result in results.items():
        status = result.get("status", "?")
        load_time = result.get("load_time_s", 0)
        queries = result.get("queries", {})

        if status == "completed" and queries:
            all_p95 = [q["stats"]["p95"] for q in queries.values()
                       if q.get("stats") and q["stats"].get("p95")]
            avg_p95 = sum(all_p95) / len(all_p95) if all_p95 else 0
            print(f"{engine:<15} {status:<12} {load_time:<10.1f} {avg_p95:<12.1f}")
        else:
            print(f"{engine:<15} {status:<12} {'-':<10} {'-':<12}")


def _print_ram_gradient_summary(all_results: Dict, scale: str):
    """Print RAM-Gradient summary table."""
    print(f"\n{BOLD}RAM × Scenario Matrix (avg p95 in ms):{RESET}\n")

    # Header
    scenarios = list(all_results.keys())
    header = f"{'RAM(GB)':<10} |" + "".join(f" {s:<12} |" for s in scenarios)
    sep = "-" * len(header)

    print(sep)
    print(header)
    print(sep)

    # Find all RAM levels tested
    all_rams = set()
    for scenario_results in all_results.values():
        all_rams.update(scenario_results.keys())
    all_rams = sorted(all_rams)

    for ram in all_rams:
        row = f"{ram:<10} |"
        for scenario in scenarios:
            result = all_results.get(scenario, {}).get(ram, {})
            status = result.get("status", "")

            if status == "oom":
                row += f" {'OOM':<12} |"
            elif status == "stalled":
                row += f" {'STALL':<12} |"
            elif status == "timeout":
                row += f" {'TIMEOUT':<12} |"
            elif status == "completed":
                queries = result.get("queries", {})
                all_p95 = [q["stats"]["p95"] for q in queries.values()
                           if q.get("stats") and q["stats"].get("p95")]
                avg_p95 = sum(all_p95) / len(all_p95) if all_p95 else 0
                row += f" {avg_p95:<12.1f} |"
            elif status == "error":
                row += f" {'ERR':<12} |"
            else:
                row += f" {'-':<12} |"
        print(row)

    print(sep)

    # RAM_min per scenario
    print(f"\n{BOLD}RAM_min (smallest RAM without OOM/degradation):{RESET}")
    for scenario, results in all_results.items():
        ram_min = None
        for ram in sorted(results.keys()):
            if results[ram].get("status") == "completed":
                ram_min = ram
                break
        if ram_min:
            print(f"  {scenario}: {ram_min} GB")
        else:
            print(f"  {scenario}: N/A (all failed)")


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
        # Count both complete and partial exports
        if _is_export_dir(subdir):
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
            # Include both complete and partial exports
            if _is_export_dir(subdir):
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
