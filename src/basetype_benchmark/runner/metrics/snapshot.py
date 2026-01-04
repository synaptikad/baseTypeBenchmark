"""Container metrics snapshot.

Captures point-in-time resource usage from Docker containers.
"""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .cgroup import get_cgroup_path, get_cgroup_metrics, reset_memory_peak


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
