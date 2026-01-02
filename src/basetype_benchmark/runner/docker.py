"""Docker container management for benchmark execution."""

import os
import subprocess
import time
from pathlib import Path
from typing import List, Optional


def _find_docker_dir() -> Path:
    """Find docker directory relative to repo root."""
    # Try multiple approaches to find repo root
    candidates = [
        # From runner module: runner/docker.py -> runner(0), basetype_benchmark(1), src(2), repo(3)
        Path(__file__).parent.parent.parent.parent / "docker",
        # From current working directory
        Path.cwd() / "docker",
        # If we're in a subdirectory of the repo
        Path.cwd().parent / "docker",
        Path.cwd().parent.parent / "docker",
    ]

    for candidate in candidates:
        if candidate.exists() and (candidate / "docker-compose.yml").exists():
            return candidate

    # Fallback - assume cwd is repo root
    return Path.cwd() / "docker"


# Docker compose directory
DOCKER_DIR = _find_docker_dir()

# Container names
CONTAINERS = {
    "timescaledb": "btb_timescaledb",
    "memgraph": "btb_memgraph",
    "oxigraph": "btb_oxigraph",
}

# Containers needed per scenario
SCENARIO_CONTAINERS = {
    "P1": ["timescaledb"],
    "P2": ["timescaledb"],
    "M1": ["memgraph"],
    "M2": ["memgraph", "timescaledb"],
    "O1": ["oxigraph"],
    "O2": ["oxigraph", "timescaledb"],
}


def _get_docker_compose_cmd() -> str:
    """Detect available docker compose command."""
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return "docker compose"
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["docker-compose", "version"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return "docker-compose"
    except Exception:
        pass

    return "docker compose"


DOCKER_COMPOSE = _get_docker_compose_cmd()


def stop_all() -> None:
    """Stop all benchmark containers."""
    subprocess.run(
        f"{DOCKER_COMPOSE} down",
        shell=True,
        cwd=str(DOCKER_DIR),
        capture_output=True
    )


def start(scenario: str, ram_gb: int, wait_s: int = 10, data_dir: Path = None) -> bool:
    """Start containers for a scenario with RAM limit.

    Args:
        scenario: P1, P2, M1, M2, O1, O2
        ram_gb: RAM limit in GB
        wait_s: Seconds to wait for containers to initialize
        data_dir: Directory containing data files (mounted as /data in container)

    Returns:
        True if containers started successfully
    """
    stop_all()

    containers = SCENARIO_CONTAINERS.get(scenario.upper(), [])
    if not containers:
        print(f"[ERROR] Unknown scenario: {scenario}")
        return False

    # Set environment for docker-compose
    env = os.environ.copy()
    env["MEMORY_LIMIT"] = f"{ram_gb}g"
    if data_dir:
        env["BTB_DATA_DIR"] = str(data_dir.resolve())

    # Start containers
    container_names = " ".join(containers)
    result = subprocess.run(
        f"{DOCKER_COMPOSE} up -d {container_names}",
        shell=True,
        cwd=str(DOCKER_DIR),
        env=env,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"[ERROR] Failed to start containers: {result.stderr}")
        return False

    # Wait for containers to initialize
    time.sleep(wait_s)
    return True


def prune_volumes(scenario: str) -> None:
    """Remove Docker volumes for a scenario to free memory.

    Args:
        scenario: P1, P2, M1, M2, O1, O2
    """
    stop_all()

    # Remove volumes
    subprocess.run(
        f"{DOCKER_COMPOSE} down -v",
        shell=True,
        cwd=str(DOCKER_DIR),
        capture_output=True
    )


def get_container_name(service: str) -> str:
    """Get container name for a service."""
    return CONTAINERS.get(service, f"btb_{service}")


def is_container_running(container_name: str) -> bool:
    """Check if a container is running."""
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
        capture_output=True,
        text=True
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def run_in_container(
    container_name: str,
    argv: List[str],
    check: bool = False,
    timeout_s: Optional[int] = None,
) -> subprocess.CompletedProcess:
    """Run a command inside a running container via `docker exec`.

    Args:
        container_name: Docker container name (e.g., btb_timescaledb)
        argv: Command argv list, e.g. ["bash", "-lc", "echo hi"]
        check: If True, raise CalledProcessError on non-zero exit
        timeout_s: Optional timeout

    Returns:
        CompletedProcess with stdout/stderr captured.
    """
    cmd = ["docker", "exec", "-i", container_name, *argv]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=check,
        timeout=timeout_s,
    )
