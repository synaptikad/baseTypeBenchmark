"""Bulk loaders for Benchmark Runner V3.

Sprint 2 - Benchmark BaseType V3

Loaders disponibles:
- PostgresLoader: P1 (relationnel) et P2 (JSONB)
- MemgraphLoader: M1 (standalone) et M2 (+ TimescaleDB)

Exemple d'utilisation:
    ```python
    from src.basetype_benchmark.runner.loaders import get_loader
    from src.basetype_benchmark.runner.config import get_config

    config = get_config("P1")
    loader = get_loader("P1", config)

    result = loader.load_all(
        data_dir=Path("data/export/p1"),
        workers=16,
    )
    ```
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from .base import (
    BaseLoader,
    BulkLoader,
    LoadPhase,
    LoadProgress,
    LoadResult,
    ProgressCallback,
    TimeseriesDependencyResult,
    TimeseriesDependencyStatus,
)
from .memgraph import MemgraphLoader
from .postgres import PostgresLoader
from .progress import (
    LoadProgressDisplay,
    print_simple_result,
    verbose_callback,
)

if TYPE_CHECKING:
    from ..config import (
        MemgraphConfig,
        PostgresConfig,
    )

__all__ = [
    # Base types
    "BaseLoader",
    "BulkLoader",
    "LoadPhase",
    "LoadProgress",
    "LoadResult",
    "ProgressCallback",
    "TimeseriesDependencyResult",
    "TimeseriesDependencyStatus",
    # Loaders
    "PostgresLoader",
    "MemgraphLoader",
    # Progress display
    "LoadProgressDisplay",
    "print_simple_result",
    "verbose_callback",
    # Factory
    "get_loader",
]

# Paradigm type
Paradigm = Literal["P1", "P2", "M1", "M2"]


def get_loader(
    paradigm: Paradigm,
    primary_config: "PostgresConfig | MemgraphConfig",
    timescale_config: "PostgresConfig | None" = None,
) -> BulkLoader:
    """Factory pour obtenir le loader adapte au paradigme.

    Args:
        paradigm: P1, P2, M1, ou M2
        primary_config: Configuration de la base principale
        timescale_config: Configuration TimescaleDB pour M2

    Returns:
        BulkLoader configure

    Raises:
        ValueError: Si paradigme invalide

    Exemple:
        ```python
        from src.basetype_benchmark.runner.config import PostgresConfig

        config = PostgresConfig(
            host="localhost",
            port=5432,
            database="benchmark_p1",
        )
        loader = get_loader("P1", config)
        ```
    """
    paradigm = paradigm.upper()

    if paradigm in ("P1", "P2"):
        if not hasattr(primary_config, "dsn"):
            raise TypeError(f"PostgresConfig required for {paradigm}")
        return PostgresLoader(
            config=primary_config,  # type: ignore
            paradigm=paradigm,  # type: ignore
        )

    elif paradigm in ("M1", "M2"):
        if not hasattr(primary_config, "uri"):
            raise TypeError(f"MemgraphConfig required for {paradigm}")
        return MemgraphLoader(
            config=primary_config,  # type: ignore
            paradigm=paradigm,  # type: ignore
            timescale_config=timescale_config,
        )

    else:
        raise ValueError(
            f"Unknown paradigm: {paradigm}. "
            f"Valid options: P1, P2, M1, M2"
        )
