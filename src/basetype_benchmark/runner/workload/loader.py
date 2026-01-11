"""YAML loader for workload scenarios.

Loads workload definitions from config/workloads/ directory.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import QueryStep, WorkloadProfile, WorkloadScenario


# Default workloads directory
DEFAULT_WORKLOADS_DIR = Path(__file__).parent.parent.parent.parent.parent / "config" / "workloads"


# =============================================================================
# PREDEFINED WORKLOADS
# =============================================================================

WORKLOADS: dict[str, WorkloadScenario] = {
    "dashboard_refresh": WorkloadScenario(
        name="Dashboard Refresh",
        description="Simulates a dashboard refreshing every 5 seconds",
        profile=WorkloadProfile.READ_HEAVY,
        paradigms=["P1", "M1", "M2"],
        sequence=[
            QueryStep(query_id="Q12", repeat=1),  # Initial load
            QueryStep(query_id="Q6", repeat=10, think_time_ms=5000),  # Hourly aggregation
            QueryStep(query_id="Q7", repeat=5, think_time_ms=5000),  # Drift detection
            QueryStep(query_id="Q13", repeat=5, think_time_ms=5000),  # Office comfort
        ],
        duration_seconds=300,
        loop=True,
    ),
    "iot_ingestion": WorkloadScenario(
        name="IoT Gateway Ingestion",
        description="Simulates IoT gateway ingesting sensor data",
        profile=WorkloadProfile.WRITE_HEAVY,
        paradigms=["P1", "P2", "M1", "M2"],
        sequence=[
            QueryStep(query_id="QW1", repeat=100, batch_size=100, think_time_ms=10),
            QueryStep(query_id="QW2", repeat=5, think_time_ms=100),  # Metadata update
        ],
        duration_seconds=60,
        loop=True,
    ),
    "mixed_middleware": WorkloadScenario(
        name="Mixed Middleware",
        description="Realistic middleware with reads and writes",
        profile=WorkloadProfile.MIXED,
        paradigms=["P1", "P2", "M1", "M2", "O2"],
        sequence=[
            QueryStep(query_id="QW1", repeat=50, batch_size=10),
            QueryStep(query_id="Q1", repeat=5),  # Energy chain
            QueryStep(query_id="Q8", repeat=3),  # Tenant energy
            QueryStep(query_id="QW1", repeat=50, batch_size=10),
            QueryStep(query_id="Q7", repeat=1),  # Drift detection
        ],
        duration_seconds=180,
        loop=True,
    ),
    "bos_twin": WorkloadScenario(
        name="BOS Digital Twin",
        description="Digital twin platform with graph navigation and high-frequency ingestion",
        profile=WorkloadProfile.MIXED,
        paradigms=["P1", "M1", "M2"],
        sequence=[
            # Graph context navigation
            QueryStep(query_id="Q1", repeat=10, think_time_ms=100),  # FEEDS traversal
            QueryStep(query_id="Q2", repeat=5, think_time_ms=100),  # SERVES traversal
            # High-frequency ingestion (~350/s target)
            QueryStep(query_id="QW1", repeat=350, batch_size=100, think_time_ms=0),
            # Dashboard queries
            QueryStep(query_id="Q7", repeat=5),
            QueryStep(query_id="Q12", repeat=1),
        ],
        duration_seconds=120,
        loop=True,
    ),
    "graph_stress": WorkloadScenario(
        name="Graph Stress",
        description="Graph-intensive workload with deep traversals",
        profile=WorkloadProfile.GRAPH_STRESS,
        paradigms=["P1", "M1", "M2", "O2"],
        sequence=[
            QueryStep(query_id="Q1", repeat=20),  # Energy chain
            QueryStep(query_id="Q2", repeat=20),  # Tenant meters
            QueryStep(query_id="Q3", repeat=20),  # Zone sensors
            QueryStep(query_id="Q4", repeat=10),  # Equipment hierarchy
            QueryStep(query_id="Q5", repeat=10),  # Spatial containment
            QueryStep(query_id="Q20", repeat=5),  # Shortest path
            QueryStep(query_id="Q21", repeat=5),  # All paths
            QueryStep(query_id="Q22", repeat=5),  # Reachability
        ],
        duration_seconds=180,
        loop=True,
    ),
    "timeseries_stress": WorkloadScenario(
        name="Timeseries Stress",
        description="Timeseries-intensive with aggregations and sliding windows",
        profile=WorkloadProfile.TIMESERIES_STRESS,
        paradigms=["P1", "P2", "M1", "M2"],
        sequence=[
            QueryStep(query_id="Q6", repeat=30),  # Hourly aggregation (time_bucket)
            QueryStep(query_id="Q7", repeat=20),  # Drift detection
            QueryStep(query_id="Q9", repeat=15),  # Rolling average
            QueryStep(query_id="Q10", repeat=15),  # Peak detection
            QueryStep(query_id="Q11", repeat=10),  # Anomaly detection
        ],
        duration_seconds=180,
        loop=True,
    ),
}


# Workload info for display
WORKLOAD_INFO: dict[str, dict[str, Any]] = {
    "dashboard_refresh": {
        "name": "Dashboard Refresh",
        "description": "Read-heavy dashboard simulation",
        "profile": "read_heavy",
        "duration": "~5 min",
    },
    "iot_ingestion": {
        "name": "IoT Ingestion",
        "description": "Write-heavy IoT gateway simulation",
        "profile": "write_heavy",
        "duration": "~1 min",
    },
    "mixed_middleware": {
        "name": "Mixed Middleware",
        "description": "50/50 read/write middleware",
        "profile": "mixed",
        "duration": "~3 min",
    },
    "bos_twin": {
        "name": "BOS Digital Twin",
        "description": "Digital twin with graph + high-freq ingestion",
        "profile": "mixed",
        "duration": "~2 min",
    },
    "graph_stress": {
        "name": "Graph Stress",
        "description": "Graph traversal intensive",
        "profile": "graph_stress",
        "duration": "~3 min",
    },
    "timeseries_stress": {
        "name": "Timeseries Stress",
        "description": "TS aggregation intensive",
        "profile": "timeseries_stress",
        "duration": "~3 min",
    },
}


def get_workload(name: str) -> WorkloadScenario:
    """Get predefined workload by name.

    Args:
        name: Workload name

    Returns:
        WorkloadScenario instance

    Raises:
        ValueError: If workload name is unknown
    """
    if name not in WORKLOADS:
        available = ", ".join(WORKLOADS.keys())
        raise ValueError(f"Unknown workload: {name}. Available: {available}")
    return WORKLOADS[name]


def get_workload_info(name: str) -> dict[str, Any]:
    """Get workload info for display."""
    return WORKLOAD_INFO.get(name, {})


def list_workloads() -> list[str]:
    """List all available workload names."""
    return list(WORKLOADS.keys())


# =============================================================================
# YAML LOADING
# =============================================================================

def load_workload_from_yaml(path: Path) -> WorkloadScenario:
    """Load workload scenario from YAML file.

    YAML format:
    ```yaml
    name: "Dashboard Refresh"
    description: "Simulates a dashboard refreshing every 5 seconds"
    profile: read_heavy

    paradigms:
      - P1
      - M1
      - M2

    sequence:
      - query: Q12
        repeat: 1

      - query: Q6
        repeat: 10
        think_time_ms: 5000

      - query: QW1
        repeat: 100
        batch_size: 100

    duration_seconds: 300
    loop: true

    metrics:
      throughput: true
      latency_distribution: true
      error_rate: true
    ```

    Args:
        path: Path to YAML file

    Returns:
        WorkloadScenario instance

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If YAML format is invalid
    """
    if not path.exists():
        raise FileNotFoundError(f"Workload file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid workload file: expected dict, got {type(data)}")

    # Required fields
    name = data.get("name", path.stem)
    description = data.get("description", "")

    # Parse profile
    profile_str = data.get("profile", "mixed")
    try:
        profile = WorkloadProfile(profile_str)
    except ValueError:
        profile = WorkloadProfile.MIXED

    # Parse paradigms
    paradigms = data.get("paradigms", ["P1", "M1", "M2"])
    if isinstance(paradigms, str):
        paradigms = [p.strip() for p in paradigms.split(",")]

    # Parse sequence
    sequence_data = data.get("sequence", [])
    sequence: list[QueryStep] = []
    for step in sequence_data:
        if isinstance(step, dict):
            query_id = step.get("query") or step.get("query_id", "")
            sequence.append(
                QueryStep(
                    query_id=query_id,
                    repeat=step.get("repeat", 1),
                    think_time_ms=step.get("think_time_ms", 0),
                    batch_size=step.get("batch_size"),
                    concurrent=step.get("concurrent", False),
                )
            )

    if not sequence:
        raise ValueError("Workload must have at least one query in sequence")

    # Duration and loop
    duration_seconds = data.get("duration_seconds")
    loop = data.get("loop", False)

    # Metrics options
    metrics = data.get("metrics", {})
    collect_throughput = metrics.get("throughput", True)
    collect_latency = metrics.get("latency_distribution", True)
    collect_errors = metrics.get("error_rate", True)

    return WorkloadScenario(
        name=name,
        description=description,
        profile=profile,
        paradigms=paradigms,
        sequence=sequence,
        duration_seconds=duration_seconds,
        loop=loop,
        collect_throughput=collect_throughput,
        collect_latency_distribution=collect_latency,
        collect_error_rate=collect_errors,
    )


def save_workload_to_yaml(scenario: WorkloadScenario, path: Path) -> None:
    """Save workload scenario to YAML file.

    Args:
        scenario: WorkloadScenario instance
        path: Output path
    """
    sequence_data = []
    for step in scenario.sequence:
        step_dict: dict[str, Any] = {
            "query": step.query_id,
            "repeat": step.repeat,
        }
        if step.think_time_ms > 0:
            step_dict["think_time_ms"] = step.think_time_ms
        if step.batch_size is not None:
            step_dict["batch_size"] = step.batch_size
        if step.concurrent:
            step_dict["concurrent"] = step.concurrent
        sequence_data.append(step_dict)

    data = {
        "name": scenario.name,
        "description": scenario.description,
        "profile": scenario.profile.value,
        "paradigms": scenario.paradigms,
        "sequence": sequence_data,
        "duration_seconds": scenario.duration_seconds,
        "loop": scenario.loop,
        "metrics": {
            "throughput": scenario.collect_throughput,
            "latency_distribution": scenario.collect_latency_distribution,
            "error_rate": scenario.collect_error_rate,
        },
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def load_or_get_workload(name_or_path: str) -> WorkloadScenario:
    """Load workload from name or YAML path.

    Args:
        name_or_path: Either a predefined workload name or path to YAML file

    Returns:
        WorkloadScenario instance
    """
    # Check if it's a predefined workload
    if name_or_path in WORKLOADS:
        return get_workload(name_or_path)

    # Try as path
    path = Path(name_or_path)
    if path.exists():
        return load_workload_from_yaml(path)

    # Try in default workloads directory
    default_path = DEFAULT_WORKLOADS_DIR / f"{name_or_path}.yaml"
    if default_path.exists():
        return load_workload_from_yaml(default_path)

    raise ValueError(
        f"Unknown workload: {name_or_path}. "
        f"Available: {', '.join(WORKLOADS.keys())}"
    )
