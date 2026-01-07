"""Docker SDK wrapper for container management.

Sprint 3 - Benchmark BaseType V3

Provides high-level Docker operations needed for benchmark execution:
- Get container IDs from names
- Set memory limits without restart (docker update)
- Check container health
- Get basic container stats
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import docker
from docker.errors import DockerException, NotFound, APIError


class ContainerNotFoundError(Exception):
    """Raised when a container cannot be found."""
    pass


class DockerNotAvailableError(Exception):
    """Raised when Docker daemon is not available."""
    pass


@dataclass
class ContainerInfo:
    """Basic container information."""
    id: str
    name: str
    status: str  # running, exited, paused, etc.
    image: str
    memory_limit_bytes: int | None
    memory_usage_bytes: int | None

    @property
    def short_id(self) -> str:
        """Short container ID (12 chars)."""
        return self.id[:12]

    @property
    def memory_limit_mb(self) -> float | None:
        """Memory limit in MB."""
        if self.memory_limit_bytes is None:
            return None
        return self.memory_limit_bytes / (1024 * 1024)

    @property
    def memory_usage_mb(self) -> float | None:
        """Memory usage in MB."""
        if self.memory_usage_bytes is None:
            return None
        return self.memory_usage_bytes / (1024 * 1024)

    @property
    def is_running(self) -> bool:
        """Check if container is running."""
        return self.status == "running"


class DockerClient:
    """Docker SDK wrapper for benchmark container management.

    Example:
        ```python
        client = DockerClient()

        # Get container info
        info = client.get_container_info("benchmark-memgraph")
        print(f"Container {info.short_id} using {info.memory_usage_mb:.1f} MB")

        # Set memory limit (no restart)
        client.set_memory_limit("benchmark-memgraph", 8192)  # 8 GB
        ```
    """

    def __init__(self):
        """Initialize Docker client.

        Raises:
            DockerNotAvailableError: If Docker daemon is not available
        """
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
        except DockerException as e:
            raise DockerNotAvailableError(
                f"Cannot connect to Docker daemon: {e}. "
                "Is Docker running?"
            )

    def get_container_id(self, name: str) -> str:
        """Get full container ID from name.

        Args:
            name: Container name (e.g., "benchmark-memgraph")

        Returns:
            Full container ID (64 hex chars)

        Raises:
            ContainerNotFoundError: If container not found
        """
        try:
            container = self.client.containers.get(name)
            return container.id
        except NotFound:
            raise ContainerNotFoundError(f"Container not found: {name}")

    def get_container_info(self, name: str) -> ContainerInfo:
        """Get container information.

        Args:
            name: Container name

        Returns:
            ContainerInfo with ID, status, memory info

        Raises:
            ContainerNotFoundError: If container not found
        """
        try:
            container = self.client.containers.get(name)
            attrs = container.attrs

            # Get memory limit from HostConfig
            host_config = attrs.get("HostConfig", {})
            memory_limit = host_config.get("Memory")
            if memory_limit == 0:
                memory_limit = None  # 0 means unlimited

            # Try to get current memory usage (requires container running)
            memory_usage = None
            if container.status == "running":
                try:
                    stats = container.stats(stream=False)
                    memory_usage = stats.get("memory_stats", {}).get("usage")
                except (APIError, KeyError):
                    pass

            return ContainerInfo(
                id=container.id,
                name=container.name,
                status=container.status,
                image=attrs.get("Config", {}).get("Image", "unknown"),
                memory_limit_bytes=memory_limit,
                memory_usage_bytes=memory_usage,
            )
        except NotFound:
            raise ContainerNotFoundError(f"Container not found: {name}")

    def set_memory_limit(self, name: str, limit_mb: int) -> bool:
        """Set memory limit on a container without restart.

        Uses `docker update --memory` which can change limits on running
        containers without requiring a restart.

        Args:
            name: Container name
            limit_mb: Memory limit in MB

        Returns:
            True if successful

        Raises:
            ContainerNotFoundError: If container not found
            DockerException: If update fails
        """
        try:
            container = self.client.containers.get(name)

            # Convert MB to bytes
            limit_bytes = limit_mb * 1024 * 1024

            # Update memory limit (also set memswap to same to disable swap)
            container.update(
                mem_limit=limit_bytes,
                memswap_limit=limit_bytes,  # Same as mem_limit = no swap
            )
            return True
        except NotFound:
            raise ContainerNotFoundError(f"Container not found: {name}")

    def is_container_running(self, name: str) -> bool:
        """Check if container is running.

        Args:
            name: Container name

        Returns:
            True if running, False otherwise
        """
        try:
            container = self.client.containers.get(name)
            return container.status == "running"
        except NotFound:
            return False

    def wait_for_healthy(
        self,
        name: str,
        timeout_seconds: int = 60,
        check_interval: float = 1.0,
    ) -> bool:
        """Wait for container to become healthy.

        Args:
            name: Container name
            timeout_seconds: Maximum wait time
            check_interval: Time between checks

        Returns:
            True if healthy within timeout, False otherwise
        """
        import time

        deadline = time.time() + timeout_seconds

        while time.time() < deadline:
            try:
                container = self.client.containers.get(name)

                # Check if running
                if container.status != "running":
                    time.sleep(check_interval)
                    continue

                # Check health status if available
                health = container.attrs.get("State", {}).get("Health", {})
                health_status = health.get("Status")

                if health_status == "healthy":
                    return True
                elif health_status is None:
                    # No healthcheck defined, consider running as healthy
                    return True

                time.sleep(check_interval)
            except NotFound:
                time.sleep(check_interval)

        return False

    def get_container_stats(self, name: str) -> dict[str, Any]:
        """Get current container statistics.

        Args:
            name: Container name

        Returns:
            Dictionary with memory, CPU, and network stats

        Raises:
            ContainerNotFoundError: If container not found
        """
        try:
            container = self.client.containers.get(name)
            stats = container.stats(stream=False)

            # Parse memory stats
            mem_stats = stats.get("memory_stats", {})
            memory_usage = mem_stats.get("usage", 0)
            memory_limit = mem_stats.get("limit", 0)

            # Parse CPU stats
            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})

            cpu_percent = 0.0
            try:
                cpu_delta = (
                    cpu_stats.get("cpu_usage", {}).get("total_usage", 0) -
                    precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
                )
                system_delta = (
                    cpu_stats.get("system_cpu_usage", 0) -
                    precpu_stats.get("system_cpu_usage", 0)
                )
                if system_delta > 0 and cpu_delta > 0:
                    cpu_percent = (cpu_delta / system_delta) * 100.0
            except (KeyError, TypeError, ZeroDivisionError):
                pass

            return {
                "memory_usage_bytes": memory_usage,
                "memory_limit_bytes": memory_limit,
                "memory_percent": (memory_usage / memory_limit * 100) if memory_limit > 0 else 0,
                "cpu_percent": cpu_percent,
            }
        except NotFound:
            raise ContainerNotFoundError(f"Container not found: {name}")

    def list_benchmark_containers(self, prefix: str = "benchmark-") -> list[ContainerInfo]:
        """List all benchmark containers.

        Args:
            prefix: Container name prefix to filter

        Returns:
            List of ContainerInfo for matching containers
        """
        result = []
        for container in self.client.containers.list(all=True):
            if container.name.startswith(prefix):
                try:
                    info = self.get_container_info(container.name)
                    result.append(info)
                except ContainerNotFoundError:
                    pass
        return result


def is_docker_available() -> bool:
    """Check if Docker daemon is available.

    Returns:
        True if Docker is available, False otherwise
    """
    try:
        client = docker.from_env()
        client.ping()
        return True
    except DockerException:
        return False
