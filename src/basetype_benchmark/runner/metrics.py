"""Resource metrics collection via cgroup v2.

Collects RAM, CPU usage from Docker containers using cgroup v2 interface.
Consolidated module - single source of truth for all metrics operations.
"""

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Event, Thread
from typing import Dict, List, Optional

IS_LINUX = os.name == "posix" and os.path.exists("/sys/fs/cgroup")


# =============================================================================
# Low-level cgroup functions
# =============================================================================

def get_cgroup_path(container_name: str) -> Optional[Path]:
    """Get cgroup v2 path for a container.

    Args:
        container_name: Docker container name

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
            # Try with sudo if direct write fails (cgroup files often need root)
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


# =============================================================================
# High-level Metrics class (used by run.py)
# =============================================================================

@dataclass
class Metrics:
    """Container metrics snapshot."""
    container: str
    timestamp: float
    memory_mb: float
    memory_peak_mb: float
    cpu_time_sec: float
    cgroup_path: Optional[Path] = None

    @classmethod
    def capture(cls, container_name: str) -> "Metrics":
        """Capture current metrics for a container."""
        cgroup_path = get_cgroup_path(container_name)
        metrics = get_cgroup_metrics(cgroup_path) if cgroup_path else None

        if metrics:
            return cls(
                container=container_name,
                timestamp=time.time(),
                memory_mb=metrics.get("memory_bytes", 0) / (1024 * 1024),
                memory_peak_mb=metrics.get("memory_peak_bytes", 0) / (1024 * 1024),
                cpu_time_sec=metrics.get("cpu_usage_usec", 0) / 1_000_000,
                cgroup_path=cgroup_path,
            )

        # Fallback to docker stats
        return cls._from_docker_stats(container_name)

    @classmethod
    def _from_docker_stats(cls, container_name: str) -> "Metrics":
        """Fallback: get metrics from docker stats."""
        try:
            result = subprocess.run(
                f"docker stats --no-stream --format '{{{{.MemUsage}}}}' {container_name}",
                shell=True, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                usage = result.stdout.strip().split("/")[0].strip()
                mem_mb = 0.0
                if "GiB" in usage:
                    mem_mb = float(usage.replace("GiB", "").strip()) * 1024
                elif "MiB" in usage:
                    mem_mb = float(usage.replace("MiB", "").strip())

                return cls(
                    container=container_name,
                    timestamp=time.time(),
                    memory_mb=mem_mb,
                    memory_peak_mb=mem_mb,  # No peak available via docker stats
                    cpu_time_sec=0.0,
                )
        except Exception:
            pass

        return cls(
            container=container_name,
            timestamp=time.time(),
            memory_mb=0.0,
            memory_peak_mb=0.0,
            cpu_time_sec=0.0,
        )

    def reset_peak(self) -> bool:
        """Reset memory peak counter (for query-only measurements)."""
        if self.cgroup_path:
            return reset_memory_peak(self.cgroup_path)
        return False


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


# =============================================================================
# Background monitoring (for stress tests / continuous monitoring)
# =============================================================================

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
