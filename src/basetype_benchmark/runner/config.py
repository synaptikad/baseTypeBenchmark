"""Configuration models for Benchmark Runner V3.

Specifications EXACTES basees sur les fichiers YAML sources:
- queries/catalog.yaml (categories, paradigm_status)
- data/generated/{profile}/queries_params.yaml (parametres)
- src/basetype_benchmark/schema/data_model.yaml (types)
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator
import yaml


# =============================================================================
# ENUMS - Valeurs EXACTES des YAML sources
# =============================================================================

class EngineType(str, Enum):
    """Les 5 paradigmes du benchmark."""
    P1 = "P1"  # PostgreSQL Relational
    P2 = "P2"  # PostgreSQL JSONB
    M1 = "M1"  # Memgraph Standalone
    M2 = "M2"  # Memgraph + TimescaleDB
    O2 = "O2"  # Oxigraph + TimescaleDB


class QueryCategory(str, Enum):
    """Categories de queries (catalog.yaml:11-29)."""
    GRAPH_ONLY = "graph_only"           # Q1-Q5
    TIMESERIES_PURE = "timeseries_pure" # Q6
    HYBRID = "hybrid"                   # Q7-Q13
    JSONB_SPECIFIC = "jsonb_specific"   # Q14-Q19
    GRAPH_NATIVE = "graph_native"       # Q20-Q23
    WRITE_WORKLOAD = "write_workload"   # QW1-QW3


class ParadigmStatus(str, Enum):
    """Status paradigme (catalog.yaml:975-979)."""
    NATIVE = "NATIVE"               # Supporte nativement avec performance optimale
    DEGRADED = "DEGRADED"           # Possible mais avec limitations
    VERY_DEGRADED = "VERY_DEGRADED" # Possible mais complexite elevee
    IMPOSSIBLE = "IMPOSSIBLE"       # Non supporte par le paradigme


class DatasetProfile(str, Enum):
    """Profils de taille de dataset."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"


# =============================================================================
# Engine Profiles (RAM characteristics)
# =============================================================================

class EngineProfile(BaseModel):
    """Profil RAM d'un moteur.

    Note: RAM requirements are measured via cgroups v2, not estimated.
    The multipliers have been removed - we measure actual memory.peak.
    """
    engine: EngineType
    is_in_memory: bool = Field(description="Stocke toutes les donnees en RAM")
    base_overhead_mb: int = Field(ge=0, description="Overhead RAM de base (MB)")
    timeseries_in_memory: bool = Field(default=False, description="Timeseries en RAM")
    can_oom: bool = Field(default=False, description="Engine peut OOM si RAM insuffisante")


ENGINE_PROFILES: dict[EngineType, EngineProfile] = {
    EngineType.P1: EngineProfile(
        engine=EngineType.P1,
        is_in_memory=False,
        base_overhead_mb=256,
        can_oom=False,
    ),
    EngineType.P2: EngineProfile(
        engine=EngineType.P2,
        is_in_memory=False,
        base_overhead_mb=256,
        can_oom=False,
    ),
    EngineType.M1: EngineProfile(
        engine=EngineType.M1,
        is_in_memory=True,
        base_overhead_mb=512,
        timeseries_in_memory=True,
        can_oom=True,
    ),
    EngineType.M2: EngineProfile(
        engine=EngineType.M2,
        is_in_memory=True,
        base_overhead_mb=512,
        timeseries_in_memory=False,
        can_oom=True,
    ),
    EngineType.O2: EngineProfile(
        engine=EngineType.O2,
        is_in_memory=False,
        base_overhead_mb=128,
        can_oom=False,
    ),
}


# =============================================================================
# Dataset Size Estimates (avec node_count, edge_count, timeseries_rows)
# =============================================================================

class DatasetSizeEstimate(BaseModel):
    """Estimation de taille d'un dataset."""
    profile: DatasetProfile
    duration: str = Field(description="Duree: 2d, 1w, 1m, 6m")
    node_count: int = Field(ge=0, description="Nombre de noeuds")
    edge_count: int = Field(ge=0, description="Nombre d'aretes")
    timeseries_rows: int = Field(ge=0, description="Nombre de lignes timeseries")
    structure_mb: int = Field(ge=0, description="Taille structure en MB")
    timeseries_mb: int = Field(ge=0, description="Taille timeseries en MB")

    @property
    def total_mb(self) -> int:
        """Taille totale estimee."""
        return self.structure_mb + self.timeseries_mb

    @property
    def key(self) -> str:
        """Cle unique pour cette estimation."""
        return f"{self.profile.value}-{self.duration}"


DATASET_SIZE_ESTIMATES: dict[str, DatasetSizeEstimate] = {
    # Small (1 building, ~1300 nodes, ~1000 points)
    "small-2d": DatasetSizeEstimate(
        profile=DatasetProfile.SMALL, duration="2d",
        node_count=1300, edge_count=1500, timeseries_rows=288_000,
        structure_mb=5, timeseries_mb=50
    ),
    "small-1w": DatasetSizeEstimate(
        profile=DatasetProfile.SMALL, duration="1w",
        node_count=1300, edge_count=1500, timeseries_rows=1_008_000,
        structure_mb=5, timeseries_mb=175
    ),
    "small-1m": DatasetSizeEstimate(
        profile=DatasetProfile.SMALL, duration="1m",
        node_count=1300, edge_count=1500, timeseries_rows=4_320_000,
        structure_mb=5, timeseries_mb=750
    ),

    # Medium (10 buildings, ~13k nodes, ~10k points)
    "medium-2d": DatasetSizeEstimate(
        profile=DatasetProfile.MEDIUM, duration="2d",
        node_count=13000, edge_count=15000, timeseries_rows=2_880_000,
        structure_mb=50, timeseries_mb=500
    ),
    "medium-1w": DatasetSizeEstimate(
        profile=DatasetProfile.MEDIUM, duration="1w",
        node_count=13000, edge_count=15000, timeseries_rows=10_080_000,
        structure_mb=50, timeseries_mb=1750
    ),
    "medium-1m": DatasetSizeEstimate(
        profile=DatasetProfile.MEDIUM, duration="1m",
        node_count=13000, edge_count=15000, timeseries_rows=43_200_000,
        structure_mb=50, timeseries_mb=7500
    ),
    "medium-6m": DatasetSizeEstimate(
        profile=DatasetProfile.MEDIUM, duration="6m",
        node_count=13000, edge_count=15000, timeseries_rows=259_200_000,
        structure_mb=50, timeseries_mb=45000
    ),

    # Large (100 buildings, ~130k nodes, ~100k points)
    "large-2d": DatasetSizeEstimate(
        profile=DatasetProfile.LARGE, duration="2d",
        node_count=130000, edge_count=150000, timeseries_rows=28_800_000,
        structure_mb=500, timeseries_mb=5000
    ),
    "large-1w": DatasetSizeEstimate(
        profile=DatasetProfile.LARGE, duration="1w",
        node_count=130000, edge_count=150000, timeseries_rows=100_800_000,
        structure_mb=500, timeseries_mb=17500
    ),
    "large-1m": DatasetSizeEstimate(
        profile=DatasetProfile.LARGE, duration="1m",
        node_count=130000, edge_count=150000, timeseries_rows=432_000_000,
        structure_mb=500, timeseries_mb=75000
    ),

    # XLarge (stress test, ~400k nodes, ~500k points)
    "xlarge-2d": DatasetSizeEstimate(
        profile=DatasetProfile.XLARGE, duration="2d",
        node_count=400000, edge_count=500000, timeseries_rows=144_000_000,
        structure_mb=1500, timeseries_mb=25000
    ),
    "xlarge-1w": DatasetSizeEstimate(
        profile=DatasetProfile.XLARGE, duration="1w",
        node_count=400000, edge_count=500000, timeseries_rows=504_000_000,
        structure_mb=1500, timeseries_mb=87500
    ),
    "xlarge-6m": DatasetSizeEstimate(
        profile=DatasetProfile.XLARGE, duration="6m",
        node_count=400000, edge_count=500000, timeseries_rows=2_592_000_000,
        structure_mb=1500, timeseries_mb=450000
    ),
}


# =============================================================================
# Connection Configuration
# =============================================================================

class PostgresConfig(BaseModel):
    """PostgreSQL connection configuration."""
    dsn: str = Field(
        default="postgresql://postgres:benchmark@localhost:5432/benchmark",
        description="PostgreSQL DSN"
    )
    pool_size: int = Field(default=5, ge=1, le=50)
    timeout_seconds: int = Field(default=300, ge=1)


class MemgraphConfig(BaseModel):
    """Memgraph connection configuration."""
    uri: str = Field(default="bolt://localhost:7687", description="Bolt URI")
    auth: Optional[tuple[str, str]] = Field(default=None)
    timeout_seconds: int = Field(default=300, ge=1)


class OxigraphConfig(BaseModel):
    """Oxigraph connection configuration."""
    query_endpoint: str = Field(
        default="http://localhost:7878/query",
        description="SPARQL query endpoint"
    )
    update_endpoint: str = Field(
        default="http://localhost:7878/update",
        description="SPARQL update endpoint"
    )
    db_path: Optional[Path] = Field(default=None, description="Path to Oxigraph database")
    timeout_seconds: int = Field(default=300, ge=1)


class HybridConfig(BaseModel):
    """Hybrid paradigm configuration (M2, O2)."""
    graph: MemgraphConfig | OxigraphConfig
    timeseries: PostgresConfig


class ParadigmConfig(BaseModel):
    """Configuration for a specific paradigm."""
    type: str = Field(description="Paradigm type: postgresql, memgraph, oxigraph, hybrid")
    config: PostgresConfig | MemgraphConfig | OxigraphConfig | HybridConfig


# =============================================================================
# Execution Configuration
# =============================================================================

class ExecutionConfig(BaseModel):
    """Benchmark execution configuration."""
    timeout_seconds: int = Field(default=300, ge=1)
    warmup_runs: int = Field(default=3, ge=0)
    timed_runs: int = Field(default=10, ge=1)
    collect_metrics: bool = Field(default=True)
    validate_results: bool = Field(default=True)


class RAMGradientConfig(BaseModel):
    """RAM gradient testing configuration."""
    levels_mb: list[int] = Field(
        default=[512, 1024, 2048, 4096, 8192, 16384, 32768],
        description="RAM levels to test in MB"
    )
    warmup_after_limit: bool = Field(default=True)
    detect_oom_early: bool = Field(default=True)


# =============================================================================
# Main Benchmark Configuration
# =============================================================================

class BenchmarkConfig(BaseModel):
    """Complete benchmark configuration."""
    paradigms: dict[EngineType, ParadigmConfig] = Field(default_factory=dict)
    profiles: dict[str, Path] = Field(default_factory=dict)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    ram_gradient: RAMGradientConfig = Field(default_factory=RAMGradientConfig)

    @classmethod
    def from_yaml(cls, path: Path) -> "BenchmarkConfig":
        """Load configuration from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)


# =============================================================================
# Utility Functions
# =============================================================================

def get_engine_profile(engine: EngineType) -> EngineProfile:
    """Get the RAM profile for an engine."""
    return ENGINE_PROFILES[engine]


def get_dataset_estimate(profile: str, duration: str) -> Optional[DatasetSizeEstimate]:
    """Get the size estimate for a dataset configuration."""
    key = f"{profile}-{duration}"
    return DATASET_SIZE_ESTIMATES.get(key)


def get_measured_ram(paradigm: str, results_file: Optional[Path] = None) -> Optional[int]:
    """Get RAM_viable from actual benchmark measurements.

    RAM requirements are measured via cgroups v2 memory.peak during
    benchmark execution, not estimated. This function retrieves
    previously measured values.

    Args:
        paradigm: Paradigm ID (P1, P2, M1, M2, O2)
        results_file: Path to results.json from benchmark run

    Returns:
        Measured RAM_viable in MB, or None if not yet measured
    """
    if results_file is None:
        return None

    if not results_file.exists():
        return None

    import json
    try:
        with open(results_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        results = data.get("results", {})
        paradigm_data = results.get(paradigm, {})
        return paradigm_data.get("ram_viable_mb")
    except Exception:
        return None
