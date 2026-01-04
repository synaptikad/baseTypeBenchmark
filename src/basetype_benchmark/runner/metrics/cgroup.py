"""Low-level cgroup v2 filesystem operations.

Reads container metrics directly from Linux cgroup v2 filesystem.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Optional

IS_LINUX = os.name == "posix" and os.path.exists("/sys/fs/cgroup")


def get_cgroup_path(container_name: str) -> Optional[Path]:
    """Get cgroup v2 path for a Docker container.

    Args:
        container_name: Docker container name (e.g., "btb_timescaledb")

    Returns:
        Path to cgroup directory or None if not found
    """
    if not IS_LINUX:
        return None

    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.Id}}", container_name],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return None

        container_id = result.stdout.strip()
        if not container_id:
            return None

        # cgroup v2 paths (Linux)
        candidates = [
            Path(f"/sys/fs/cgroup/system.slice/docker-{container_id}.scope"),
            Path(f"/sys/fs/cgroup/docker/{container_id}"),
        ]

        for path in candidates:
            if path.exists():
                return path

        return None
    except Exception:
        return None


def read_memory_current(cgroup_path: Path) -> int:
    """Read current memory usage in bytes."""
    mem_file = cgroup_path / "memory.current"
    if mem_file.exists():
        return int(mem_file.read_text().strip())
    return 0


def read_memory_peak(cgroup_path: Path) -> int:
    """Read peak memory usage in bytes."""
    mem_file = cgroup_path / "memory.peak"
    if mem_file.exists():
        return int(mem_file.read_text().strip())
    return 0


def reset_memory_peak(cgroup_path: Path) -> bool:
    """Reset memory.peak counter (requires root).

    Returns True only if peak was actually reset (value decreased).
    This verification is critical - without it, peak accumulates across queries.
    """
    if not cgroup_path:
        return False

    peak_file = cgroup_path / "memory.peak"
    if not peak_file.exists():
        return False

    try:
        # 1. Read BEFORE
        peak_before = int(peak_file.read_text().strip())

        # 2. Write "0"
        try:
            peak_file.write_text("0")
        except PermissionError:
            # Try with sudo if direct write fails
            if not str(peak_file).startswith("/sys/fs/cgroup/"):
                return False
            result = subprocess.run(
                ["sudo", "-n", "tee", str(peak_file)],
                input="0", text=True, capture_output=True,
            )
            if result.returncode != 0:
                return False

        # 3. Verify AFTER - did the reset actually work?
        peak_after = int(peak_file.read_text().strip())
        return peak_after < peak_before

    except Exception:
        return False


def read_cpu_usage(cgroup_path: Path) -> int:
    """Read CPU usage in microseconds."""
    cpu_file = cgroup_path / "cpu.stat"
    if cpu_file.exists():
        for line in cpu_file.read_text().splitlines():
            if line.startswith("usage_usec"):
                return int(line.split()[1])
    return 0


def get_cgroup_metrics(cgroup_path: Path) -> Optional[Dict]:
    """Read all cgroup v2 metrics from filesystem.

    Returns:
        Dict with memory_bytes, memory_peak_bytes, cpu_usage_usec, etc.
    """
    if not cgroup_path or not cgroup_path.exists():
        return None

    metrics = {}
    try:
        mem_current = cgroup_path / "memory.current"
        if mem_current.exists():
            metrics["memory_bytes"] = int(mem_current.read_text().strip())

        mem_peak = cgroup_path / "memory.peak"
        if mem_peak.exists():
            metrics["memory_peak_bytes"] = int(mem_peak.read_text().strip())

        cpu_stat = cgroup_path / "cpu.stat"
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
