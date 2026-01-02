"""Lightweight cgroup-based metrics for accurate container RAM/CPU measurement.

Uses Linux cgroup v2 filesystem directly for precise measurements,
with fallback to docker stats if cgroups unavailable.
"""

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

IS_LINUX = os.name == "posix" and os.path.exists("/sys/fs/cgroup")


def get_container_cgroup_path(container_name: str) -> Optional[str]:
    """Get the cgroup v2 path for a container (Linux only)."""
    if not IS_LINUX:
        return None
    try:
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
        Dict with memory_bytes, memory_peak_bytes, cpu_usage_usec, etc.
    """
    if not cgroup_path or not os.path.exists(cgroup_path):
        return None

    metrics = {}
    try:
        mem_current = Path(cgroup_path) / "memory.current"
        if mem_current.exists():
            metrics["memory_bytes"] = int(mem_current.read_text().strip())

        mem_peak = Path(cgroup_path) / "memory.peak"
        if mem_peak.exists():
            metrics["memory_peak_bytes"] = int(mem_peak.read_text().strip())

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
    """Reset memory.peak counter to current value (requires root/sudo)."""
    if not cgroup_path:
        return False
    try:
        mem_peak = Path(cgroup_path) / "memory.peak"
        if not mem_peak.exists():
            return False
        
        # Try direct write first
        try:
            mem_peak.write_text("0")
            return True
        except PermissionError:
            # Requires sudo - try non-interactive
            if not str(mem_peak).startswith("/sys/fs/cgroup/"):
                return False
            r = subprocess.run(
                ["sudo", "-n", "tee", str(mem_peak)],
                input="0", text=True, capture_output=True,
            )
            return r.returncode == 0
    except Exception:
        return False


@dataclass
class Metrics:
    """Container metrics snapshot."""
    container: str
    timestamp: float
    memory_mb: float
    memory_peak_mb: float
    cpu_time_sec: float
    cgroup_path: Optional[str] = None
    
    @classmethod
    def capture(cls, container_name: str) -> "Metrics":
        """Capture current metrics for a container."""
        cgroup_path = get_container_cgroup_path(container_name)
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
