"""Scenario orchestration for benchmark execution."""

import time
from pathlib import Path
from typing import Dict, Optional

from . import docker
from .protocol import Protocol, get_protocol, QUERIES, QUERY_TYPE
from .metrics import ResourceMonitor, get_peak_memory_mb
from .results import BenchmarkResult, QueryResult, LoadResult, save_results
from .engines.postgres import PostgresEngine
from .engines.memgraph import MemgraphEngine
from .engines.oxigraph import OxigraphEngine
from .engines.timescale import TimescaleEngine

# Import exporter for on-demand CSV generation
from ..dataset.exporter_v2 import (
    export_postgresql_csv,
    export_postgresql_jsonb_csv,
    export_memgraph_csv,
    export_memgraph_chunks_csv,
    export_ntriples,
    export_oxigraph_chunks_ntriples,
    export_timeseries_csv_shared,
)


# Query file paths by scenario
QUERY_DIRS = {
    "P1": Path("queries/p1_p2"),
    "P2": Path("queries/p1_p2"),
    "M1": Path("queries/m1"),
    "M2": Path("queries/m2/graph"),
    "O1": Path("queries/o1"),
    "O2": Path("queries/o2/graph"),
}

# Query file extensions
QUERY_EXT = {
    "P1": ".sql",
    "P2": ".sql",
    "M1": ".cypher",
    "M2": ".cypher",
    "O1": ".sparql",
    "O2": ".sparql",
}


def ensure_scenario_exported(parquet_dir: Path, scenario: str) -> None:
    """Export CSV/NT files for a scenario if they don't exist.

    Args:
        parquet_dir: Directory containing parquet files (nodes.parquet, etc.)
        scenario: P1, P2, M1, M2, O1, O2
    """
    scenario = scenario.upper()
    scenario_dir = parquet_dir / scenario.lower()

    # Scenarios that need timeseries.csv (use TimescaleDB)
    NEEDS_TIMESERIES_CSV = {"P1", "P2", "M2", "O2"}

    # Export shared timeseries.csv ONCE for all scenarios that need it
    if scenario in NEEDS_TIMESERIES_CSV:
        shared_ts = parquet_dir / "timeseries.csv"
        if not shared_ts.exists():
            print(f"  [EXPORT] Generating shared timeseries.csv...")
            export_timeseries_csv_shared(parquet_dir, shared_ts)

    # Check if scenario-specific files already exported
    key_files = {
        "P1": scenario_dir / "pg_nodes.csv",
        "P2": scenario_dir / "pg_jsonb_nodes.csv",
        "M1": scenario_dir / "mg_nodes.csv",
        "M2": scenario_dir / "mg_nodes.csv",
        "O1": scenario_dir / "graph.nt",
        "O2": scenario_dir / "graph.nt",
    }

    if key_files[scenario].exists():
        print(f"  [SKIP] {scenario} files already exported")
        return

    print(f"  [EXPORT] Generating {scenario} files from parquet...")

    # Export scenario-specific files (nodes, edges, chunks)
    if scenario == "P1":
        export_postgresql_csv(parquet_dir, scenario_dir, skip_timeseries=True)

    elif scenario == "P2":
        export_postgresql_jsonb_csv(parquet_dir, scenario_dir, skip_timeseries=True)

    elif scenario == "M1":
        export_memgraph_csv(parquet_dir, scenario_dir, skip_timeseries=True)
        export_memgraph_chunks_csv(parquet_dir, scenario_dir)

    elif scenario == "M2":
        export_memgraph_csv(parquet_dir, scenario_dir, skip_timeseries=True)

    elif scenario == "O1":
        export_ntriples(parquet_dir, scenario_dir)
        export_oxigraph_chunks_ntriples(parquet_dir, scenario_dir)

    elif scenario == "O2":
        export_ntriples(parquet_dir, scenario_dir)


def get_scenario_files(export_dir: Path, scenario: str) -> Dict[str, Path]:
    """Get file paths for a scenario.

    Args:
        export_dir: Base export directory
        scenario: P1, P2, M1, M2, O1, O2

    Returns:
        Dict with 'nodes', 'edges', 'timeseries' paths
    """
    scenario_dir = export_dir / scenario.lower()
    scenario = scenario.upper()

    if scenario == "P1":
        return {
            "nodes": scenario_dir / "pg_nodes.csv",
            "edges": scenario_dir / "pg_edges.csv",
            "timeseries": export_dir / "timeseries.csv",  # Shared timeseries at root
        }
    elif scenario == "P2":
        return {
            "nodes": scenario_dir / "pg_jsonb_nodes.csv",
            "edges": scenario_dir / "pg_jsonb_edges.csv",
            "timeseries": export_dir / "timeseries.csv",  # Shared timeseries at root
        }
    elif scenario == "M1":
        return {
            "nodes": scenario_dir / "mg_nodes.csv",
            "edges": scenario_dir / "mg_edges.csv",
            "chunks": scenario_dir / "mg_chunks.csv",
        }
    elif scenario == "M2":
        return {
            "nodes": scenario_dir / "mg_nodes.csv",
            "edges": scenario_dir / "mg_edges.csv",
            "timeseries": export_dir / "timeseries.csv",
        }
    elif scenario == "O1":
        return {
            "graph": scenario_dir / "graph.nt",
            "chunks": scenario_dir / "chunks.nt",
        }
    elif scenario == "O2":
        return {
            "graph": scenario_dir / "graph.nt",
            "timeseries": export_dir / "timeseries.csv",
        }
    else:
        raise ValueError(f"Unknown scenario: {scenario}")


def load_query(scenario: str, query_id: str, base_dir: Path = None) -> Optional[str]:
    """Load query text from file.

    Args:
        scenario: P1, P2, M1, M2, O1, O2
        query_id: Q1, Q2, ... Q13
        base_dir: Base directory for queries (default: repo root)

    Returns:
        Query text or None if not found
    """
    if base_dir is None:
        # runner/scenario.py -> parents: runner(0), basetype_benchmark(1), src(2), repo_root(3)
        base_dir = Path(__file__).parent.parent.parent.parent

    query_dir = base_dir / QUERY_DIRS[scenario.upper()]
    ext = QUERY_EXT[scenario.upper()]

    # Try different naming patterns
    patterns = [
        f"{query_id}_*.{ext.lstrip('.')}",
        f"{query_id.lower()}_*.{ext.lstrip('.')}",
    ]

    for pattern in patterns:
        matches = list(query_dir.glob(pattern))
        if matches:
            return matches[0].read_text(encoding="utf-8")

    return None


def run_scenario(
    scenario: str,
    export_dir: Path,
    profile: str,
    ram_gb: int,
    output_dir: Path = None,
) -> BenchmarkResult:
    """Run benchmark for a single scenario.

    Args:
        scenario: P1, P2, M1, M2, O1, O2
        export_dir: Path to exported dataset
        profile: Profile name (e.g., 'small-2d')
        ram_gb: RAM limit in GB
        output_dir: Output directory for results

    Returns:
        BenchmarkResult
    """
    if output_dir is None:
        output_dir = Path("benchmark_results")

    scenario = scenario.upper()
    protocol = get_protocol(profile)

    result = BenchmarkResult(
        scenario=scenario,
        profile=profile,
        ram_gb=ram_gb,
        status="running",
    )

    print(f"\n{'='*60}")
    print(f"SCENARIO: {scenario} | Profile: {profile} | RAM: {ram_gb}GB")
    print(f"Protocol: {protocol.n_warmup} warmup, {protocol.n_runs} runs, {protocol.n_variants} variants")
    print(f"{'='*60}")

    try:
        # Export CSV/NT if needed (on-demand from parquet)
        print("\n[0] Checking/exporting data files...")
        ensure_scenario_exported(export_dir, scenario)

        # Start containers (mount data dir for server-side COPY)
        print("\n[1] Starting containers...")
        if not docker.start(scenario, ram_gb, data_dir=export_dir):
            result.status = "failed"
            result.error = "Failed to start containers"
            return result

        # Run scenario-specific benchmark
        if scenario in ("P1", "P2"):
            result = _run_postgres(scenario, export_dir, protocol, result)
        elif scenario in ("M1", "M2"):
            result = _run_memgraph(scenario, export_dir, protocol, result)
        elif scenario in ("O1", "O2"):
            result = _run_oxigraph(scenario, export_dir, protocol, result)
        else:
            result.status = "failed"
            result.error = f"Unknown scenario: {scenario}"

    except Exception as e:
        result.status = "failed"
        result.error = str(e)
        import traceback
        traceback.print_exc()

    finally:
        # Stop containers
        print("\n[5] Stopping containers...")
        docker.stop_all()

    # Save results
    if result.status != "failed":
        result.status = "completed"

    full_path, summary_path = save_results(result, output_dir)
    print(f"\n[DONE] Results saved to:")
    print(f"  Full:    {full_path}")
    print(f"  Summary: {summary_path}")

    return result


def _run_postgres(
    scenario: str,
    export_dir: Path,
    protocol: Protocol,
    result: BenchmarkResult,
) -> BenchmarkResult:
    """Run PostgreSQL benchmark (P1 or P2)."""
    container = docker.get_container_name("timescaledb")
    files = get_scenario_files(export_dir, scenario)

    # Connect
    print("\n[2] Connecting to PostgreSQL...")
    engine = PostgresEngine(scenario)
    engine.connect()

    try:
        # Load data
        print("\n[3] Loading data...")
        monitor = ResourceMonitor(container)
        monitor.start()
        load_start = time.time()

        engine.clear()
        engine.create_schema()

        nodes = engine.load_nodes(files["nodes"])
        edges = engine.load_edges(files["edges"])

        # Load timeseries via server-side COPY (CSV already generated in ensure_scenario_exported)
        ts_csv = export_dir / "timeseries.csv"
        ts_rows = 0
        if ts_csv.exists():
            try:
                ts_rows = engine.load_timeseries_server_copy("/data/timeseries.csv")
            except Exception as e:
                print(f"  [WARN] Server-side COPY failed ({e}), falling back to client-side...")
                ts_rows = engine.load_timeseries(ts_csv)

        load_stats = monitor.stop()
        result.load = LoadResult(
            duration_s=time.time() - load_start,
            nodes=nodes,
            edges=edges,
            timeseries_rows=ts_rows,
            peak_ram_mb=get_peak_memory_mb(container),
        )
        print(f"  Load complete: {result.load.duration_s:.1f}s, peak RAM: {result.load.peak_ram_mb:.0f}MB")

        # Run queries
        print(f"\n[4] Running queries ({len(QUERIES)} queries)...")
        result = _run_queries(engine.get_executor(), scenario, protocol, result)

    finally:
        engine.close()

    return result


def _run_memgraph(
    scenario: str,
    export_dir: Path,
    protocol: Protocol,
    result: BenchmarkResult,
) -> BenchmarkResult:
    """Run Memgraph benchmark (M1 or M2)."""
    container = docker.get_container_name("memgraph")
    files = get_scenario_files(export_dir, scenario)

    # Connect
    print("\n[2] Connecting to Memgraph...")
    engine = MemgraphEngine(scenario)
    engine.connect()

    try:
        # Load data
        print("\n[3] Loading data...")
        monitor = ResourceMonitor(container)
        monitor.start()
        load_start = time.time()

        engine.clear()

        nodes = engine.load_nodes(files["nodes"])
        edges = engine.load_edges(files["edges"])

        # M1: load chunks, M2: load timeseries to TimescaleDB
        ts_rows = 0
        if scenario == "M1" and files.get("chunks"):
            ts_rows = engine.load_chunks(files["chunks"])
        elif scenario == "M2":
            ts_csv = export_dir / "timeseries.csv"
            if ts_csv.exists():
                ts_engine = TimescaleEngine()
                ts_engine.connect()
                ts_engine.create_timeseries_schema()
                try:
                    ts_rows = ts_engine.load_timeseries_server_copy("/data/timeseries.csv")
                except Exception as e:
                    print(f"  [WARN] Server-side COPY failed ({e}), falling back to client-side...")
                    ts_rows = ts_engine.load_timeseries(ts_csv)
                ts_engine.close()

        load_stats = monitor.stop()
        result.load = LoadResult(
            duration_s=time.time() - load_start,
            nodes=nodes,
            edges=edges,
            timeseries_rows=ts_rows,
            peak_ram_mb=get_peak_memory_mb(container),
        )

        # Run queries
        print(f"\n[4] Running queries ({len(QUERIES)} queries)...")
        result = _run_queries(engine.get_executor(), scenario, protocol, result)

    finally:
        engine.close()

    return result


def _run_oxigraph(
    scenario: str,
    export_dir: Path,
    protocol: Protocol,
    result: BenchmarkResult,
) -> BenchmarkResult:
    """Run Oxigraph benchmark (O1 or O2)."""
    container = docker.get_container_name("oxigraph")
    files = get_scenario_files(export_dir, scenario)

    # Connect
    print("\n[2] Connecting to Oxigraph...")
    engine = OxigraphEngine(scenario)
    engine.connect()

    try:
        # Load data
        print("\n[3] Loading data...")
        monitor = ResourceMonitor(container)
        monitor.start()
        load_start = time.time()

        engine.clear()

        triples = 0
        if files.get("graph"):
            triples = engine.load_ntriples(files["graph"])
        if scenario == "O1" and files.get("chunks"):
            triples += engine.load_ntriples(files["chunks"])

        # O2: load timeseries to TimescaleDB
        ts_rows = 0
        if scenario == "O2":
            ts_csv = export_dir / "timeseries.csv"
            if ts_csv.exists():
                ts_engine = TimescaleEngine()
                ts_engine.connect()
                ts_engine.create_timeseries_schema()
                try:
                    ts_rows = ts_engine.load_timeseries_server_copy("/data/timeseries.csv")
                except Exception as e:
                    print(f"  [WARN] Server-side COPY failed ({e}), falling back to client-side...")
                    ts_rows = ts_engine.load_timeseries(ts_csv)
                ts_engine.close()

        load_stats = monitor.stop()
        result.load = LoadResult(
            duration_s=time.time() - load_start,
            nodes=triples,  # Using nodes field for triple count
            edges=0,
            timeseries_rows=ts_rows,
            peak_ram_mb=get_peak_memory_mb(container),
        )

        # Run queries
        print(f"\n[4] Running queries ({len(QUERIES)} queries)...")
        result = _run_queries(engine.get_executor(), scenario, protocol, result)

    finally:
        engine.close()

    return result


def _run_queries(
    executor,
    scenario: str,
    protocol: Protocol,
    result: BenchmarkResult,
) -> BenchmarkResult:
    """Run all queries with warmup and measurement.

    Args:
        executor: Function that executes queries (query -> (rows, latency_ms))
        scenario: Scenario code
        protocol: Benchmark protocol
        result: Result object to update

    Returns:
        Updated result
    """
    for query_id in QUERIES:
        query_text = load_query(scenario, query_id)
        if not query_text:
            print(f"  [{query_id}] SKIP - query file not found")
            continue

        qr = QueryResult(query_id=query_id)

        # Warmup
        for _ in range(protocol.n_warmup):
            try:
                executor(query_text)
            except Exception:
                pass

        # Measurement runs
        for run in range(protocol.n_runs):
            try:
                rows, latency_ms = executor(query_text)
                qr.latencies_ms.append(latency_ms)
                qr.rows = rows
            except Exception as e:
                qr.errors.append(str(e))

        result.queries[query_id] = qr
        status = f"p95={qr.p95_ms:.1f}ms, rows={qr.rows}"
        if qr.errors:
            status += f", errors={len(qr.errors)}"
        print(f"  [{query_id}] {status}")

    return result
