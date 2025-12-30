"""Benchmark results handling - JSON export."""

import json
import statistics
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class QueryResult:
    """Results for a single query."""
    query_id: str
    latencies_ms: List[float] = field(default_factory=list)
    rows: int = 0
    variants: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def p50_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        return statistics.median(self.latencies_ms)

    @property
    def p95_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_lat = sorted(self.latencies_ms)
        idx = int(len(sorted_lat) * 0.95)
        return sorted_lat[min(idx, len(sorted_lat) - 1)]

    @property
    def avg_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        return sum(self.latencies_ms) / len(self.latencies_ms)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_id": self.query_id,
            "latencies_ms": self.latencies_ms,
            "p50_ms": round(self.p50_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            "avg_ms": round(self.avg_ms, 2),
            "rows": self.rows,
            "variants": self.variants,
            "errors": self.errors,
        }

    def to_summary(self) -> Dict[str, Any]:
        return {
            "p50_ms": round(self.p50_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            "rows": self.rows,
        }


@dataclass
class LoadResult:
    """Results for data loading phase."""
    duration_s: float = 0.0
    nodes: int = 0
    edges: int = 0
    timeseries_rows: int = 0
    peak_ram_mb: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "duration_s": round(self.duration_s, 2),
            "nodes": self.nodes,
            "edges": self.edges,
            "timeseries_rows": self.timeseries_rows,
            "peak_ram_mb": round(self.peak_ram_mb, 1),
            "error": self.error,
        }


@dataclass
class BenchmarkResult:
    """Complete benchmark result for a scenario run."""
    scenario: str
    profile: str
    ram_gb: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"  # pending, running, completed, failed
    load: LoadResult = field(default_factory=LoadResult)
    queries: Dict[str, QueryResult] = field(default_factory=dict)
    error: Optional[str] = None
    system_info: Dict[str, Any] = field(default_factory=dict)

    @property
    def global_p95_ms(self) -> float:
        """Global p95 across all queries."""
        all_latencies = []
        for qr in self.queries.values():
            all_latencies.extend(qr.latencies_ms)
        if not all_latencies:
            return 0.0
        sorted_lat = sorted(all_latencies)
        idx = int(len(sorted_lat) * 0.95)
        return sorted_lat[min(idx, len(sorted_lat) - 1)]

    def to_full_dict(self) -> Dict[str, Any]:
        """Full result with all details."""
        return {
            "scenario": self.scenario,
            "profile": self.profile,
            "ram_gb": self.ram_gb,
            "timestamp": self.timestamp,
            "status": self.status,
            "system_info": self.system_info,
            "load": self.load.to_dict(),
            "queries": {qid: qr.to_dict() for qid, qr in self.queries.items()},
            "global_p95_ms": round(self.global_p95_ms, 2),
            "error": self.error,
        }

    def to_summary_dict(self) -> Dict[str, Any]:
        """Summary result for quick analysis."""
        return {
            "scenario": self.scenario,
            "profile": self.profile,
            "ram_gb": self.ram_gb,
            "load_s": round(self.load.duration_s, 2),
            "queries": {qid: qr.to_summary() for qid, qr in self.queries.items()},
            "global_p95_ms": round(self.global_p95_ms, 2),
            "status": self.status,
        }


def save_results(result: BenchmarkResult, output_dir: Path) -> tuple[Path, Path]:
    """Save benchmark results to JSON files.

    Args:
        result: Benchmark result
        output_dir: Output directory

    Returns:
        Tuple of (full_path, summary_path)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{result.scenario}_{result.profile}_{result.ram_gb}GB"
    full_path = output_dir / f"{base_name}_full.json"
    summary_path = output_dir / f"{base_name}_summary.json"

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(result.to_full_dict(), f, indent=2)

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result.to_summary_dict(), f, indent=2)

    return full_path, summary_path
