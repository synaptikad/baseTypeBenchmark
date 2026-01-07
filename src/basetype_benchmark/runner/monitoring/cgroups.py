"""Linux cgroups v2 reader for container memory monitoring.

Sprint 3 - Benchmark BaseType V3

Provides direct reading of cgroups v2 memory metrics for Docker containers.
This is Linux-only and requires kernel >= 5.10 for memory.peak support.

Key metrics:
- memory.current: Current memory usage in bytes
- memory.peak: Peak memory usage since last reset (kernel 5.10+)
- memory.max: Memory limit configured
- memory.events: OOM kill count
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class CgroupsNotFoundError(Exception):
    """Raised when cgroups path cannot be found for container."""
    pass


class CgroupsNotSupportedError(Exception):
    """Raised when cgroups v2 is not available on this system."""
    pass


@dataclass
class MemoryStats:
    """Memory statistics from cgroups v2."""
    current_bytes: int
    peak_bytes: int
    max_bytes: int | None  # None if unlimited
    oom_kill_count: int

    @property
    def current_mb(self) -> float:
        """Current memory in MB."""
        return self.current_bytes / (1024 * 1024)

    @property
    def peak_mb(self) -> float:
        """Peak memory in MB."""
        return self.peak_bytes / (1024 * 1024)

    @property
    def max_mb(self) -> float | None:
        """Memory limit in MB."""
        if self.max_bytes is None:
            return None
        return self.max_bytes / (1024 * 1024)

    @property
    def usage_percent(self) -> float | None:
        """Current usage as percentage of limit."""
        if self.max_bytes is None or self.max_bytes == 0:
            return None
        return (self.current_bytes / self.max_bytes) * 100


class CgroupsV2Monitor:
    """Direct cgroups v2 reading for Docker containers.

    Docker with cgroups v2 places container cgroups at:
    /sys/fs/cgroup/system.slice/docker-{container_id}.scope/

    Or in some configurations:
    /sys/fs/cgroup/docker/{container_id}/

    Example:
        ```python
        monitor = CgroupsV2Monitor("abc123def456...")
        monitor.reset_memory_peak()

        # ... run query ...

        stats = monitor.get_memory_stats()
        print(f"Peak: {stats.peak_mb:.1f} MB")
        print(f"OOM kills: {stats.oom_kill_count}")
        ```
    """

    CGROUP_BASE = Path("/sys/fs/cgroup")

    # Possible cgroup path patterns for Docker containers
    CGROUP_PATTERNS = [
        "system.slice/docker-{container_id}.scope",
        "docker/{container_id}",
        "docker.slice/docker-{container_id}.scope",
    ]

    def __init__(self, container_id: str):
        """Initialize cgroups monitor for a container.

        Args:
            container_id: Full Docker container ID (64 hex chars)

        Raises:
            CgroupsNotSupportedError: If cgroups v2 not available
            CgroupsNotFoundError: If container cgroup path not found
        """
        self.container_id = container_id
        self.cgroup_path = self._find_container_cgroup(container_id)

    def _find_container_cgroup(self, container_id: str) -> Path:
        """Find the cgroup path for a container.

        Args:
            container_id: Docker container ID

        Returns:
            Path to container's cgroup directory

        Raises:
            CgroupsNotSupportedError: If cgroups v2 not available
            CgroupsNotFoundError: If container cgroup not found
        """
        if not self.CGROUP_BASE.exists():
            raise CgroupsNotSupportedError(
                f"cgroups base path not found: {self.CGROUP_BASE}. "
                "This is likely not a Linux system or cgroups is not mounted."
            )

        # Check if this is cgroups v2 (unified hierarchy)
        if not (self.CGROUP_BASE / "cgroup.controllers").exists():
            raise CgroupsNotSupportedError(
                "cgroups v2 (unified hierarchy) not detected. "
                "This system may be using cgroups v1."
            )

        # Try each pattern to find the container
        for pattern in self.CGROUP_PATTERNS:
            path = self.CGROUP_BASE / pattern.format(container_id=container_id)
            if path.exists():
                return path

        # Try partial container ID match (Docker often uses short IDs)
        for pattern in self.CGROUP_PATTERNS:
            parent = self.CGROUP_BASE / pattern.split("{")[0].rstrip("/")
            if parent.exists():
                for child in parent.iterdir():
                    if container_id[:12] in child.name:
                        return child

        raise CgroupsNotFoundError(
            f"Cannot find cgroup for container {container_id[:12]}... "
            f"Searched patterns: {self.CGROUP_PATTERNS}"
        )

    def get_memory_current(self) -> int:
        """Get current memory usage in bytes.

        Returns:
            Current memory usage in bytes
        """
        return self._read_int("memory.current")

    def get_memory_peak(self) -> int:
        """Get peak memory usage since last reset.

        Note: Requires kernel >= 5.10 for memory.peak support.

        Returns:
            Peak memory usage in bytes
        """
        try:
            return self._read_int("memory.peak")
        except FileNotFoundError:
            # Fallback: return current if peak not supported
            return self.get_memory_current()

    def get_memory_max(self) -> int | None:
        """Get configured memory limit.

        Returns:
            Memory limit in bytes, or None if unlimited
        """
        content = self._read_text("memory.max").strip()
        if content == "max":
            return None
        return int(content)

    def get_oom_kill_count(self) -> int:
        """Get number of OOM kills from memory.events.

        Returns:
            Number of times OOM killer was triggered
        """
        try:
            events = self._read_text("memory.events")
            for line in events.splitlines():
                if line.startswith("oom_kill"):
                    parts = line.split()
                    if len(parts) >= 2:
                        return int(parts[1])
            return 0
        except FileNotFoundError:
            return 0

    def reset_memory_peak(self) -> bool:
        """Reset peak memory counter.

        Writes "0" to memory.peak to reset the peak counter.
        This allows measuring peak memory for a specific operation.

        Returns:
            True if reset successful, False otherwise
        """
        peak_path = self.cgroup_path / "memory.peak"
        try:
            peak_path.write_text("0")
            return True
        except (PermissionError, OSError) as e:
            # May need root/docker group permissions
            return False

    def get_memory_stats(self) -> MemoryStats:
        """Get all memory statistics.

        Returns:
            MemoryStats with current, peak, max, and OOM count
        """
        return MemoryStats(
            current_bytes=self.get_memory_current(),
            peak_bytes=self.get_memory_peak(),
            max_bytes=self.get_memory_max(),
            oom_kill_count=self.get_oom_kill_count(),
        )

    def _read_text(self, filename: str) -> str:
        """Read text content from a cgroup file."""
        filepath = self.cgroup_path / filename
        return filepath.read_text()

    def _read_int(self, filename: str) -> int:
        """Read integer value from a cgroup file."""
        return int(self._read_text(filename).strip())


def is_cgroups_v2_available() -> bool:
    """Check if cgroups v2 is available on this system.

    Returns:
        True if cgroups v2 is available, False otherwise
    """
    cgroup_base = Path("/sys/fs/cgroup")
    if not cgroup_base.exists():
        return False
    return (cgroup_base / "cgroup.controllers").exists()


def get_container_cgroup_path(container_id: str) -> Path | None:
    """Get cgroup path for a container if it exists.

    Args:
        container_id: Docker container ID

    Returns:
        Path to cgroup, or None if not found
    """
    try:
        monitor = CgroupsV2Monitor(container_id)
        return monitor.cgroup_path
    except (CgroupsNotFoundError, CgroupsNotSupportedError):
        return None
