"""Resource monitoring for Benchmark Runner V3.

Sprint 3 - Benchmark BaseType V3

Provides Linux cgroups v2 based monitoring for accurate memory measurement
during benchmark execution.

Components:
- CgroupsV2Monitor: Direct cgroups v2 reading
- DockerClient: Docker SDK wrapper for container management
- MetricsSampler: Background thread sampling

Example:
    ```python
    from basetype_benchmark.runner.monitoring import (
        MetricsSampler,
        DockerClient,
        is_cgroups_v2_available,
    )

    if is_cgroups_v2_available():
        client = DockerClient()
        container_id = client.get_container_id("benchmark-memgraph")

        sampler = MetricsSampler(container_id)
        sampler.start()

        # ... run queries ...

        result = sampler.stop()
        print(f"Peak: {result.memory_peak_mb:.1f} MB")
    ```
"""
from __future__ import annotations

from .cgroups import (
    CgroupsV2Monitor,
    CgroupsNotFoundError,
    CgroupsNotSupportedError,
    MemoryStats,
    is_cgroups_v2_available,
    get_container_cgroup_path,
)
from .docker_client import (
    DockerClient,
    ContainerInfo,
    ContainerNotFoundError,
    DockerNotAvailableError,
    is_docker_available,
)
from .sampler import (
    MetricsSampler,
    MultiContainerSampler,
    Sample,
    SamplingResult,
)

__all__ = [
    # cgroups
    "CgroupsV2Monitor",
    "CgroupsNotFoundError",
    "CgroupsNotSupportedError",
    "MemoryStats",
    "is_cgroups_v2_available",
    "get_container_cgroup_path",
    # docker
    "DockerClient",
    "ContainerInfo",
    "ContainerNotFoundError",
    "DockerNotAvailableError",
    "is_docker_available",
    # sampler
    "MetricsSampler",
    "MultiContainerSampler",
    "Sample",
    "SamplingResult",
]
