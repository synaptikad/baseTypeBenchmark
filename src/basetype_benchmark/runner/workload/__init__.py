"""Workload scenarios for stress testing.

This module provides workload-based testing that simulates realistic
middleware usage patterns:

- dashboard_refresh: Read-heavy dashboard simulation
- iot_ingestion: Write-heavy IoT gateway
- mixed_middleware: 50/50 read/write
- bos_twin: BOS digital twin with graph + high-freq ingestion
- graph_stress: Graph traversal intensive
- timeseries_stress: TS aggregation intensive

Unlike the simple benchmark (isolated queries with RAM gradient),
workloads run query sequences with:
- No state reset between queries
- Optional looping with duration limits
- Focus on throughput (QPS) metrics
"""

from .models import (
    QueryStats,
    QueryStep,
    WorkloadProfile,
    WorkloadResult,
    WorkloadResults,
    WorkloadScenario,
)

from .loader import (
    get_workload,
    get_workload_info,
    list_workloads,
    load_or_get_workload,
    load_workload_from_yaml,
    save_workload_to_yaml,
    WORKLOADS,
    WORKLOAD_INFO,
)

from .executor import (
    WorkloadExecutor,
    WorkloadOrchestrator,
)

__all__ = [
    # Models
    "QueryStats",
    "QueryStep",
    "WorkloadProfile",
    "WorkloadResult",
    "WorkloadResults",
    "WorkloadScenario",
    # Loader
    "get_workload",
    "get_workload_info",
    "list_workloads",
    "load_or_get_workload",
    "load_workload_from_yaml",
    "save_workload_to_yaml",
    "WORKLOADS",
    "WORKLOAD_INFO",
    # Executor
    "WorkloadExecutor",
    "WorkloadOrchestrator",
]
