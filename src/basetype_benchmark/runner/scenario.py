"""Scenario orchestration for benchmark execution."""

import os
import time
from pathlib import Path
from typing import Dict, Optional

from . import docker
from .protocol import Protocol, get_protocol, QUERIES, QUERY_TYPE
from .metrics import ResourceMonitor, get_peak_memory_mb
from .results import BenchmarkResult, QueryResult, LoadResult, save_results
from .params import (
    extract_dataset_info,
    extract_timeseries_range,
    extract_dataset_info_from_parquet,
    extract_timeseries_range_from_parquet,
    get_query_variants,
    substitute_params,
    get_nodes_csv_path,
)
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


def _queries_need_timeseries(query_ids: list[str]) -> bool:
    """Return True if selected queries require timeseries/chunk data."""
    return any(QUERY_TYPE.get(q) != "graph_only" for q in query_ids)


def ensure_scenario_exported(
    export_dir: Path,
    scenario: str,
    query_ids: Optional[list[str]] = None,
) -> None:
    """Export CSV/NT files for a scenario if they don't exist.

    Args:
        export_dir: Export directory (may contain parquet/ subdirectory)
        scenario: P1, P2, M1, M2, O1, O2
    """
    scenario = scenario.upper()
    
    # Resolve parquet directory: check for parquet/ subdirectory structure
    # Structure can be either:
    #   export_dir/nodes.parquet (flat)
    #   export_dir/parquet/nodes.parquet (nested)
    if (export_dir / "parquet" / "nodes.parquet").exists():
        parquet_dir = export_dir / "parquet"
    elif (export_dir / "nodes.parquet").exists():
        parquet_dir = export_dir
    else:
        raise FileNotFoundError(
            f"No parquet files found in {export_dir} or {export_dir / 'parquet'}. "
            f"Generate dataset first with: python -m basetype_benchmark.dataset generate small-2d"
        )
    
    scenario_dir = export_dir / scenario.lower()

    selected = query_ids or QUERIES

    # Scenarios that need timeseries.csv (use TimescaleDB)
    NEEDS_TIMESERIES_CSV = {"P1", "P2", "M2", "O2"}

    # Export shared timeseries.csv ONCE for all scenarios that need it.
    # If we only run graph-only queries, skip generating timeseries.csv.
    # timeseries.csv goes at export_dir root (not in parquet/ subdirectory)
    if scenario in NEEDS_TIMESERIES_CSV and _queries_need_timeseries(selected):
        shared_ts = export_dir / "timeseries.csv"
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
        if _queries_need_timeseries(selected):
            export_memgraph_chunks_csv(parquet_dir, scenario_dir)

    elif scenario == "M2":
        export_memgraph_csv(parquet_dir, scenario_dir, skip_timeseries=True)

    elif scenario == "O1":
        export_ntriples(parquet_dir, scenario_dir)
        if _queries_need_timeseries(selected):
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
    query_ids: Optional[list[str]] = None,
    protocol_override: Optional[Protocol] = None,
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
    protocol = protocol_override or get_protocol(profile)

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
        selected = query_ids or QUERIES

        # Export CSV/NT if needed (on-demand from parquet)
        print("\n[0] Checking/exporting data files...")
        ensure_scenario_exported(export_dir, scenario, query_ids=selected)

        # Start containers (mount data dir for server-side COPY)
        print("\n[1] Starting containers...")
        if not docker.start(scenario, ram_gb, data_dir=export_dir):
            result.status = "failed"
            result.error = "Failed to start containers"
            return result

        # Run scenario-specific benchmark
        if scenario in ("P1", "P2"):
            result = _run_postgres(scenario, export_dir, protocol, result, query_ids=query_ids)
        elif scenario in ("M1", "M2"):
            result = _run_memgraph(scenario, export_dir, protocol, result, query_ids=query_ids)
        elif scenario in ("O1", "O2"):
            result = _run_oxigraph(scenario, export_dir, protocol, result, query_ids=query_ids)
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
    query_ids: Optional[list[str]] = None,
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

        selected = query_ids or QUERIES

        # Load timeseries (ingestion is not a benchmark target, but must be fast and fair)
        ts_csv = export_dir / "timeseries.csv"
        parquet_dir = export_dir / "parquet"
        ts_parquet = parquet_dir / "timeseries.parquet"
        ts_rows = 0

        if _queries_need_timeseries(selected) and ts_csv.exists():
            # Prefer fastest in-container bulk path
            try:
                ts_rows = engine.load_timeseries_parallel_copy("/data/timeseries.csv")
            except Exception as e:
                print(f"  [WARN] parallel-copy failed ({e}); trying server-side COPY...")
                try:
                    ts_rows = engine.load_timeseries_server_copy("/data/timeseries.csv")
                except Exception as e2:
                    print(f"  [WARN] Server-side COPY failed ({e2}), falling back to client-side...")
                    ts_rows = engine.load_timeseries(ts_csv)
        elif _queries_need_timeseries(selected) and ts_parquet.exists() and hasattr(engine, "load_timeseries_from_parquet"):
            print("  [LOAD] timeseries.csv missing; falling back to Parquet enrichment path...")
            ts_rows = engine.load_timeseries_from_parquet(ts_parquet)

        load_stats = monitor.stop()
        result.load = LoadResult(
            duration_s=time.time() - load_start,
            nodes=nodes,
            edges=edges,
            timeseries_rows=ts_rows,
            peak_ram_mb=get_peak_memory_mb(container),
        )
        print(f"  Load complete: {result.load.duration_s:.1f}s, peak RAM: {result.load.peak_ram_mb:.0f}MB")

        # Run queries (this is what we benchmark)
        print(f"\n[4] Running queries ({len(selected)} queries)...")

        # Monitor query-phase resource usage (queries-only window)
        monitors: Dict[str, ResourceMonitor] = {}
        for svc in docker.SCENARIO_CONTAINERS.get(scenario, []):
            cname = docker.get_container_name(svc)
            m = ResourceMonitor(cname)
            if m.start():
                monitors[cname] = m

        t_q0 = time.time()
        result = _run_queries(engine.get_executor(), scenario, protocol, result, export_dir, query_ids=selected)
        query_elapsed = time.time() - t_q0

        query_stats: Dict[str, Dict] = {"duration_s": round(query_elapsed, 3), "containers": {}}
        for cname, m in monitors.items():
            stats = m.stop()
            query_stats["containers"][cname] = {
                "mem_mb_avg": round(stats.mem_mb_avg, 1),
                "mem_mb_min": round(stats.mem_mb_min, 1),
                "mem_mb_max": round(stats.mem_mb_max, 1),
                "cpu_pct_avg": round(stats.cpu_pct_avg, 1),
                "samples": stats.samples,
            }
        result.system_info["query_phase"] = query_stats

    finally:
        engine.close()

    return result


def _run_memgraph(
    scenario: str,
    export_dir: Path,
    protocol: Protocol,
    result: BenchmarkResult,
    query_ids: Optional[list[str]] = None,
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

        selected = query_ids or QUERIES

        # M1: load chunks, M2: load timeseries to TimescaleDB
        ts_rows = 0
        if scenario == "M1" and _queries_need_timeseries(selected) and files.get("chunks"):
            ts_rows = engine.load_chunks(files["chunks"])
        elif scenario == "M2" and _queries_need_timeseries(selected):
            ts_csv = export_dir / "timeseries.csv"
            if ts_csv.exists():
                ts_engine = TimescaleEngine()
                ts_engine.connect()
                ts_engine.create_timeseries_schema()
                try:
                    ts_rows = ts_engine.load_timeseries_parallel_copy(
                        "/data/timeseries.csv",
                        container_name=docker.get_container_name("timescaledb"),
                        workers=int(os.getenv("BTB_TS_PARALLEL_COPY_WORKERS", "8")),
                        batch_size=int(os.getenv("BTB_TS_PARALLEL_COPY_BATCH_SIZE", "50000")),
                    )
                except Exception as e:
                    print(f"  [WARN] parallel-copy failed ({e}); trying server-side COPY...")
                    try:
                        ts_rows = ts_engine.load_timeseries_server_copy("/data/timeseries.csv")
                    except Exception as e2:
                        print(f"  [WARN] Server-side COPY failed ({e2}), falling back to client-side...")
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

        print(f"\n[4] Running queries ({len(selected)} queries)...")

        monitors: Dict[str, ResourceMonitor] = {}
        for svc in docker.SCENARIO_CONTAINERS.get(scenario, []):
            cname = docker.get_container_name(svc)
            m = ResourceMonitor(cname)
            if m.start():
                monitors[cname] = m

        t_q0 = time.time()
        result = _run_queries(engine.get_executor(), scenario, protocol, result, export_dir, query_ids=selected)
        query_elapsed = time.time() - t_q0

        query_stats: Dict[str, Dict] = {"duration_s": round(query_elapsed, 3), "containers": {}}
        for cname, m in monitors.items():
            stats = m.stop()
            query_stats["containers"][cname] = {
                "mem_mb_avg": round(stats.mem_mb_avg, 1),
                "mem_mb_min": round(stats.mem_mb_min, 1),
                "mem_mb_max": round(stats.mem_mb_max, 1),
                "cpu_pct_avg": round(stats.cpu_pct_avg, 1),
                "samples": stats.samples,
            }
        result.system_info["query_phase"] = query_stats

    finally:
        engine.close()

    return result


def _run_oxigraph(
    scenario: str,
    export_dir: Path,
    protocol: Protocol,
    result: BenchmarkResult,
    query_ids: Optional[list[str]] = None,
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

        selected = query_ids or QUERIES

        if scenario == "O1" and _queries_need_timeseries(selected) and files.get("chunks"):
            triples += engine.load_ntriples(files["chunks"])

        # O2: load timeseries to TimescaleDB
        ts_rows = 0
        if scenario == "O2" and _queries_need_timeseries(selected):
            ts_csv = export_dir / "timeseries.csv"
            if ts_csv.exists():
                ts_engine = TimescaleEngine()
                ts_engine.connect()
                ts_engine.create_timeseries_schema()
                try:
                    ts_rows = ts_engine.load_timeseries_parallel_copy(
                        "/data/timeseries.csv",
                        container_name=docker.get_container_name("timescaledb"),
                        workers=int(os.getenv("BTB_TS_PARALLEL_COPY_WORKERS", "8")),
                        batch_size=int(os.getenv("BTB_TS_PARALLEL_COPY_BATCH_SIZE", "50000")),
                    )
                except Exception as e:
                    print(f"  [WARN] parallel-copy failed ({e}); trying server-side COPY...")
                    try:
                        ts_rows = ts_engine.load_timeseries_server_copy("/data/timeseries.csv")
                    except Exception as e2:
                        print(f"  [WARN] Server-side COPY failed ({e2}), falling back to client-side...")
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

        print(f"\n[4] Running queries ({len(selected)} queries)...")

        monitors: Dict[str, ResourceMonitor] = {}
        for svc in docker.SCENARIO_CONTAINERS.get(scenario, []):
            cname = docker.get_container_name(svc)
            m = ResourceMonitor(cname)
            if m.start():
                monitors[cname] = m

        t_q0 = time.time()
        result = _run_queries(engine.get_executor(), scenario, protocol, result, export_dir, query_ids=selected)
        query_elapsed = time.time() - t_q0

        query_stats: Dict[str, Dict] = {"duration_s": round(query_elapsed, 3), "containers": {}}
        for cname, m in monitors.items():
            stats = m.stop()
            query_stats["containers"][cname] = {
                "mem_mb_avg": round(stats.mem_mb_avg, 1),
                "mem_mb_min": round(stats.mem_mb_min, 1),
                "mem_mb_max": round(stats.mem_mb_max, 1),
                "cpu_pct_avg": round(stats.cpu_pct_avg, 1),
                "samples": stats.samples,
            }
        result.system_info["query_phase"] = query_stats

    finally:
        engine.close()

    return result


def _run_queries(
    executor,
    scenario: str,
    protocol: Protocol,
    result: BenchmarkResult,
    export_dir: Path,
    query_ids: Optional[list[str]] = None,
) -> BenchmarkResult:
    """Run all queries with warmup and measurement using parameter variants.

    Args:
        executor: Function that executes queries (query -> (rows, latency_ms))
        scenario: Scenario code
        protocol: Benchmark protocol
        result: Result object to update
        export_dir: Export directory for extracting dataset info

    Returns:
        Updated result
    """
    # Extract dataset info for parameterization
    nodes_csv = get_nodes_csv_path(export_dir, scenario)
    if nodes_csv.exists():
        dataset_info = extract_dataset_info(nodes_csv, scenario)
    else:
        nodes_parquet = export_dir / "parquet" / "nodes.parquet"
        dataset_info = extract_dataset_info_from_parquet(nodes_parquet)

    # Add timeseries range (prefer CSV if present; else use parquet stats)
    ts_csv = export_dir / "timeseries.csv"
    if ts_csv.exists():
        dataset_info.update(extract_timeseries_range(ts_csv))
    else:
        ts_parquet = export_dir / "parquet" / "timeseries.parquet"
        dataset_info.update(extract_timeseries_range_from_parquet(ts_parquet))

    for query_id in (query_ids or QUERIES):
        query_text = load_query(scenario, query_id)
        if not query_text:
            print(f"  [{query_id}] SKIP - query file not found")
            continue

        qr = QueryResult(query_id=query_id)

        # Generate parameter variants
        variants = get_query_variants(
            query_id=query_id,
            profile=result.profile,
            dataset_info=dataset_info,
            seed=42,
            scenario=scenario,
            n_variants=protocol.n_variants,
        )

        # Warmup with first variant
        if variants:
            warmup_query = substitute_params(query_text, variants[0])
            for _ in range(protocol.n_warmup):
                try:
                    executor(warmup_query)
                except Exception:
                    pass

        # Measurement runs across all variants
        for variant in variants:
            variant_query = substitute_params(query_text, variant)
            for run in range(protocol.n_runs):
                try:
                    rows, latency_ms = executor(variant_query)
                    qr.latencies_ms.append(latency_ms)
                    qr.rows = rows
                except Exception as e:
                    qr.errors.append(str(e))

        result.queries[query_id] = qr
        n_total = len(variants) * protocol.n_runs
        status = f"p95={qr.p95_ms:.1f}ms, rows={qr.rows}, variants={len(variants)}, runs={n_total}"
        if qr.errors:
            status += f", errors={len(qr.errors)}"
        print(f"  [{query_id}] {status}")

    return result
