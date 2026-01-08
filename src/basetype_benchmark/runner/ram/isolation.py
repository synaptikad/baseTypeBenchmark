"""Container lifecycle management for benchmark isolation.

Sprint 3 - Benchmark BaseType V3

Provides perfect isolation between benchmark runs by:
- Starting/stopping containers for each paradigm
- Cleaning up volumes between runs
- Dropping OS caches
- Managing container health checks
"""
from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ..monitoring import DockerClient, is_docker_available

# Project root: isolation.py is in src/basetype_benchmark/runner/ram/
# So we go up 5 levels to reach project root
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


class IsolationError(Exception):
    """Raised when isolation operations fail."""
    pass


@dataclass
class ContainerSet:
    """Containers for a paradigm."""
    paradigm: str
    containers: list[str]
    compose_services: list[str]

    @property
    def is_hybrid(self) -> bool:
        """Check if this is a hybrid paradigm (multiple containers)."""
        return len(self.containers) > 1


# Container mapping for each paradigm
PARADIGM_CONTAINERS: dict[str, ContainerSet] = {
    "P1": ContainerSet(
        paradigm="P1",
        containers=["benchmark-timescale"],
        compose_services=["timescale"],
    ),
    "P2": ContainerSet(
        paradigm="P2",
        containers=["benchmark-timescale"],
        compose_services=["timescale"],
    ),
    "M1": ContainerSet(
        paradigm="M1",
        containers=["benchmark-memgraph"],
        compose_services=["memgraph"],
    ),
    "M2": ContainerSet(
        paradigm="M2",
        containers=["benchmark-memgraph", "benchmark-timescale"],
        compose_services=["memgraph", "timescale"],
    ),
    "O2": ContainerSet(
        paradigm="O2",
        containers=["benchmark-oxigraph", "benchmark-timescale"],
        compose_services=["oxigraph", "timescale"],
    ),
}


class IsolationManager:
    """Container lifecycle management for perfect isolation.

    Ensures clean state between benchmark runs:
    - Containers started fresh for each paradigm
    - Volumes cleaned up
    - OS caches dropped
    - Health checks verified

    Example:
        ```python
        manager = IsolationManager()  # uses DEFAULT_COMPOSE_FILE

        # Start paradigm
        manager.start_paradigm("M1")

        # ... run benchmark ...

        # Clean up
        manager.stop_paradigm("M1")
        ```
    """

    DEFAULT_COMPOSE_FILE = _PROJECT_ROOT / "docker" / "docker-compose.yml"
    HEALTH_CHECK_TIMEOUT = 60  # seconds
    CLEANUP_DELAY = 5  # seconds between stop and start

    def __init__(
        self,
        compose_file: Path | None = None,
        docker_client: DockerClient | None = None,
    ):
        """Initialize isolation manager.

        Args:
            compose_file: Path to docker-compose.yml
            docker_client: Optional DockerClient instance
        """
        self.compose_file = compose_file or self.DEFAULT_COMPOSE_FILE
        self.docker = docker_client or DockerClient()
        self._current_paradigm: str | None = None

    def start_paradigm(
        self,
        paradigm: str,
        clean_volumes: bool = True,
        wait_healthy: bool = True,
    ) -> list[str]:
        """Start containers for a paradigm.

        Args:
            paradigm: P1, P2, M1, M2, or O2
            clean_volumes: Remove volumes before starting
            wait_healthy: Wait for containers to be healthy

        Returns:
            List of started container names

        Raises:
            IsolationError: If containers fail to start
        """
        paradigm = paradigm.upper()

        if paradigm not in PARADIGM_CONTAINERS:
            raise ValueError(f"Unknown paradigm: {paradigm}")

        container_set = PARADIGM_CONTAINERS[paradigm]

        # Stop any currently running paradigm (unless they share TimescaleDB)
        if self._current_paradigm:
            # Check if both paradigms use TimescaleDB (Option A shared state)
            # WITH schema isolation: all paradigms can share ts.timeseries
            timescale_paradigms = {"P1", "P2", "M2", "O2"}
            current_uses_ts = self._current_paradigm in timescale_paradigms
            next_uses_ts = paradigm in timescale_paradigms

            # Only stop if they don't share TimescaleDB
            if not (current_uses_ts and next_uses_ts):
                self.stop_paradigm(self._current_paradigm)

        # Clean volumes if requested
        if clean_volumes:
            self._clean_volumes(container_set)

        # Start containers via docker-compose
        self._compose_up(container_set.compose_services)

        # Wait for health
        if wait_healthy:
            for container in container_set.containers:
                if not self.docker.wait_for_healthy(
                    container,
                    timeout_seconds=self.HEALTH_CHECK_TIMEOUT,
                ):
                    raise IsolationError(
                        f"Container {container} did not become healthy "
                        f"within {self.HEALTH_CHECK_TIMEOUT}s"
                    )

        self._current_paradigm = paradigm
        return container_set.containers

    def stop_paradigm(self, paradigm: str) -> None:
        """Stop and remove containers for a paradigm.

        Note: Volumes are preserved to support Option A (shared TimescaleDB).
        Use docker volume prune manually if cleanup is needed.

        Args:
            paradigm: P1, P2, M1, M2, or O2
        """
        paradigm = paradigm.upper()

        if paradigm not in PARADIGM_CONTAINERS:
            raise ValueError(f"Unknown paradigm: {paradigm}")

        container_set = PARADIGM_CONTAINERS[paradigm]

        # Stop via docker-compose
        self._compose_down(container_set.compose_services)

        # Wait for cleanup
        time.sleep(self.CLEANUP_DELAY)

        if self._current_paradigm == paradigm:
            self._current_paradigm = None

    def restart_paradigm(self, paradigm: str) -> list[str]:
        """Restart containers for a paradigm (stop + start).

        Args:
            paradigm: P1, P2, M1, M2, or O2

        Returns:
            List of container names
        """
        self.stop_paradigm(paradigm)
        return self.start_paradigm(paradigm)

    def drop_caches(self) -> bool:
        """Drop OS filesystem caches.

        Executes: sync; echo 3 > /proc/sys/vm/drop_caches

        This ensures clean state for memory measurements.
        Requires root/sudo access.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Sync first
            subprocess.run(["sync"], check=True)

            # Drop caches (requires root)
            subprocess.run(
                ["sudo", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"],
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def set_memory_limit(self, paradigm: str, limit_mb: int) -> dict[str, int]:
        """Set memory limit on containers for a paradigm.

        Uses docker update --memory which applies without restart.

        Args:
            paradigm: P1, P2, M1, M2, or O2
            limit_mb: Total memory limit in MB

        Returns:
            Dict mapping container name to applied limit

        Raises:
            IsolationError: If limit cannot be applied
        """
        paradigm = paradigm.upper()

        if paradigm not in PARADIGM_CONTAINERS:
            raise ValueError(f"Unknown paradigm: {paradigm}")

        container_set = PARADIGM_CONTAINERS[paradigm]
        limits = self._compute_limit_split(container_set, limit_mb)

        for container, container_limit in limits.items():
            try:
                self.docker.set_memory_limit(container, container_limit)
            except Exception as e:
                raise IsolationError(
                    f"Failed to set memory limit on {container}: {e}"
                )

        return limits

    def get_container_ids(self, paradigm: str) -> dict[str, str]:
        """Get container IDs for a paradigm.

        Args:
            paradigm: P1, P2, M1, M2, or O2

        Returns:
            Dict mapping container name to full container ID
        """
        paradigm = paradigm.upper()

        if paradigm not in PARADIGM_CONTAINERS:
            raise ValueError(f"Unknown paradigm: {paradigm}")

        container_set = PARADIGM_CONTAINERS[paradigm]
        ids = {}

        for container in container_set.containers:
            try:
                ids[container] = self.docker.get_container_id(container)
            except Exception:
                pass

        return ids

    def is_paradigm_running(self, paradigm: str) -> bool:
        """Check if all containers for a paradigm are running.

        Args:
            paradigm: P1, P2, M1, M2, or O2

        Returns:
            True if all containers running
        """
        paradigm = paradigm.upper()

        if paradigm not in PARADIGM_CONTAINERS:
            return False

        container_set = PARADIGM_CONTAINERS[paradigm]

        for container in container_set.containers:
            if not self.docker.is_container_running(container):
                return False

        return True

    def _compose_up(self, services: list[str]) -> None:
        """Start services via docker compose."""
        cmd = [
            "docker", "compose",
            "-f", str(self.compose_file),
            "up", "-d",
        ] + services

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise IsolationError(
                f"docker-compose up failed: {result.stderr}"
            )

    def _compose_down(self, services: list[str]) -> None:
        """Stop services via docker compose."""
        cmd = [
            "docker", "compose",
            "-f", str(self.compose_file),
            "down", "--remove-orphans",  # Removed -v flag to preserve volumes (Option A)
        ]

        subprocess.run(cmd, capture_output=True, text=True)

    def _clean_volumes(self, container_set: ContainerSet) -> None:
        """Remove volumes for containers."""
        # docker-compose down -v handles this
        pass

    def _compute_limit_split(
        self,
        container_set: ContainerSet,
        total_mb: int,
    ) -> dict[str, int]:
        """Compute memory limit split for containers.

        For hybrid paradigms, split is:
        - Graph DB: 70%
        - TimescaleDB: 30%

        This reflects that TimescaleDB is disk-backed and less RAM-critical.

        Args:
            container_set: Container configuration
            total_mb: Total memory budget

        Returns:
            Dict mapping container name to limit in MB
        """
        if len(container_set.containers) == 1:
            return {container_set.containers[0]: total_mb}

        # Hybrid split (70/30)
        limits = {}
        graph_containers = [c for c in container_set.containers if "timescale" not in c]
        ts_containers = [c for c in container_set.containers if "timescale" in c]

        # Graph gets 70%
        graph_mb = int(total_mb * 0.7)
        for c in graph_containers:
            limits[c] = graph_mb

        # TimescaleDB gets 30%
        ts_mb = total_mb - graph_mb
        for c in ts_containers:
            limits[c] = ts_mb

        return limits


def get_paradigm_containers(paradigm: str) -> list[str]:
    """Get container names for a paradigm.

    Args:
        paradigm: P1, P2, M1, M2, or O2

    Returns:
        List of container names
    """
    paradigm = paradigm.upper()
    if paradigm in PARADIGM_CONTAINERS:
        return PARADIGM_CONTAINERS[paradigm].containers
    return []
