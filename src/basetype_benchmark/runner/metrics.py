"""Resource metrics collection via cgroup v2.

Collects RAM, CPU usage from Docker containers using cgroup v2 interface.
"""

import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from threading import Thread, Event


@dataclass
class ResourceSnapshot:
    """Single resource measurement."""
    timestamp: float
    mem_bytes: int
    cpu_usage_usec: int


@dataclass
class ResourceStats:
    """Aggregated resource statistics."""
    mem_mb_avg: float = 0.0
    mem_mb_max: float = 0.0
    mem_mb_min: float = 0.0
    cpu_pct_avg: float = 0.0
    samples: int = 0


def get_cgroup_path(container_name: str) -> Optional[Path]:
    """Get cgroup v2 path for a container.

    Args:
        container_name: Docker container name

    Returns:
        Path to cgroup directory or None if not found
    """
    # Get container ID
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.Id}}", container_name],
        capture_output=True, text=True
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
    """Reset memory.peak counter (requires root)."""
    peak_file = cgroup_path / "memory.peak"
    if peak_file.exists():
        try:
            peak_file.write_text("0")
            return True
        except PermissionError:
            return False
    return False


def read_cpu_usage(cgroup_path: Path) -> int:
    """Read CPU usage in microseconds."""
    cpu_file = cgroup_path / "cpu.stat"
    if cpu_file.exists():
        for line in cpu_file.read_text().splitlines():
            if line.startswith("usage_usec"):
                return int(line.split()[1])
    return 0


class ResourceMonitor:
    """Background resource monitor for containers.

    Usage:
        monitor = ResourceMonitor("btb_timescaledb", interval_s=1.0)
        monitor.start()
        # ... run workload ...
        stats = monitor.stop()
    """

    def __init__(self, container_name: str, interval_s: float = 1.0):
        self.container_name = container_name
        self.interval_s = interval_s
        self._samples: List[ResourceSnapshot] = []
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._cgroup_path: Optional[Path] = None

    def start(self) -> bool:
        """Start background monitoring."""
        self._cgroup_path = get_cgroup_path(self.container_name)
        if not self._cgroup_path:
            return False

        self._samples.clear()
        self._stop_event.clear()
        self._thread = Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> ResourceStats:
        """Stop monitoring and return aggregated stats."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

        return self._compute_stats()

    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while not self._stop_event.is_set():
            if self._cgroup_path:
                snapshot = ResourceSnapshot(
                    timestamp=time.time(),
                    mem_bytes=read_memory_current(self._cgroup_path),
                    cpu_usage_usec=read_cpu_usage(self._cgroup_path),
                )
                self._samples.append(snapshot)

            self._stop_event.wait(self.interval_s)

    def _compute_stats(self) -> ResourceStats:
        """Compute aggregated statistics from samples."""
        if not self._samples:
            return ResourceStats()

        mem_mb = [s.mem_bytes / (1024 * 1024) for s in self._samples]

        # CPU percentage: delta usage / delta time
        cpu_pcts = []
        for i in range(1, len(self._samples)):
            dt = self._samples[i].timestamp - self._samples[i - 1].timestamp
            du = self._samples[i].cpu_usage_usec - self._samples[i - 1].cpu_usage_usec
            if dt > 0:
                cpu_pcts.append((du / 1_000_000) / dt * 100)

        return ResourceStats(
            mem_mb_avg=sum(mem_mb) / len(mem_mb) if mem_mb else 0,
            mem_mb_max=max(mem_mb) if mem_mb else 0,
            mem_mb_min=min(mem_mb) if mem_mb else 0,
            cpu_pct_avg=sum(cpu_pcts) / len(cpu_pcts) if cpu_pcts else 0,
            samples=len(self._samples),
        )


def get_peak_memory_mb(container_name: str) -> float:
    """Get peak memory usage for a container in MB."""
    cgroup_path = get_cgroup_path(container_name)
    if cgroup_path:
        return read_memory_peak(cgroup_path) / (1024 * 1024)
    return 0.0
