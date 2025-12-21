"""Benchmark module for resource monitoring and metrics collection."""
from .resource_monitor import (
    ExtendedResourceMonitor,
    ResourceSample,
    DockerStatsCollector,
    HostStatsCollector,
    CloudMetadataCollector,
    EC2MetadataCollector,  # Backward compatibility alias
    create_monitor,
    get_system_info,
)

__all__ = [
    "ExtendedResourceMonitor",
    "ResourceSample",
    "DockerStatsCollector",
    "HostStatsCollector",
    "CloudMetadataCollector",
    "EC2MetadataCollector",  # Backward compatibility alias
    "create_monitor",
    "get_system_info",
]
