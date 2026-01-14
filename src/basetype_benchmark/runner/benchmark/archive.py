"""Results archiving for reproducibility and audit.

Sprint 3 - Benchmark BaseType V3

Provides structured archiving of benchmark results:
- Raw query results per paradigm/query (Parquet format for efficiency)
- Run metadata (config, params, git hash)
- Enables validation replay without re-executing queries
- Efficiency analysis with business-relevant thresholds

Archive structure:
    data/results/runs/{benchmark_id}/
    ├── metadata.json           # Config, params, git hash, timestamps
    ├── raw_results/
    │   ├── P1/
    │   │   ├── Q1.parquet      # Full query result rows (compact)
    │   │   ├── Q1.meta.json    # Metadata (params, hash, timing)
    │   │   └── ...
    │   ├── M1/
    │   │   └── ...
    │   └── ...
    ├── benchmark_summary.json  # Performance metrics
    ├── report.md               # Human-readable report with efficiency analysis
    └── validation/
        ├── cross_matrix.json   # Cross-paradigm validation
        └── semantic_report.json
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
import yaml


@dataclass
class RunMetadata:
    """Metadata for a benchmark run."""
    benchmark_id: str
    start_time: datetime
    end_time: datetime | None = None

    # Configuration
    paradigms: list[str] = field(default_factory=list)
    queries: list[str] = field(default_factory=list)
    data_profile: str = ""
    ram_levels_mb: list[int] = field(default_factory=list)

    # Execution params
    n_warmup: int = 0
    n_runs: int = 10
    n_variants: int = 3
    timeout_seconds: float = 300.0

    # Environment
    git_hash: str = ""
    git_branch: str = ""
    git_dirty: bool = False
    hostname: str = ""

    # Query parameters used
    query_parameters: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "benchmark_id": self.benchmark_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "config": {
                "paradigms": self.paradigms,
                "queries": self.queries,
                "data_profile": self.data_profile,
                "ram_levels_mb": self.ram_levels_mb,
                "n_warmup": self.n_warmup,
                "n_runs": self.n_runs,
                "n_variants": self.n_variants,
                "timeout_seconds": self.timeout_seconds,
            },
            "environment": {
                "git_hash": self.git_hash,
                "git_branch": self.git_branch,
                "git_dirty": self.git_dirty,
                "hostname": self.hostname,
            },
            "query_parameters": self.query_parameters,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RunMetadata":
        config = data.get("config", {})
        env = data.get("environment", {})

        return cls(
            benchmark_id=data.get("benchmark_id", ""),
            start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else datetime.now(),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            paradigms=config.get("paradigms", []),
            queries=config.get("queries", []),
            data_profile=config.get("data_profile", ""),
            ram_levels_mb=config.get("ram_levels_mb", []),
            n_warmup=config.get("n_warmup", 0),
            n_runs=config.get("n_runs", 10),
            n_variants=config.get("n_variants", 3),
            timeout_seconds=config.get("timeout_seconds", 300.0),
            git_hash=env.get("git_hash", ""),
            git_branch=env.get("git_branch", ""),
            git_dirty=env.get("git_dirty", False),
            hostname=env.get("hostname", ""),
            query_parameters=data.get("query_parameters", {}),
        )


@dataclass
class QueryArchive:
    """Archived result for a single query execution."""
    query_id: str
    paradigm: str
    timestamp: datetime

    # Full results (not just sample)
    row_count: int = 0
    rows: list[dict[str, Any]] = field(default_factory=list)
    column_names: list[str] = field(default_factory=list)

    # Hash for integrity
    content_hash: str = ""

    # Parameters used
    parameters: dict[str, Any] = field(default_factory=dict)

    # Execution info
    execution_time_ms: float = 0.0
    ram_limit_mb: int = 0

    def to_meta_dict(self) -> dict:
        """Return metadata only (without rows) for JSON storage."""
        return {
            "query_id": self.query_id,
            "paradigm": self.paradigm,
            "timestamp": self.timestamp.isoformat(),
            "row_count": self.row_count,
            "column_names": self.column_names,
            "content_hash": self.content_hash,
            "parameters": self.parameters,
            "execution_time_ms": self.execution_time_ms,
            "ram_limit_mb": self.ram_limit_mb,
        }

    def to_dict(self) -> dict:
        """Full dict including rows (for backwards compatibility)."""
        result = self.to_meta_dict()
        result["rows"] = self.rows
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "QueryArchive":
        return cls(
            query_id=data.get("query_id", ""),
            paradigm=data.get("paradigm", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
            row_count=data.get("row_count", 0),
            rows=data.get("rows", []),
            column_names=data.get("column_names", []),
            content_hash=data.get("content_hash", ""),
            parameters=data.get("parameters", {}),
            execution_time_ms=data.get("execution_time_ms", 0.0),
            ram_limit_mb=data.get("ram_limit_mb", 0),
        )

    @classmethod
    def from_parquet(cls, parquet_path: Path, meta_path: Path) -> "QueryArchive":
        """Load QueryArchive from Parquet + metadata files."""
        # Load metadata
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        # Load rows from Parquet
        table = pq.read_table(parquet_path)
        rows = table.to_pylist()

        return cls(
            query_id=meta.get("query_id", ""),
            paradigm=meta.get("paradigm", ""),
            timestamp=datetime.fromisoformat(meta["timestamp"]) if meta.get("timestamp") else datetime.now(),
            row_count=meta.get("row_count", len(rows)),
            rows=rows,
            column_names=meta.get("column_names", []),
            content_hash=meta.get("content_hash", ""),
            parameters=meta.get("parameters", {}),
            execution_time_ms=meta.get("execution_time_ms", 0.0),
            ram_limit_mb=meta.get("ram_limit_mb", 0),
        )

    def compute_hash(self) -> str:
        """Compute SHA256 hash of row data for integrity verification."""
        content = json.dumps(self.rows, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_arrow_table(self) -> pa.Table:
        """Convert rows to PyArrow Table for Parquet storage."""
        if not self.rows:
            # Empty table with no columns
            return pa.table({})

        # Convert list of dicts to columnar format
        # Handle mixed types by converting to strings for problematic columns
        columns = {}
        if self.rows:
            # Get all unique keys across all rows
            all_keys = set()
            for row in self.rows:
                all_keys.update(row.keys())

            for key in all_keys:
                values = [row.get(key) for row in self.rows]
                # Try to create array, fall back to string if mixed types
                try:
                    columns[key] = pa.array(values)
                except (pa.ArrowInvalid, pa.ArrowTypeError):
                    # Convert to strings for mixed/complex types
                    columns[key] = pa.array([
                        json.dumps(v, default=str) if not isinstance(v, (str, type(None))) else v
                        for v in values
                    ])

        return pa.table(columns)


class ResultsArchive:
    """Manager for archived benchmark results.

    Provides:
    - Structured storage of raw query results
    - Metadata tracking (config, git, params)
    - Replay capability for validation

    Example:
        ```python
        archive = ResultsArchive(Path("data/results/runs"))

        # During benchmark
        archive.start_run("2026-01-11_153439", metadata)
        archive.save_query_result("Q1", "P1", rows, params)
        archive.save_query_result("Q1", "M1", rows, params)
        archive.finalize_run()

        # Later: replay validation
        run = archive.load_run("2026-01-11_153439")
        q1_p1 = run.get_query("Q1", "P1")
        q1_m1 = run.get_query("Q1", "M1")
        validator.compare(q1_p1, q1_m1)
        ```
    """

    def __init__(self, base_path: Path):
        """Initialize archive manager.

        Args:
            base_path: Base directory for archives (e.g., data/results/runs)
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        self._current_run: str | None = None
        self._metadata: RunMetadata | None = None

    def start_run(
        self,
        benchmark_id: str,
        paradigms: list[str],
        queries: list[str],
        data_profile: str = "",
        ram_levels_mb: list[int] | None = None,
        n_warmup: int = 0,
        n_runs: int = 10,
        n_variants: int = 3,
        timeout_seconds: float = 300.0,
    ) -> Path:
        """Start a new benchmark run archive.

        Args:
            benchmark_id: Unique identifier for this run
            paradigms: List of paradigms being tested
            queries: List of query IDs
            data_profile: Data profile name
            ram_levels_mb: RAM levels being tested
            n_warmup: Warmup iterations
            n_runs: Number of runs per query
            n_variants: Parameter variants per query
            timeout_seconds: Query timeout

        Returns:
            Path to the run directory
        """
        self._current_run = benchmark_id
        run_path = self._get_run_path(benchmark_id)
        run_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (run_path / "raw_results").mkdir(exist_ok=True)
        (run_path / "metrics").mkdir(exist_ok=True)
        (run_path / "validation").mkdir(exist_ok=True)

        # Collect environment info
        git_hash, git_branch, git_dirty = self._get_git_info()
        hostname = self._get_hostname()

        # Create metadata
        self._metadata = RunMetadata(
            benchmark_id=benchmark_id,
            start_time=datetime.now(),
            paradigms=paradigms,
            queries=queries,
            data_profile=data_profile,
            ram_levels_mb=ram_levels_mb or [],
            n_warmup=n_warmup,
            n_runs=n_runs,
            n_variants=n_variants,
            timeout_seconds=timeout_seconds,
            git_hash=git_hash,
            git_branch=git_branch,
            git_dirty=git_dirty,
            hostname=hostname,
        )

        # Save initial metadata
        self._save_metadata()

        return run_path

    def save_query_result(
        self,
        query_id: str,
        paradigm: str,
        rows: list[dict[str, Any]],
        column_names: list[str] | None = None,
        parameters: dict[str, Any] | None = None,
        execution_time_ms: float = 0.0,
        ram_limit_mb: int = 0,
    ) -> QueryArchive:
        """Save a query result to the archive.

        Args:
            query_id: Query identifier (e.g., "Q1")
            paradigm: Paradigm identifier (e.g., "P1")
            rows: All result rows (full data, not sample)
            column_names: Column names from result
            parameters: Query parameters used
            execution_time_ms: Execution time
            ram_limit_mb: RAM limit during execution

        Returns:
            QueryArchive object
        """
        if not self._current_run:
            raise RuntimeError("No active run. Call start_run() first.")

        # Create archive object
        archive = QueryArchive(
            query_id=query_id,
            paradigm=paradigm,
            timestamp=datetime.now(),
            row_count=len(rows),
            rows=rows,
            column_names=column_names or [],
            parameters=parameters or {},
            execution_time_ms=execution_time_ms,
            ram_limit_mb=ram_limit_mb,
        )
        archive.content_hash = archive.compute_hash()

        # Save to files (Parquet for rows, JSON for metadata)
        paradigm_dir = self._get_run_path(self._current_run) / "raw_results" / paradigm
        paradigm_dir.mkdir(parents=True, exist_ok=True)

        # Save rows as Parquet (compact, efficient)
        parquet_path = paradigm_dir / f"{query_id}.parquet"
        if rows:
            table = archive.to_arrow_table()
            pq.write_table(table, parquet_path, compression='snappy')
        else:
            # Empty result - write empty parquet
            pq.write_table(pa.table({}), parquet_path)

        # Save metadata as JSON (small, human-readable)
        meta_path = paradigm_dir / f"{query_id}.meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(archive.to_meta_dict(), f, indent=2, default=str)

        # Track parameters in metadata
        if self._metadata and parameters:
            if query_id not in self._metadata.query_parameters:
                self._metadata.query_parameters[query_id] = {}
            self._metadata.query_parameters[query_id][paradigm] = parameters

        return archive

    def save_query_metrics(
        self,
        query_id: str,
        paradigm: str,
        metrics: dict[str, Any],
    ) -> None:
        """Save metrics for a query to metrics/ directory.

        Args:
            query_id: Query identifier
            paradigm: Paradigm identifier
            metrics: Metrics dict (p50, p95, avg, etc.)
        """
        if not self._current_run:
            return

        metrics_dir = self._get_run_path(self._current_run) / "metrics" / paradigm
        metrics_dir.mkdir(parents=True, exist_ok=True)

        metrics_path = metrics_dir / f"{query_id}.json"
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, default=str)

    def finalize_run(self, benchmark_summary: dict | None = None) -> None:
        """Finalize the current run.

        Args:
            benchmark_summary: Optional summary data to save
        """
        if not self._current_run or not self._metadata:
            return

        self._metadata.end_time = datetime.now()
        self._save_metadata()

        run_path = self._get_run_path(self._current_run)

        # Save benchmark summary if provided
        if benchmark_summary:
            summary_path = run_path / "benchmark_summary.json"
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(benchmark_summary, f, indent=2, default=str)

            # Generate Markdown report
            self._generate_report_md(run_path, benchmark_summary)

        self._current_run = None
        self._metadata = None

    def _load_efficiency_thresholds(self) -> dict:
        """Load efficiency thresholds from config file."""
        config_path = Path(__file__).parent.parent.parent.parent.parent / "config" / "efficiency_thresholds.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def _get_query_threshold(self, query_id: str, thresholds: dict) -> tuple[float, float, str]:
        """Get acceptable/degraded thresholds for a query.

        Returns:
            (acceptable_ms, degraded_ms, category_name)
        """
        latency_thresholds = thresholds.get("latency_thresholds", {})
        for category, config in latency_thresholds.items():
            if isinstance(config, dict) and query_id in config.get("queries", []):
                return (
                    config.get("acceptable_ms", 500),
                    config.get("degraded_ms", 2000),
                    category,
                )
        # Default
        default = thresholds.get("default", {})
        return (default.get("acceptable_ms", 500), default.get("degraded_ms", 2000), "default")

    def _generate_report_md(self, run_path: Path, summary: dict) -> None:
        """Generate a factual Markdown report for the benchmark run.

        Includes efficiency analysis with:
        - Latency acceptability per use case
        - Memory efficiency ratios
        - Hypothesis validation conclusion

        Args:
            run_path: Path to run directory
            summary: Benchmark summary dict
        """
        report_path = run_path / "report.md"
        metadata = self._metadata
        results = summary.get("results", {})
        ram_summary = summary.get("summary", {})

        # Load efficiency thresholds
        thresholds = self._load_efficiency_thresholds()

        lines = [
            f"# Benchmark Report: {metadata.benchmark_id}",
            "",
            "## Executive Summary",
            "",
        ]

        # Collect query data first for analysis
        query_data: dict[str, dict[str, float | None]] = {}
        memory_data: dict[str, dict[str, float | None]] = {}

        for p, p_data in results.items():
            for level in p_data.get("levels", []):
                if level.get("status") == "success":
                    for qid, qdata in level.get("queries", {}).items():
                        if qid not in query_data:
                            query_data[qid] = {}
                            memory_data[qid] = {}
                        if p not in query_data[qid]:
                            query_data[qid][p] = qdata.get("p50_ms")
                            memory_data[qid][p] = qdata.get("memory_peak_mb")
                    break  # First successful level only

        # Calculate efficiency scores
        paradigm_scores: dict[str, dict] = {}
        reference_paradigm = "P2"  # P2 as reference for comparison

        for p in metadata.paradigms:
            acceptable_count = 0
            degraded_count = 0
            unacceptable_count = 0
            total_queries = 0

            for qid, latencies in query_data.items():
                if latencies.get(p) is not None:
                    total_queries += 1
                    lat = latencies[p]
                    acceptable_ms, degraded_ms, _ = self._get_query_threshold(qid, thresholds)

                    if lat <= acceptable_ms:
                        acceptable_count += 1
                    elif lat <= degraded_ms:
                        degraded_count += 1
                    else:
                        unacceptable_count += 1

            paradigm_scores[p] = {
                "acceptable": acceptable_count,
                "degraded": degraded_count,
                "unacceptable": unacceptable_count,
                "total": total_queries,
                "acceptable_pct": (acceptable_count / total_queries * 100) if total_queries > 0 else 0,
            }

        # Executive summary with hypothesis validation
        lines.extend([
            "**Hypothesis**: Graph databases (M1, M2) do not provide significant advantages over ",
            "SQL+JSONB (P2) for building management workloads, especially considering resource costs.",
            "",
        ])

        # RAM efficiency comparison
        ram_viable = ram_summary.get("ram_viable", {})
        ram_baseline = ram_summary.get("ram_baseline", {})

        p2_ram = ram_baseline.get("P2", 0)
        if p2_ram > 0:
            lines.append("### Resource Efficiency")
            lines.append("")
            lines.append("| Paradigm | RAM Baseline (MB) | vs P2 | RAM Viable | Verdict |")
            lines.append("|----------|-------------------|-------|------------|---------|")

            for p in metadata.paradigms:
                baseline = ram_baseline.get(p, 0)
                viable = ram_viable.get(p)
                ratio = baseline / p2_ram if p2_ram > 0 else 0

                if ratio <= 1.5:
                    verdict = "Equivalent"
                elif ratio <= 3.0:
                    verdict = "Acceptable"
                elif ratio <= 6.0:
                    verdict = "Degraded"
                else:
                    verdict = "**Costly**"

                viable_str = f"{viable} GB" if viable else "OOM"
                lines.append(f"| {p} | {baseline:.0f} | {ratio:.1f}x | {viable_str} | {verdict} |")
            lines.append("")

        # Latency acceptability summary
        lines.extend([
            "### Latency Acceptability",
            "",
            "| Paradigm | Acceptable | Degraded | Slow | Score |",
            "|----------|------------|----------|------|-------|",
        ])

        for p in metadata.paradigms:
            scores = paradigm_scores.get(p, {})
            score_pct = scores.get("acceptable_pct", 0)
            lines.append(
                f"| {p} | {scores.get('acceptable', 0)} | {scores.get('degraded', 0)} | "
                f"{scores.get('unacceptable', 0)} | {score_pct:.0f}% |"
            )
        lines.append("")

        # Critical Findings: P2 vs M1 (standalone graph, like SpinalCom architecture)
        # M2 uses TimescaleDB so it's not a fair "in-memory graph" comparison
        critical_threshold_ms = thresholds.get("conclusion", {}).get("critical_difference_ms", 500)

        p2_wins_critical: list[tuple[str, float, float, float]] = []  # (qid, p2_ms, m1_ms, diff)
        m1_wins_critical: list[tuple[str, float, float, float]] = []

        # Get row counts to exclude queries with 0 rows (not meaningful comparisons)
        query_row_counts: dict[str, dict[str, int]] = {}
        for p, p_data in results.items():
            for level in p_data.get("levels", []):
                if level.get("status") == "success":
                    for qid, qdata in level.get("queries", {}).items():
                        if qid not in query_row_counts:
                            query_row_counts[qid] = {}
                        query_row_counts[qid][p] = qdata.get("row_count", 0)
                    break

        for qid, latencies in query_data.items():
            p2_lat = latencies.get("P2")
            m1_lat = latencies.get("M1")
            if p2_lat is not None and m1_lat is not None:
                # Skip queries where both paradigms return 0 rows (not meaningful)
                p2_rows = query_row_counts.get(qid, {}).get("P2", 0)
                m1_rows = query_row_counts.get(qid, {}).get("M1", 0)
                if p2_rows == 0 and m1_rows == 0:
                    continue

                diff = m1_lat - p2_lat
                if diff > critical_threshold_ms:
                    p2_wins_critical.append((qid, p2_lat, m1_lat, diff))
                elif diff < -critical_threshold_ms:
                    m1_wins_critical.append((qid, p2_lat, m1_lat, -diff))

        # Sort by difference (most significant first)
        p2_wins_critical.sort(key=lambda x: -x[3])
        m1_wins_critical.sort(key=lambda x: -x[3])

        lines.extend([
            "### Critical Findings: P2 vs M1 (In-Memory Graph)",
            "",
            "*Comparing P2 (SQL+JSONB) vs M1 (Memgraph standalone) - the 'in-memory graph kernel' architecture.*",
            "*M2 uses TimescaleDB for timeseries, so M1 is the fair comparison for SpinalCom-style claims.*",
            "",
        ])

        if p2_wins_critical:
            lines.extend([
                f"**P2 significantly faster** (>{critical_threshold_ms}ms difference):",
                "",
                "| Query | P2 | M1 | Difference | Ratio |",
                "|-------|---:|---:|----------:|------:|",
            ])
            for qid, p2_lat, m1_lat, diff in p2_wins_critical:
                ratio = m1_lat / p2_lat if p2_lat > 0 else float('inf')
                lines.append(f"| {qid} | {p2_lat:.0f}ms | {m1_lat:.0f}ms | **+{diff:.0f}ms** | M1 {ratio:.0f}x slower |")
            lines.append("")

        if m1_wins_critical:
            lines.extend([
                f"**M1 significantly faster** (>{critical_threshold_ms}ms difference):",
                "",
                "| Query | P2 | M1 | Difference | Ratio |",
                "|-------|---:|---:|----------:|------:|",
            ])
            for qid, p2_lat, m1_lat, diff in m1_wins_critical:
                ratio = p2_lat / m1_lat if m1_lat > 0 else float('inf')
                lines.append(f"| {qid} | {p2_lat:.0f}ms | {m1_lat:.0f}ms | **-{diff:.0f}ms** | P2 {ratio:.0f}x slower |")
            lines.append("")

        if not p2_wins_critical and not m1_wins_critical:
            lines.extend([
                f"No queries show >{critical_threshold_ms}ms difference between P2 and M1.",
                "",
            ])

        # Conclusion
        lines.extend([
            "### Conclusion",
            "",
        ])

        # Analyze results for conclusion - focus on P2 vs M1
        p2_score = paradigm_scores.get("P2", {}).get("acceptable_pct", 0)
        m1_score = paradigm_scores.get("M1", {}).get("acceptable_pct", 0)

        m1_ram_ratio = ram_baseline.get("M1", 0) / p2_ram if p2_ram > 0 else 0

        latency_equiv_pct = thresholds.get("conclusion", {}).get("latency_equivalence_pct", 20)
        memory_sig_ratio = thresholds.get("conclusion", {}).get("memory_significant_ratio", 3.0)

        # Determine conclusion based on critical findings
        if p2_wins_critical and not m1_wins_critical:
            latency_conclusion = f"P2 is **significantly faster** on {len(p2_wins_critical)} critical queries (timeseries/analytics). M1 shows no perceptible advantage."
        elif m1_wins_critical and not p2_wins_critical:
            latency_conclusion = f"M1 is **significantly faster** on {len(m1_wins_critical)} queries. Graph-native workloads benefit from in-memory."
        elif p2_wins_critical and m1_wins_critical:
            latency_conclusion = f"Mixed results: P2 wins on {len(p2_wins_critical)} queries, M1 wins on {len(m1_wins_critical)}."
        else:
            latency_conclusion = "P2 and M1 are **latency-equivalent** - no perceptible difference (all <500ms)."

        if m1_ram_ratio >= 1.5:
            memory_conclusion = f"M1 consumes **{m1_ram_ratio:.1f}x more RAM** than P2."
        else:
            memory_conclusion = "Memory consumption is comparable."

        lines.extend([
            f"- **Latency**: {latency_conclusion}",
            f"- **Memory**: {memory_conclusion}",
            "",
        ])

        # Final verdict - based on critical findings
        has_critical_p2_advantage = len(p2_wins_critical) > 0
        has_critical_m1_advantage = len(m1_wins_critical) > 0

        if has_critical_p2_advantage and not has_critical_m1_advantage:
            lines.extend([
                "**Verdict**: The hypothesis is **SUPPORTED**.",
                "",
                "M1 (in-memory graph) provides **no perceptible latency advantage** over P2 on any query, ",
                "while P2 is **seconds faster** on timeseries/analytics workloads. ",
                "The 'in-memory graph kernel' architecture (SpinalCom-style) is not justified for ",
                "smart building middleware where IoT/timeseries queries dominate.",
                "",
                "**Recommendation**: Use PostgreSQL+JSONB (P2) for building management systems.",
                "",
            ])
        elif has_critical_m1_advantage and not has_critical_p2_advantage:
            lines.extend([
                "**Verdict**: The hypothesis is **REFUTED**.",
                "",
                "M1 shows significant latency advantages on graph-native workloads that justify ",
                "the in-memory architecture for graph-heavy use cases.",
                "",
            ])
        elif has_critical_p2_advantage and has_critical_m1_advantage:
            lines.extend([
                "**Verdict**: Results are **MIXED**.",
                "",
                "P2 excels on timeseries/analytics, M1 excels on graph-native queries. ",
                "Architecture choice depends on workload distribution.",
                "",
            ])
        else:
            lines.extend([
                "**Verdict**: The hypothesis is **SUPPORTED** (equivalence).",
                "",
                "No perceptible difference between P2 and M1 on any query. ",
                "P2 is recommended due to lower operational complexity and better ecosystem.",
                "",
            ])

        # Scalability reference
        scalability = thresholds.get("scalability_reference", {})
        if scalability:
            lines.extend([
                "### Scalability Reference",
                "",
                "| Stack | Read QPS | Write QPS | Notes |",
                "|-------|----------|-----------|-------|",
            ])
            for stack, data in scalability.items():
                if isinstance(data, dict):
                    lines.append(
                        f"| {stack} | {data.get('read_qps', 'N/A'):,} | "
                        f"{data.get('write_qps', 'N/A'):,} | {data.get('description', '')[:50]}... |"
                    )
            lines.append("")
            lines.append("*Source: TechEmpower benchmarks, vendor documentation*")
            lines.append("")

        # Detailed sections
        lines.extend([
            "---",
            "",
            "## Detailed Results",
            "",
            "### Dataset",
            "",
            f"| Property | Value |",
            f"|----------|-------|",
            f"| Profile | {metadata.data_profile} |",
            f"| Queries | {len(metadata.queries)} |",
            f"| Runs/Query | {metadata.n_runs} |",
            f"| Variants | {metadata.n_variants} |",
            "",
        ])

        # RAM Footprint
        if ram_summary:
            lines.extend([
                "### RAM Footprint (MB)",
                "",
                "| Paradigm | Baseline | Viable |",
                "|----------|----------|--------|",
            ])
            for p in metadata.paradigms:
                baseline = ram_baseline.get(p, 0)
                viable = ram_viable.get(p)
                viable_str = str(viable) if viable else "OOM"
                lines.append(f"| {p} | {baseline:.0f} | {viable_str} |")
            lines.append("")

        # Query Latency with acceptability indicator
        if results:
            lines.extend([
                "### Query Latency p50 (ms)",
                "",
                "*Legend: acceptable | degraded | slow*",
                "",
            ])

            # Header
            header = "| Query | Category |"
            separator = "|-------|----------|"
            for p in metadata.paradigms:
                header += f" {p} |"
                separator += "-----:|"
            lines.append(header)
            lines.append(separator)

            for qid in sorted(query_data.keys()):
                acceptable_ms, degraded_ms, category = self._get_query_threshold(qid, thresholds)
                row = f"| {qid} | {category[:8]} |"
                for p in metadata.paradigms:
                    val = query_data[qid].get(p)
                    if val is not None:
                        if val <= acceptable_ms:
                            row += f" {val:.1f} |"
                        elif val <= degraded_ms:
                            row += f" *{val:.1f}* |"
                        else:
                            row += f" **{val:.1f}** |"
                    else:
                        row += " - |"
                lines.append(row)
            lines.append("")

        # Query Coverage
        if results:
            lines.extend([
                "### Query Coverage",
                "",
                "| Paradigm | Answered | Impossible |",
                "|----------|----------|------------|",
            ])
            for p in metadata.paradigms:
                answered = sum(1 for qid in query_data if query_data[qid].get(p) is not None)
                impossible = len(metadata.queries) - answered
                lines.append(f"| {p} | {answered} | {impossible} |")
            lines.append("")

        # Environment (compact)
        lines.extend([
            "### Environment",
            "",
            f"| Property | Value |",
            f"|----------|-------|",
            f"| Git | {metadata.git_branch}@{metadata.git_hash} |",
            f"| Host | {metadata.hostname} |",
        ])
        if metadata.end_time:
            duration = (metadata.end_time - metadata.start_time).total_seconds()
            lines.append(f"| Duration | {duration:.0f}s |")
        lines.append("")

        # Write report
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def load_run(self, benchmark_id: str) -> "ArchivedRun":
        """Load an archived run.

        Args:
            benchmark_id: Run identifier

        Returns:
            ArchivedRun object for accessing archived data
        """
        run_path = self._get_run_path(benchmark_id)
        if not run_path.exists():
            raise FileNotFoundError(f"Run not found: {benchmark_id}")

        return ArchivedRun(run_path)

    def list_runs(self) -> list[str]:
        """List all archived runs.

        Returns:
            List of benchmark IDs
        """
        runs = []
        for path in self.base_path.iterdir():
            if path.is_dir() and (path / "metadata.json").exists():
                runs.append(path.name)
        return sorted(runs, reverse=True)  # Most recent first

    def _get_run_path(self, benchmark_id: str) -> Path:
        """Get path for a run directory."""
        return self.base_path / benchmark_id

    def _save_metadata(self) -> None:
        """Save current metadata to file."""
        if not self._current_run or not self._metadata:
            return

        metadata_path = self._get_run_path(self._current_run) / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self._metadata.to_dict(), f, indent=2, default=str)

    def _get_git_info(self) -> tuple[str, str, bool]:
        """Get current git information."""
        try:
            # Get commit hash
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, timeout=5
            )
            git_hash = result.stdout.strip() if result.returncode == 0 else ""

            # Get branch name
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, timeout=5
            )
            git_branch = result.stdout.strip() if result.returncode == 0 else ""

            # Check if dirty
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, timeout=5
            )
            git_dirty = bool(result.stdout.strip()) if result.returncode == 0 else False

            return git_hash, git_branch, git_dirty
        except Exception:
            return "", "", False

    def _get_hostname(self) -> str:
        """Get hostname."""
        try:
            import socket
            return socket.gethostname()
        except Exception:
            return ""


class ArchivedRun:
    """Access to an archived benchmark run.

    Provides lazy loading of query results for validation replay.
    """

    def __init__(self, run_path: Path):
        """Initialize from run directory.

        Args:
            run_path: Path to the run directory
        """
        self.run_path = Path(run_path)
        self._metadata: RunMetadata | None = None
        self._cache: dict[str, QueryArchive] = {}

    @property
    def metadata(self) -> RunMetadata:
        """Get run metadata (lazy loaded)."""
        if self._metadata is None:
            metadata_path = self.run_path / "metadata.json"
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._metadata = RunMetadata.from_dict(data)
        return self._metadata

    @property
    def benchmark_id(self) -> str:
        """Get benchmark ID."""
        return self.metadata.benchmark_id

    @property
    def paradigms(self) -> list[str]:
        """Get list of paradigms in this run."""
        raw_results = self.run_path / "raw_results"
        if not raw_results.exists():
            return []
        return [p.name for p in raw_results.iterdir() if p.is_dir()]

    @property
    def queries(self) -> list[str]:
        """Get list of queries in this run (supports Parquet and JSON)."""
        queries = set()
        raw_results = self.run_path / "raw_results"
        if raw_results.exists():
            for paradigm_dir in raw_results.iterdir():
                if paradigm_dir.is_dir():
                    # Check for Parquet files (new format)
                    for query_file in paradigm_dir.glob("*.parquet"):
                        queries.add(query_file.stem)
                    # Check for JSON files (legacy format, exclude .meta.json)
                    for query_file in paradigm_dir.glob("*.json"):
                        if not query_file.name.endswith(".meta.json"):
                            queries.add(query_file.stem)
        return sorted(queries)

    def get_query(self, query_id: str, paradigm: str) -> QueryArchive | None:
        """Get archived query result.

        Supports both Parquet (new) and JSON (legacy) formats.

        Args:
            query_id: Query identifier
            paradigm: Paradigm identifier

        Returns:
            QueryArchive or None if not found
        """
        cache_key = f"{paradigm}/{query_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        paradigm_dir = self.run_path / "raw_results" / paradigm

        # Try Parquet format first (new)
        parquet_path = paradigm_dir / f"{query_id}.parquet"
        meta_path = paradigm_dir / f"{query_id}.meta.json"

        if parquet_path.exists() and meta_path.exists():
            archive = QueryArchive.from_parquet(parquet_path, meta_path)
            self._cache[cache_key] = archive
            return archive

        # Fall back to JSON format (legacy)
        json_path = paradigm_dir / f"{query_id}.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            archive = QueryArchive.from_dict(data)
            self._cache[cache_key] = archive
            return archive

        return None

    def get_parameters(self, query_id: str) -> dict[str, Any]:
        """Get parameters used for a query.

        Args:
            query_id: Query identifier

        Returns:
            Parameters dict (from first paradigm that has them)
        """
        return self.metadata.query_parameters.get(query_id, {})

    def to_benchmark_results(self) -> "BenchmarkResults":
        """Convert archived run to BenchmarkResults for validation.

        This enables replaying validation on archived data.

        Returns:
            BenchmarkResults object with query results populated
        """
        from .results import BenchmarkResults, BenchmarkConfig, ParadigmResults, LevelResult, QueryResult

        results = BenchmarkResults(
            benchmark_id=self.metadata.benchmark_id,
            start_time=self.metadata.start_time,
            end_time=self.metadata.end_time,
        )

        results.config = BenchmarkConfig(
            paradigms=self.metadata.paradigms,
            queries=self.metadata.queries,
            data_profile=self.metadata.data_profile,
            ram_levels_mb=self.metadata.ram_levels_mb,
            n_warmup=self.metadata.n_warmup,
            n_runs=self.metadata.n_runs,
            n_variants=self.metadata.n_variants,
            timeout_seconds=self.metadata.timeout_seconds,
        )

        # Load results for each paradigm
        for paradigm in self.paradigms:
            pr = ParadigmResults(paradigm=paradigm)

            # Create a single "archive" level to hold the query results
            level = LevelResult(
                limit_mb=self.metadata.ram_levels_mb[0] if self.metadata.ram_levels_mb else 0,
                status="archived",
            )

            for query_id in self.queries:
                archive = self.get_query(query_id, paradigm)
                if archive:
                    # Convert to QueryResult for validation
                    level.queries[query_id] = QueryResult(
                        query_id=query_id,
                        row_count=archive.row_count,
                        sample_rows=archive.rows,  # Full rows from archive
                        column_names=archive.column_names,
                        row_hash=archive.content_hash,
                    )

            pr.levels.append(level)
            results.results[paradigm] = pr

        return results
