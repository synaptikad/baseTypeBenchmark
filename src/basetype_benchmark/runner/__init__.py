"""
Runner - Benchmark BaseType V3
Parquet-first query execution and cross-paradigm validation.

2025 Best Practices:
- Parquet streaming for bulk loading
- Async everywhere (psycopg3, httpx, asyncio)
- Modern Python (Pydantic, Typer, Polars)
- Protocol-based runners for type safety
"""

from .config import (
    EngineType,
    ParadigmStatus,
    QueryCategory,
    DatasetProfile,
    DatasetSizeEstimate,
    EngineProfile,
    ENGINE_PROFILES,
    DATASET_SIZE_ESTIMATES,
)
from .core import (
    QueryCatalog,
    QueryDefinition,
    QueryPlan,
    QueryResult,
    BatchResult,
    DryRunResult,
    DryRunBatch,
    ExecutionStatus,
    get_catalog,
    get_query,
    get_query_parameters,
)
from .cli import app as cli_app

__all__ = [
    # Config
    "EngineType",
    "ParadigmStatus",
    "QueryCategory",
    "DatasetProfile",
    "DatasetSizeEstimate",
    "EngineProfile",
    "ENGINE_PROFILES",
    "DATASET_SIZE_ESTIMATES",
    # Core
    "QueryCatalog",
    "QueryDefinition",
    "QueryPlan",
    "QueryResult",
    "BatchResult",
    "DryRunResult",
    "DryRunBatch",
    "ExecutionStatus",
    "get_catalog",
    "get_query",
    "get_query_parameters",
    # CLI
    "cli_app",
]
