"""Results archiving for reproducibility and audit.

Sprint 3 - Benchmark BaseType V3

Provides structured archiving of benchmark results:
- Raw query results per paradigm/query
- Run metadata (config, params, git hash)
- Enables validation replay without re-executing queries

Archive structure:
    data/results/runs/{benchmark_id}/
    ├── metadata.json           # Config, params, git hash, timestamps
    ├── raw_results/
    │   ├── P1/
    │   │   ├── Q1.json         # Full query result (all rows)
    │   │   ├── Q2.json
    │   │   └── ...
    │   ├── M1/
    │   │   └── ...
    │   └── ...
    ├── benchmark_summary.json  # Performance metrics
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

    def to_dict(self) -> dict:
        return {
            "query_id": self.query_id,
            "paradigm": self.paradigm,
            "timestamp": self.timestamp.isoformat(),
            "row_count": self.row_count,
            "rows": self.rows,
            "column_names": self.column_names,
            "content_hash": self.content_hash,
            "parameters": self.parameters,
            "execution_time_ms": self.execution_time_ms,
            "ram_limit_mb": self.ram_limit_mb,
        }

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

    def compute_hash(self) -> str:
        """Compute SHA256 hash of row data for integrity verification."""
        content = json.dumps(self.rows, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


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

        # Save to file
        paradigm_dir = self._get_run_path(self._current_run) / "raw_results" / paradigm
        paradigm_dir.mkdir(parents=True, exist_ok=True)

        result_path = paradigm_dir / f"{query_id}.json"
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(archive.to_dict(), f, indent=2, default=str)

        # Track parameters in metadata
        if self._metadata and parameters:
            if query_id not in self._metadata.query_parameters:
                self._metadata.query_parameters[query_id] = {}
            self._metadata.query_parameters[query_id][paradigm] = parameters

        return archive

    def finalize_run(self, benchmark_summary: dict | None = None) -> None:
        """Finalize the current run.

        Args:
            benchmark_summary: Optional summary data to save
        """
        if not self._current_run or not self._metadata:
            return

        self._metadata.end_time = datetime.now()
        self._save_metadata()

        # Save benchmark summary if provided
        if benchmark_summary:
            summary_path = self._get_run_path(self._current_run) / "benchmark_summary.json"
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(benchmark_summary, f, indent=2, default=str)

        self._current_run = None
        self._metadata = None

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
        """Get list of queries in this run."""
        queries = set()
        raw_results = self.run_path / "raw_results"
        if raw_results.exists():
            for paradigm_dir in raw_results.iterdir():
                if paradigm_dir.is_dir():
                    for query_file in paradigm_dir.glob("Q*.json"):
                        queries.add(query_file.stem)
        return sorted(queries)

    def get_query(self, query_id: str, paradigm: str) -> QueryArchive | None:
        """Get archived query result.

        Args:
            query_id: Query identifier
            paradigm: Paradigm identifier

        Returns:
            QueryArchive or None if not found
        """
        cache_key = f"{paradigm}/{query_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result_path = self.run_path / "raw_results" / paradigm / f"{query_id}.json"
        if not result_path.exists():
            return None

        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        archive = QueryArchive.from_dict(data)
        self._cache[cache_key] = archive
        return archive

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
