"""Background resource monitoring for containers.

Provides continuous sampling of container resources during workload execution.
"""

import time
from dataclasses import dataclass
from pathlib import Path
from threading import Event, Thread
from typing import List, Optional

from .cgroup import get_cgroup_path, read_memory_current, read_cpu_usage


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
