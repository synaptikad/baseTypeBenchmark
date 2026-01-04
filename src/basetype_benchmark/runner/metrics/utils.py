"""Utility functions for metrics processing."""

import subprocess
from typing import Dict

from .cgroup import get_cgroup_path, read_memory_peak
from .snapshot import Metrics


def compute_delta(before: Metrics, after: Metrics) -> Dict:
    """Compute resource usage delta between two snapshots."""
    wall_time = after.timestamp - before.timestamp
    cpu_delta = after.cpu_time_sec - before.cpu_time_sec

    return {
        "memory_before_mb": before.memory_mb,
        "memory_after_mb": after.memory_mb,
        "memory_delta_mb": after.memory_mb - before.memory_mb,
        "memory_peak_mb": after.memory_peak_mb,
        "cpu_time_sec": cpu_delta,
        "cpu_percent": (cpu_delta / wall_time * 100) if wall_time > 0 else 0.0,
        "wall_time_sec": wall_time,
    }


def check_oom(container_name: str) -> bool:
    """Check if container was OOM-killed."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.OOMKilled}}", container_name],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip().lower() == "true"
    except Exception:
        return False


def get_peak_memory_mb(container_name: str) -> float:
    """Get peak memory usage for a container in MB."""
    cgroup_path = get_cgroup_path(container_name)
    if cgroup_path:
        return read_memory_peak(cgroup_path) / (1024 * 1024)
    return 0.0
