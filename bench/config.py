"""
Configuration centralisée du runner de benchmark.
Toutes les constantes sont exprimées en unités SI et peuvent être surchargées via les variables d'environnement.
"""
from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Dict, List


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


SEED = _get_env_int("BENCH_SEED", 42)
random.seed(SEED)

SCALE_MODE = os.getenv("BENCH_SCALE_MODE", "laptop")
N_RUNS = _get_env_int("BENCH_N_RUNS", 10)
N_WARMUP = _get_env_int("BENCH_N_WARMUP", 3)
TIMEOUT_S = float(os.getenv("BENCH_TIMEOUT_S", "30"))

ACTIVE_QUERIES: Dict[str, List[str]] = {
    "pg": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"],
    "memgraph": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q8"],
    "oxigraph": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q8"],
}


@dataclass
class Profile:
    name: str
    engine: str
    type: str
    endpoint: str
    container: str | None
    volume: str | None
    ingestion: dict | None
    queries: dict

    @classmethod
    def from_mapping(cls, name: str, data: dict) -> "Profile":
        return cls(
            name=name,
            engine=data.get("engine", name),
            type=data["type"],
            endpoint=data.get("endpoint", ""),
            container=data.get("container"),
            volume=data.get("volume"),
            ingestion=data.get("ingestion"),
            queries=data.get("queries", {}),
        )
