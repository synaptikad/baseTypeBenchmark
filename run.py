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

    # Set environment variable for docker-compose
    import os
    env = os.environ.copy()
    env["MEMORY_LIMIT"] = f"{ram_gb}g"

    try:
        result = subprocess.run(
            f"docker compose up -d {' '.join(containers)}",
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


def collect_resource_samples(container_name: str, duration_s: float, interval_s: float = 1.0) -> Dict:
    """Collect resource samples during query execution."""
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

# Queries by scenario
QUERIES_BY_SCENARIO = {
    "P1": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12"],
    "P2": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12"],
    "M1": ["Q1", "Q2", "Q3", "Q4", "Q5"],  # No timeseries queries
    "M2": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q8"],  # Structure + hybrid Q8
    "O1": ["Q1", "Q2", "Q3", "Q4", "Q5"],  # No timeseries queries
    "O2": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q8"],  # Structure + hybrid Q8
}

# Benchmark protocol
N_WARMUP = 3
N_RUNS = 10

QUERIES_DIR = Path(__file__).parent / "queries"


def load_query(scenario: str, query_id: str) -> Optional[str]:
    """Load query text for a scenario."""
    if scenario.startswith("P"):
        query_dir = QUERIES_DIR / "sql"
        ext = "sql"
    elif scenario.startswith("M"):
        query_dir = QUERIES_DIR / "cypher"
        ext = "cypher"
    elif scenario.startswith("O"):
        query_dir = QUERIES_DIR / "sparql"
        ext = "sparql"
    else:
        return None

    # Find query file
    for f in query_dir.glob(f"{query_id}_*.{ext}"):
        return f.read_text(encoding="utf-8")
    return None


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


def run_scenario_benchmark(scenario: str, export_dir: Path) -> Dict:
    """Run benchmark for a single scenario using existing loaders.

    Args:
        scenario: P1, P2, M1, M2, O1, O2
        export_dir: Path to exported dataset

    Returns:
        Dict with benchmark results
    """
    result = {
        "scenario": scenario,
        "status": "pending",
        "load_time_s": 0.0,
        "queries": {},
        "error": None
    }

    start_total = time.time()

    try:
        if scenario in ["P1", "P2"]:
            result = _run_postgres_benchmark(scenario, export_dir, result)
        elif scenario in ["M1", "M2"]:
            result = _run_memgraph_benchmark(scenario, export_dir, result)
        elif scenario in ["O1", "O2"]:
            result = _run_oxigraph_benchmark(scenario, export_dir, result)
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


def _run_postgres_benchmark(scenario: str, export_dir: Path, result: Dict) -> Dict:
    """Run PostgreSQL benchmark (P1 or P2)."""
    from basetype_benchmark.loaders.postgres.load import (
        get_connection, clear_database, load_p1, load_p2
    )

    print_info(f"Connecting to PostgreSQL...")
    conn = get_connection()

    try:
        # Clear and load
        print_info("Clearing database...")
        clear_database(conn)

        print_info(f"Loading data ({scenario} schema)...")
        load_start = time.time()

        # The loaders expect JSON files, but we have CSV - need adapter
        # For now, use CSV directly with psycopg2
        if scenario == "P1":
            load_result = _load_postgres_from_csv(conn, export_dir, "relational")
        else:
            load_result = _load_postgres_from_csv(conn, export_dir, "jsonb")

        result["load_time_s"] = time.time() - load_start
        print_ok(f"Data loaded in {result['load_time_s']:.1f}s")

        # Execute queries
        queries_to_run = QUERIES_BY_SCENARIO.get(scenario, [])
        for query_id in queries_to_run:
            query_text = load_query(scenario, query_id)
            if not query_text:
                print_warn(f"Query {query_id} not found, skipping")
                continue

            print(f"    {query_id}...", end=" ", flush=True)

            # Drop caches before query (if root)
            drop_caches()

            # Warmup
            for _ in range(N_WARMUP):
                try:
                    with conn.cursor() as cur:
                        cur.execute(query_text)
                        cur.fetchall()
                    conn.commit()
                except Exception:
                    conn.rollback()

            # Measured runs
            latencies = []
            rows = 0
            for run_idx in range(N_RUNS):
                # Drop caches between runs for fair measurement
                if run_idx > 0:
                    drop_caches()
                try:
                    t0 = time.perf_counter()
                    with conn.cursor() as cur:
                        cur.execute(query_text)
                        data = cur.fetchall()
                        rows = len(data)
                    conn.commit()
                    latencies.append((time.perf_counter() - t0) * 1000)  # ms
                except Exception as e:
                    conn.rollback()
                    print_warn(f"Query error: {e}")

            stats = compute_stats(latencies)
            result["queries"][query_id] = {
                "latencies_ms": latencies,
                "rows": rows,
                "stats": stats
            }
            print(f"p50={stats['p50']:.1f}ms p95={stats['p95']:.1f}ms")

        result["status"] = "completed"

    finally:
        conn.close()

    return result


def _load_postgres_from_csv(conn, export_dir: Path, schema_type: str) -> Dict:
    """Load PostgreSQL from CSV files."""
    from psycopg2.extras import execute_batch

    cur = conn.cursor()

    # Create schema
    cur.execute("DROP TABLE IF EXISTS timeseries CASCADE")
    cur.execute("DROP TABLE IF EXISTS edges CASCADE")
    cur.execute("DROP TABLE IF EXISTS nodes CASCADE")

    # Nodes table
    cur.execute("""
        CREATE TABLE nodes (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT,
            building_id INTEGER DEFAULT 0,
            data JSONB DEFAULT '{}'
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
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, rel_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, rel_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ts_point_time ON timeseries(point_id, time DESC)")

    conn.commit()

    # Load nodes from CSV
    import csv
    nodes_file = export_dir / "nodes.csv"
    if nodes_file.exists():
        with open(nodes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                batch.append((
                    row['id'],
                    row['type'],
                    row.get('name', ''),
                    int(row['building_id']) if row.get('building_id') else 0,
                    row.get('data', '{}')
                ))
                if len(batch) >= 1000:
                    execute_batch(cur, """
                        INSERT INTO nodes (id, type, name, building_id, data)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, batch)
                    conn.commit()
                    batch.clear()
            if batch:
                execute_batch(cur, """
                    INSERT INTO nodes (id, type, name, building_id, data)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, batch)
                conn.commit()

    # Load edges from CSV
    edges_file = export_dir / "edges.csv"
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
                    batch.clear()
            if batch:
                execute_batch(cur, """
                    INSERT INTO edges (src_id, dst_id, rel_type)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, batch)
                conn.commit()

    # Load timeseries from CSV (use COPY for performance)
    ts_file = export_dir / "timeseries.csv"
    if ts_file.exists():
        with open(ts_file, 'r', encoding='utf-8') as f:
            cur.copy_expert(
                "COPY timeseries (time, point_id, value) FROM STDIN WITH CSV HEADER",
                f
            )
        conn.commit()

    cur.close()
    return {"nodes": True, "edges": True, "timeseries": True}


def _run_memgraph_benchmark(scenario: str, export_dir: Path, result: Dict) -> Dict:
    """Run Memgraph benchmark (M1 or M2)."""
    from basetype_benchmark.loaders.memgraph.load import (
        get_driver, load_constraints, load_nodes, load_edges, load_timeseries_chunks
    )

    print_info("Connecting to Memgraph...")
    driver = get_driver()

    try:
        # Clear and load
        print_info("Clearing database...")
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

        print_info("Loading data...")
        load_start = time.time()

        with driver.session() as session:
            load_constraints(session)

            nodes_file = export_dir / "nodes.json"
            edges_file = export_dir / "edges.json"
            chunks_file = export_dir / "timeseries_chunks.json"

            if nodes_file.exists():
                load_nodes(session, nodes_file, batch_size=5000)
            else:
                print_warn("nodes.json not found - need to regenerate dataset with graph format")
                result["status"] = "error"
                result["error"] = "nodes.json not found - regenerate dataset"
                return result

            if edges_file.exists():
                load_edges(session, edges_file, batch_size=5000)

            if scenario == "M2" and chunks_file.exists():
                load_timeseries_chunks(session, chunks_file, batch_size=5000)

        result["load_time_s"] = time.time() - load_start
        print_ok(f"Data loaded in {result['load_time_s']:.1f}s")

        # Execute queries
        queries_to_run = QUERIES_BY_SCENARIO.get(scenario, [])
        for query_id in queries_to_run:
            query_text = load_query(scenario, query_id)
            if not query_text:
                print_warn(f"Query {query_id} not found, skipping")
                continue

            print(f"    {query_id}...", end=" ", flush=True)

            # Drop caches before query
            drop_caches()

            # Warmup
            for _ in range(N_WARMUP):
                try:
                    with driver.session() as session:
                        list(session.run(query_text))
                except Exception:
                    pass

            # Measured runs
            latencies = []
            rows = 0
            for run_idx in range(N_RUNS):
                if run_idx > 0:
                    drop_caches()
                try:
                    t0 = time.perf_counter()
                    with driver.session() as session:
                        records = list(session.run(query_text))
                        rows = len(records)
                    latencies.append((time.perf_counter() - t0) * 1000)  # ms
                except Exception as e:
                    print_warn(f"Query error: {e}")

            stats = compute_stats(latencies)
            result["queries"][query_id] = {
                "latencies_ms": latencies,
                "rows": rows,
                "stats": stats
            }
            print(f"p50={stats['p50']:.1f}ms p95={stats['p95']:.1f}ms")

        result["status"] = "completed"

    finally:
        driver.close()

    return result


def _run_oxigraph_benchmark(scenario: str, export_dir: Path, result: Dict) -> Dict:
    """Run Oxigraph benchmark (O1 or O2)."""
    from basetype_benchmark.loaders.oxigraph.load import (
        wait_for_oxigraph, clear_store, load_jsonld, count_triples
    )
    import requests

    endpoint = "http://localhost:7878"

    print_info("Connecting to Oxigraph...")
    wait_for_oxigraph(endpoint)

    try:
        # Clear and load
        print_info("Clearing store...")
        clear_store(endpoint)

        print_info("Loading data...")
        load_start = time.time()

        jsonld_file = export_dir / "graph.jsonld"
        if not jsonld_file.exists():
            print_warn("graph.jsonld not found - need to regenerate dataset with rdf format")
            result["status"] = "error"
            result["error"] = "graph.jsonld not found - regenerate dataset"
            return result

        load_jsonld(endpoint, jsonld_file)
        result["load_time_s"] = time.time() - load_start

        triples = count_triples(endpoint)
        print_ok(f"Data loaded in {result['load_time_s']:.1f}s ({triples} triples)")

        # Execute queries
        queries_to_run = QUERIES_BY_SCENARIO.get(scenario, [])
        for query_id in queries_to_run:
            query_text = load_query(scenario, query_id)
            if not query_text:
                print_warn(f"Query {query_id} not found, skipping")
                continue

            print(f"    {query_id}...", end=" ", flush=True)

            # Drop caches before query
            drop_caches()

            # Warmup
            for _ in range(N_WARMUP):
                try:
                    requests.get(
                        f"{endpoint}/query",
                        params={"query": query_text},
                        timeout=60
                    )
                except Exception:
                    pass

            # Measured runs
            latencies = []
            rows = 0
            for run_idx in range(N_RUNS):
                if run_idx > 0:
                    drop_caches()
                try:
                    t0 = time.perf_counter()
                    resp = requests.get(
                        f"{endpoint}/query",
                        params={"query": query_text},
                        headers={"Accept": "application/sparql-results+json"},
                        timeout=60
                    )
                    latencies.append((time.perf_counter() - t0) * 1000)  # ms
                    if resp.status_code == 200:
                        data = resp.json()
                        rows = len(data.get("results", {}).get("bindings", []))
                except Exception as e:
                    print_warn(f"Query error: {e}")

            stats = compute_stats(latencies)
            result["queries"][query_id] = {
                "latencies_ms": latencies,
                "rows": rows,
                "stats": stats
            }
            print(f"p50={stats['p50']:.1f}ms p95={stats['p95']:.1f}ms")

        result["status"] = "completed"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


# =============================================================================
# WORKFLOW: BENCHMARK (RAM-Gradient Protocol)
# =============================================================================

def run_ram_gradient_benchmark(scenario: str, export_dir: Path, scale: str, results_dir: Path) -> Dict:
    """Run RAM-Gradient benchmark for a scenario.

    Protocol:
    - P1/P2: Start from min RAM, iterate up until performance plateau
    - M/O: Start from min RAM, escalate on OOM, continue to plateau

    Returns dict with results per RAM level.
    """
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
            bench_result = run_scenario_benchmark(scenario, export_dir)

            # Check for OOM
            if check_container_oom(main_container):
                print_warn(f"OOM detected at {current_ram}GB")
                ram_results[current_ram] = {"status": "oom", "ram_gb": current_ram}
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
                # For M/O, OOM might manifest as connection error
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


def workflow_benchmark():
    """Benchmark execution workflow with RAM-Gradient protocol."""
    print_header("BENCHMARK EXECUTION (RAM-Gradient Protocol)")

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

    scale = get_scale_from_profile(dataset)

    # Select engines
    scenarios = select_engines()
    if not scenarios:
        return

    # Confirm
    print_header("CONFIRM RAM-GRADIENT PROTOCOL")
    print(f"Dataset:   {dataset} (scale: {scale})")
    print(f"Engines:   {', '.join(scenarios)}")
    print(f"\n{BOLD}RAM-Gradient Protocol:{RESET}")
    print(f"  - RAM levels: {RAM_LEVELS} GB")
    print(f"  - P1/P2: Start min, iterate to plateau")
    print(f"  - M/O: Start min, escalate on OOM, then plateau")
    print(f"  - Plateau threshold: {PERF_PLATEAU_THRESHOLD}% improvement")
    print(f"\n{BOLD}Per RAM level:{RESET}")
    print(f"  - {N_WARMUP} warmup runs")
    print(f"  - {N_RUNS} measured runs per query")
    print(f"  - drop_caches between queries (if root)")
    print(f"  - Metrics: p50, p95, RAM steady/peak, CPU")

    if not prompt_yes_no("\nStart benchmark?"):
        return

    # Get export directory
    export_dir = Path("src/basetype_benchmark/dataset/exports") / f"{dataset}_seed42"
    if not export_dir.exists():
        print_err(f"Export directory not found: {export_dir}")
        input("\nPress Enter...")
        return

    # Check formats
    has_csv = (export_dir / "nodes.csv").exists()
    has_json = (export_dir / "nodes.json").exists()
    has_jsonld = (export_dir / "graph.jsonld").exists()

    print_info(f"Export formats: CSV={has_csv}, JSON={has_json}, JSON-LD={has_jsonld}")

    # Create results directory
    results_dir = Path("benchmark_results") / datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir.mkdir(parents=True, exist_ok=True)

    all_results = {}

    for scenario in scenarios:
        print_header(f"RAM-GRADIENT: {scenario} ({SCENARIOS[scenario]['name']})")

        ram_results = run_ram_gradient_benchmark(scenario, export_dir, scale, results_dir)
        all_results[scenario] = ram_results

        # Save intermediate results
        with open(results_dir / f"{scenario}_ram_gradient.json", 'w') as f:
            json.dump(ram_results, f, indent=2, default=str)

    # Save final summary
    with open(results_dir / "summary.json", 'w') as f:
        json.dump({
            "dataset": dataset,
            "scale": scale,
            "scenarios": all_results,
            "protocol": {
                "ram_levels": RAM_LEVELS,
                "warmup": N_WARMUP,
                "runs": N_RUNS,
                "plateau_threshold": PERF_PLATEAU_THRESHOLD
            },
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, default=str)

    # Print summary
    print_header("RAM-GRADIENT RESULTS")
    _print_ram_gradient_summary(all_results, scale)

    print(f"\n{DIM}Results saved to: {results_dir}{RESET}")
    input("\nPress Enter...")


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
