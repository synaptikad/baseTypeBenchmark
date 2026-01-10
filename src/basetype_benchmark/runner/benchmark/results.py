"""Benchmark results aggregation and export.

Sprint 3 - Benchmark BaseType V3

Provides structured results storage and JSON export for benchmark data.
Output format matches the specification in papier.md Section 4.

Key metrics:
- RAM_viable: Smallest RAM without OOM
- RAM_perf: RAM where latency stabilizes
- Latencies: p50, p95, min, max, stddev
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class BenchmarkConfig:
    """Configuration used for benchmark run."""
    paradigms: list[str]
    queries: list[str]
    data_profile: str
    ram_levels_mb: list[int]
    n_warmup: int
    n_runs: int
    n_variants: int
    timeout_seconds: float

    def to_dict(self) -> dict:
        return {
            "paradigms": self.paradigms,
            "queries": self.queries,
            "data_profile": self.data_profile,
            "ram_levels_mb": self.ram_levels_mb,
            "n_warmup": self.n_warmup,
            "n_runs": self.n_runs,
            "n_variants": self.n_variants,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass
class QueryResult:
    """Results for a single query.

    Includes both performance metrics and validation data for cross-paradigm comparison.
    """
    query_id: str
    # Performance metrics
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    avg_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    stddev_ms: float = 0.0
    success_rate: float = 1.0
    memory_peak_mb: float = 0.0
    run_count: int = 0

    # Validation data (for cross-paradigm comparison)
    row_count: int = 0                              # Total rows returned
    sample_rows: list[dict[str, Any]] | None = None # First N rows for comparison
    row_hash: str | None = None                     # SHA256 of full result for integrity
    column_names: list[str] | None = None           # Column names returned

    def to_dict(self) -> dict:
        result = {
            "query_id": self.query_id,
            "p50_ms": round(self.p50_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            "avg_ms": round(self.avg_ms, 2),
            "min_ms": round(self.min_ms, 2),
            "max_ms": round(self.max_ms, 2),
            "stddev_ms": round(self.stddev_ms, 2),
            "success_rate": round(self.success_rate, 3),
            "memory_peak_mb": round(self.memory_peak_mb, 1),
            "run_count": self.run_count,
            # Validation data
            "row_count": self.row_count,
        }
        # Only include validation fields if populated
        if self.sample_rows is not None:
            result["sample_rows"] = self.sample_rows
        if self.row_hash is not None:
            result["row_hash"] = self.row_hash
        if self.column_names is not None:
            result["column_names"] = self.column_names
        return result


@dataclass
class LevelResult:
    """Results for a single RAM level."""
    limit_mb: int
    status: str  # success, oom, timeout, error
    actual_peak_mb: float = 0.0
    duration_seconds: float = 0.0
    queries: dict[str, QueryResult] = field(default_factory=dict)
    error_message: str | None = None

    def to_dict(self) -> dict:
        return {
            "limit_mb": self.limit_mb,
            "status": self.status,
            "actual_peak_mb": round(self.actual_peak_mb, 1),
            "duration_seconds": round(self.duration_seconds, 1),
            "queries": {qid: q.to_dict() for qid, q in self.queries.items()},
            "error_message": self.error_message,
        }


@dataclass
class ParadigmResults:
    """Results for a single paradigm."""
    paradigm: str
    levels: list[LevelResult] = field(default_factory=list)
    baseline_peak_mb: float = 0.0

    @property
    def ram_viable_mb(self) -> int | None:
        """Smallest RAM without OOM."""
        successful = [l for l in self.levels if l.status == "success"]
        if not successful:
            return None
        return min(l.limit_mb for l in successful)

    @property
    def ram_baseline_mb(self) -> float:
        """Baseline RAM usage."""
        return self.baseline_peak_mb

    def to_dict(self) -> dict:
        return {
            "paradigm": self.paradigm,
            "ram_viable_mb": self.ram_viable_mb,
            "ram_baseline_mb": round(self.baseline_peak_mb, 1),
            "levels": [l.to_dict() for l in self.levels],
        }


@dataclass
class BenchmarkResults:
    """Complete benchmark results.

    Structure matches papier.md Section 4.3 JSON output format.
    """
    benchmark_id: str = ""
    config: BenchmarkConfig | None = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    results: dict[str, ParadigmResults] = field(default_factory=dict)

    def __post_init__(self):
        if not self.benchmark_id:
            self.benchmark_id = self.start_time.strftime("%Y-%m-%d_%H%M%S")

    def add_paradigm_results(
        self,
        paradigm: str,
        results: ParadigmResults,
    ) -> None:
        """Add results for a paradigm."""
        self.results[paradigm] = results

    def get_ram_viable(self, paradigm: str) -> int | None:
        """Get smallest viable RAM for a paradigm."""
        if paradigm in self.results:
            return self.results[paradigm].ram_viable_mb
        return None

    def get_summary(self) -> dict:
        """Get summary of results."""
        return {
            "ram_viable": {
                p: r.ram_viable_mb
                for p, r in self.results.items()
            },
            "ram_baseline": {
                p: round(r.baseline_peak_mb, 1)
                for p, r in self.results.items()
            },
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "benchmark_id": self.benchmark_id,
            "config": self.config.to_dict() if self.config else None,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "results": {p: r.to_dict() for p, r in self.results.items()},
            "summary": self.get_summary(),
        }

    def to_json(self, path: Path, indent: int = 2) -> None:
        """Export results to JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=indent, default=str)

    @classmethod
    def from_json(cls, path: Path) -> "BenchmarkResults":
        """Load results from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        results = cls(
            benchmark_id=data.get("benchmark_id", ""),
            start_time=datetime.fromisoformat(data.get("start_time", "")),
        )

        if data.get("end_time"):
            results.end_time = datetime.fromisoformat(data["end_time"])

        if data.get("config"):
            cfg = data["config"]
            results.config = BenchmarkConfig(
                paradigms=cfg.get("paradigms", []),
                queries=cfg.get("queries", []),
                data_profile=cfg.get("data_profile", ""),
                ram_levels_mb=cfg.get("ram_levels_mb", []),
                n_warmup=cfg.get("n_warmup", 3),
                n_runs=cfg.get("n_runs", 10),
                n_variants=cfg.get("n_variants", 3),
                timeout_seconds=cfg.get("timeout_seconds", 300),
            )

        # Load paradigm results
        for paradigm, pdata in data.get("results", {}).items():
            pr = ParadigmResults(
                paradigm=paradigm,
                baseline_peak_mb=pdata.get("ram_baseline_mb", 0),
            )

            for ldata in pdata.get("levels", []):
                level = LevelResult(
                    limit_mb=ldata.get("limit_mb", 0),
                    status=ldata.get("status", "error"),
                    actual_peak_mb=ldata.get("actual_peak_mb", 0),
                    duration_seconds=ldata.get("duration_seconds", 0),
                    error_message=ldata.get("error_message"),
                )

                for qid, qdata in ldata.get("queries", {}).items():
                    level.queries[qid] = QueryResult(
                        query_id=qid,
                        p50_ms=qdata.get("p50_ms", 0),
                        p95_ms=qdata.get("p95_ms", 0),
                        avg_ms=qdata.get("avg_ms", 0),
                        min_ms=qdata.get("min_ms", 0),
                        max_ms=qdata.get("max_ms", 0),
                        stddev_ms=qdata.get("stddev_ms", 0),
                        success_rate=qdata.get("success_rate", 0),
                        memory_peak_mb=qdata.get("memory_peak_mb", 0),
                        run_count=qdata.get("run_count", 0),
                        # Validation data
                        row_count=qdata.get("row_count", 0),
                        sample_rows=qdata.get("sample_rows"),
                        row_hash=qdata.get("row_hash"),
                        column_names=qdata.get("column_names"),
                    )

                pr.levels.append(level)

            results.results[paradigm] = pr

        return results


def compute_statistics(latencies: list[float]) -> dict[str, float]:
    """Compute statistics from a list of latencies.

    Args:
        latencies: List of latency values in ms

    Returns:
        Dict with p50, p95, avg, min, max, stddev
    """
    if not latencies:
        return {
            "p50_ms": 0.0,
            "p95_ms": 0.0,
            "avg_ms": 0.0,
            "min_ms": 0.0,
            "max_ms": 0.0,
            "stddev_ms": 0.0,
        }

    sorted_latencies = sorted(latencies)
    n = len(sorted_latencies)

    # Percentiles
    p50_idx = n // 2
    p95_idx = int(n * 0.95)

    p50 = sorted_latencies[p50_idx]
    p95 = sorted_latencies[min(p95_idx, n - 1)]

    # Basic stats
    avg = sum(latencies) / n
    min_val = min(latencies)
    max_val = max(latencies)

    # Standard deviation
    if n < 2:
        stddev = 0.0
    else:
        variance = sum((x - avg) ** 2 for x in latencies) / n
        stddev = variance ** 0.5

    return {
        "p50_ms": p50,
        "p95_ms": p95,
        "avg_ms": avg,
        "min_ms": min_val,
        "max_ms": max_val,
        "stddev_ms": stddev,
    }
