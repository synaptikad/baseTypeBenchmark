"""Resource metrics collection for Docker containers.

This module provides:
- Metrics: Point-in-time container resource snapshot
- MetricsCollector strategies: per_query vs aggregate
- ResourceMonitor: Background continuous monitoring
- Low-level cgroup v2 functions

Backward compatible with previous metrics.py imports:
    from basetype_benchmark.runner.metrics import Metrics, check_oom, compute_delta
"""

# Import from local sub-modules
from .snapshot import Metrics
from .utils import check_oom, compute_delta, get_peak_memory_mb
from .strategies import (
    MetricsCollector,
    PerQueryCollector,
    AggregateCollector,
    QueryMetrics,
    create_collector,
)
from .monitor import ResourceMonitor, ResourceSnapshot, ResourceStats
from .cgroup import (
    get_cgroup_path,
    read_memory_current,
    read_memory_peak,
    reset_memory_peak,
    read_cpu_usage,
    get_cgroup_metrics,
    IS_LINUX,
)

__all__ = [
    # Backward compatible exports
    "Metrics",
    "check_oom",
    "compute_delta",
    "get_peak_memory_mb",
    # New strategies
    "MetricsCollector",
    "PerQueryCollector",
    "AggregateCollector",
    "QueryMetrics",
    "create_collector",
    # Monitor
    "ResourceMonitor",
    "ResourceSnapshot",
    "ResourceStats",
    # Low-level (for advanced use)
    "get_cgroup_path",
    "read_memory_current",
    "read_memory_peak",
    "reset_memory_peak",
    "read_cpu_usage",
    "get_cgroup_metrics",
    "IS_LINUX",
]
