#!/usr/bin/env python3
"""
Benchmark runner for BaseType Benchmark.

This script orchestrates isolated benchmark runs across different database scenarios.
Each scenario runs in complete isolation (single container, clean state).

Scenarios:
  P1: PostgreSQL relational (tables + TimescaleDB)
  P2: PostgreSQL JSONB (flexible schema + TimescaleDB)
  M1: Memgraph standalone (graph + in-memory timeseries)
  M2: Memgraph + TimescaleDB (graph + external timeseries)
  O1: Oxigraph standalone (RDF + literal timeseries)
  O2: Oxigraph + TimescaleDB (RDF + external timeseries)

Usage:
  python -m scripts.run_benchmark --interactive
  python -m scripts.run_benchmark --profile small-2d --scenarios P1,P2,M1
  python -m scripts.run_benchmark --full-matrix  # All 72 combinations
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCKER_DIR = PROJECT_ROOT / "docker"
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

# Default author info
DEFAULT_AUTHOR = "Antoine Debienne"
DEFAULT_ORCID = "0009-0002-6674-2691"

# Scenario definitions
SCENARIOS = {
    "P1": {
        "name": "PostgreSQL Relational",
        "containers": ["timescaledb"],
        "structure": "SQL tables",
        "timeseries": "Hypertables",
        "ram_estimate_mb": 512,
    },
    "P2": {
        "name": "PostgreSQL JSONB",
        "containers": ["timescaledb"],
        "structure": "JSONB",
        "timeseries": "Hypertables",
        "ram_estimate_mb": 512,
    },
    "M1": {
        "name": "Memgraph Standalone",
        "containers": ["memgraph"],
        "structure": "Property Graph",
        "timeseries": "In-memory arrays",
        "ram_estimate_mb": 4096,
    },
    "M2": {
        "name": "Memgraph + TimescaleDB",
        "containers": ["memgraph", "timescaledb"],
        "structure": "Property Graph",
        "timeseries": "Hypertables (external)",
        "ram_estimate_mb": 4608,
    },
    "O1": {
        "name": "Oxigraph Standalone",
        "containers": ["oxigraph"],
        "structure": "RDF Triples",
        "timeseries": "RDF Literals",
        "ram_estimate_mb": 1024,
    },
    "O2": {
        "name": "Oxigraph + TimescaleDB",
        "containers": ["oxigraph", "timescaledb"],
        "structure": "RDF Triples",
        "timeseries": "Hypertables (external)",
        "ram_estimate_mb": 1536,
    },
}

# Scale profiles RAM multipliers
SCALE_RAM_MULTIPLIER = {
    "small": 1.0,
    "medium": 2.5,
    "large": 10.0,
}

# Available profiles
SCALES = ["small", "medium", "large"]
DURATIONS = ["2d", "1w", "1m", "6m", "1y"]


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    scenario: str
    profile: str
    timestamp: str
    success: bool
    ingestion_time_s: float = 0.0
    query_results: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # Memory metrics
    ram_initial_mb: float = 0.0
    ram_after_load_mb: float = 0.0
    ram_peak_mb: float = 0.0
    ram_steady_mb: float = 0.0  # kept for backwards compatibility
    # CPU metrics
    cpu_avg_percent: float = 0.0
    cpu_peak_percent: float = 0.0
    # I/O metrics
    net_io_mb: float = 0.0
    block_io_read_mb: float = 0.0
    block_io_write_mb: float = 0.0
    # Disk usage
    disk_mb: float = 0.0
    # Per-container stats
    per_container_stats: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # Data counts
    nodes_count: int = 0
    edges_count: int = 0
    timeseries_count: int = 0
    error: Optional[str] = None


@dataclass
class BenchmarkSuite:
    """Complete benchmark suite results."""
    started_at: str
    completed_at: str = ""
    profile: str = ""
    scenarios_requested: List[str] = field(default_factory=list)
    results: List[BenchmarkResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "profile": self.profile,
            "scenarios_requested": self.scenarios_requested,
            "results": [asdict(r) for r in self.results],
        }


def run_command(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a command and return result."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def log_progress(message: str, current: int = 0, total: int = 0) -> None:
    """Print progress message with optional counter."""
    if total > 0:
        pct = (current / total) * 100
        print(f"  [{current:,}/{total:,}] ({pct:.1f}%) {message}", flush=True)
    else:
        print(f"  {message}", flush=True)


def stop_all_containers() -> None:
    """Stop all benchmark containers and clean volumes."""
    print("[CLEANUP] Stopping all containers...")
    run_command(["docker", "compose", "down", "-v"], cwd=DOCKER_DIR, timeout=60)
    # Also stop any stray containers
    for container in ["btb_timescaledb", "btb_memgraph", "btb_oxigraph"]:
        run_command(["docker", "rm", "-f", container], timeout=30)
    time.sleep(2)

    # Verify no containers running
    result = run_command(["docker", "ps", "-q", "--filter", "name=btb_"], timeout=10)
    if result.stdout.strip():
        print("[WARNING] Some containers still running, forcing stop...")
        run_command(["docker", "stop"] + result.stdout.strip().split(), timeout=30)
    print("[CLEANUP] Environment cleared")


def start_containers(containers: List[str]) -> bool:
    """Start specific containers and wait for healthy/running state."""
    print(f"Starting containers: {', '.join(containers)}...")

    # Start only requested containers
    result = run_command(
        ["docker", "compose", "up", "-d"] + containers,
        cwd=DOCKER_DIR,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"Error starting containers: {result.stderr}")
        return False

    # Wait for healthy/running state
    max_wait = 90
    waited = 0
    while waited < max_wait:
        all_ready = True
        for container in containers:
            container_name = f"btb_{container}"

            # Check health status
            check = run_command(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_name],
                timeout=10,
            )
            health_status = check.stdout.strip()

            # If healthcheck disabled or not configured, check running state
            if health_status in ["", "none"]:
                check = run_command(
                    ["docker", "inspect", "--format", "{{.State.Running}}", container_name],
                    timeout=10,
                )
                running = check.stdout.strip() == "true"
                if not running:
                    all_ready = False
                    break
                # For oxigraph, verify HTTP response from host
                if container == "oxigraph":
                    import requests
                    try:
                        resp = requests.get("http://localhost:7878", timeout=2)
                        if resp.status_code >= 500:
                            all_ready = False
                            break
                    except Exception:
                        all_ready = False
                        break
            elif health_status != "healthy":
                all_ready = False
                break

        if all_ready:
            print(f"All containers ready after {waited}s")
            return True

        time.sleep(2)
        waited += 2

    print(f"Timeout waiting for containers to be ready")
    return False


def get_container_stats(containers: List[str]) -> Dict[str, Any]:
    """Get current resource stats for containers with detailed metrics."""
    stats = {
        "ram_mb": 0.0,
        "cpu_percent": 0.0,
        "net_io_mb": 0.0,
        "block_io_mb": 0.0,
        "per_container": {},
    }

    for container in containers:
        container_name = f"btb_{container}"
        result = run_command(
            ["docker", "stats", "--no-stream", "--format",
             "{{.MemUsage}}\t{{.CPUPerc}}\t{{.NetIO}}\t{{.BlockIO}}", container_name],
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("\t")
            container_stats = {"ram_mb": 0.0, "cpu_percent": 0.0}

            if len(parts) >= 2:
                # Parse memory (e.g., "256MiB / 1GiB")
                mem_str = parts[0].split("/")[0].strip()
                if "GiB" in mem_str:
                    container_stats["ram_mb"] = float(mem_str.replace("GiB", "")) * 1024
                elif "MiB" in mem_str:
                    container_stats["ram_mb"] = float(mem_str.replace("MiB", ""))
                elif "kB" in mem_str or "KiB" in mem_str:
                    container_stats["ram_mb"] = float(mem_str.replace("kB", "").replace("KiB", "")) / 1024

                stats["ram_mb"] += container_stats["ram_mb"]

                # Parse CPU (e.g., "2.5%")
                cpu_str = parts[1].replace("%", "").strip()
                try:
                    container_stats["cpu_percent"] = float(cpu_str)
                    stats["cpu_percent"] += container_stats["cpu_percent"]
                except ValueError:
                    pass

            if len(parts) >= 3:
                # Parse Net I/O (e.g., "1.5MB / 2.3MB")
                try:
                    net_in = parts[2].split("/")[0].strip()
                    if "GB" in net_in:
                        stats["net_io_mb"] += float(net_in.replace("GB", "")) * 1024
                    elif "MB" in net_in:
                        stats["net_io_mb"] += float(net_in.replace("MB", ""))
                    elif "kB" in net_in:
                        stats["net_io_mb"] += float(net_in.replace("kB", "")) / 1024
                except (ValueError, IndexError):
                    pass

            if len(parts) >= 4:
                # Parse Block I/O (e.g., "10MB / 5MB")
                try:
                    block_in = parts[3].split("/")[0].strip()
                    if "GB" in block_in:
                        stats["block_io_mb"] += float(block_in.replace("GB", "")) * 1024
                    elif "MB" in block_in:
                        stats["block_io_mb"] += float(block_in.replace("MB", ""))
                    elif "kB" in block_in:
                        stats["block_io_mb"] += float(block_in.replace("kB", "")) / 1024
                except (ValueError, IndexError):
                    pass

            stats["per_container"][container] = container_stats

    return stats


def check_dataset_exists(profile: str) -> bool:
    """Check if dataset exists locally."""
    scale, duration = profile.split("-")
    data_path = DATA_DIR / profile
    parquet_path = data_path / "data" / "graph" / "nodes.parquet"
    json_path = DATA_DIR / profile / "json" / "nodes.json"

    return parquet_path.exists() or json_path.exists()


def generate_dataset(profile: str, author: str = "", orcid: str = "") -> bool:
    """Generate dataset for given profile."""
    print(f"\nGenerating dataset: {profile}")

    cmd = [
        sys.executable, "-m", "scripts.publish_to_huggingface",
        f"--profile={profile}",
        "--skip-publish",
        f"--data-dir={DATA_DIR / profile}",
    ]

    if author:
        cmd.append(f"--author-name={author}")
    if orcid:
        cmd.append(f"--author-orcid={orcid}")

    result = run_command(cmd, cwd=PROJECT_ROOT, timeout=600)

    if result.returncode != 0:
        print(f"Error generating dataset: {result.stderr}")
        return False

    print(result.stdout)
    return True


def export_json_format(profile: str) -> bool:
    """Export dataset to JSON lines format for Memgraph/Oxigraph."""
    print(f"Exporting {profile} to JSON format...")

    json_dir = DATA_DIR / profile / "json"
    if (json_dir / "nodes.json").exists():
        print("JSON export already exists")
        return True

    # Use Python to export
    export_script = f'''
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path("{PROJECT_ROOT}/src")))

from basetype_benchmark.dataset.config import PROFILES
from basetype_benchmark.dataset.generator import generate_dataset

profile = PROFILES["{profile}"]
dataset, summary = generate_dataset(profile, seed=42)

out_dir = Path("{json_dir}")
out_dir.mkdir(parents=True, exist_ok=True)

with (out_dir / "nodes.json").open("w") as f:
    for node in dataset.nodes:
        json.dump({{"id": node.id, "type": node.type.value, "name": node.name, "building_id": node.properties.get("building_id", 0), "properties": node.properties}}, f)
        f.write("\\n")

with (out_dir / "edges.json").open("w") as f:
    for edge in dataset.edges:
        json.dump({{"src": edge.src, "dst": edge.dst, "rel": edge.rel.value}}, f)
        f.write("\\n")
    for measure in dataset.measures:
        json.dump({{"src": measure.src, "dst": measure.quantity, "rel": "MEASURES"}}, f)
        f.write("\\n")

print(f"Exported to {{out_dir}}")
'''

    result = subprocess.run(
        [sys.executable, "-c", export_script],
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"Error exporting: {result.stderr}")
        return False

    return True


def load_scenario_data(scenario_id: str, profile: str) -> bool:
    """Load data for a specific scenario."""
    data_dir = DATA_DIR / profile / "json"

    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return False

    try:
        if scenario_id in ["P1", "P2"]:
            return _load_postgres(scenario_id, data_dir)
        elif scenario_id in ["M1", "M2"]:
            return _load_memgraph(scenario_id, data_dir)
        elif scenario_id in ["O1", "O2"]:
            return _load_oxigraph(scenario_id, data_dir)
        else:
            print(f"Unknown scenario: {scenario_id}")
            return False
    except Exception as e:
        print(f"Load error: {e}")
        return False


def _load_postgres(scenario_id: str, data_dir: Path) -> bool:
    """Load data into PostgreSQL/TimescaleDB."""
    import psycopg2
    from psycopg2.extras import execute_batch

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="benchmark",
        password="benchmark",
        database="benchmark"
    )

    try:
        with conn.cursor() as cur:
            # Clear existing data
            cur.execute("DROP TABLE IF EXISTS timeseries CASCADE")
            cur.execute("DROP TABLE IF EXISTS edges CASCADE")
            cur.execute("DROP TABLE IF EXISTS nodes CASCADE")
            cur.execute("DROP TABLE IF EXISTS nodes_jsonb CASCADE")
            conn.commit()

            if scenario_id == "P1":
                # Relational schema with JSONB properties
                cur.execute("""
                    CREATE TABLE nodes (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        name TEXT,
                        building_id INTEGER DEFAULT 0,
                        properties JSONB DEFAULT '{}'::jsonb
                    );
                    CREATE INDEX idx_nodes_type ON nodes(type);
                    CREATE INDEX idx_nodes_properties ON nodes USING GIN (properties);
                """)

                cur.execute("""
                    CREATE TABLE edges (
                        id SERIAL PRIMARY KEY,
                        src_id TEXT NOT NULL,
                        dst_id TEXT NOT NULL,
                        rel_type TEXT NOT NULL
                    );
                    CREATE INDEX idx_edges_src ON edges(src_id);
                    CREATE INDEX idx_edges_dst ON edges(dst_id);
                """)
            else:
                # JSONB schema (P2)
                cur.execute("""
                    CREATE TABLE nodes_jsonb (
                        id TEXT PRIMARY KEY,
                        data JSONB NOT NULL
                    );
                    CREATE INDEX idx_nodes_jsonb_type ON nodes_jsonb ((data->>'type'));
                """)

                cur.execute("""
                    CREATE TABLE edges (
                        id SERIAL PRIMARY KEY,
                        src_id TEXT NOT NULL,
                        dst_id TEXT NOT NULL,
                        rel_type TEXT NOT NULL
                    );
                """)

            # Create timeseries hypertable
            cur.execute("""
                CREATE TABLE timeseries (
                    time TIMESTAMPTZ NOT NULL,
                    point_id TEXT NOT NULL,
                    value DOUBLE PRECISION
                );
                SELECT create_hypertable('timeseries', 'time',
                    if_not_exists => TRUE,
                    chunk_time_interval => INTERVAL '1 day');
            """)
            conn.commit()

        # Count lines for progress
        nodes_path = data_dir / "nodes.json"
        edges_path = data_dir / "edges.json"
        total_nodes = sum(1 for _ in nodes_path.open())
        total_edges = sum(1 for _ in edges_path.open())

        # Load nodes
        log_progress(f"Loading nodes...", 0, total_nodes)
        batch = []
        loaded = 0
        with nodes_path.open() as f:
            for line in f:
                if line.strip():
                    node = json.loads(line)
                    if scenario_id == "P1":
                        props = node.get("properties", {})
                        batch.append((node["id"], node["type"], node.get("name", ""), node.get("building_id", 0), json.dumps(props)))
                    else:
                        batch.append((node["id"], json.dumps(node)))

                    if len(batch) >= 1000:
                        with conn.cursor() as cur:
                            if scenario_id == "P1":
                                execute_batch(cur, "INSERT INTO nodes (id, type, name, building_id, properties) VALUES (%s, %s, %s, %s, %s::jsonb)", batch)
                            else:
                                execute_batch(cur, "INSERT INTO nodes_jsonb (id, data) VALUES (%s, %s::jsonb)", batch)
                        conn.commit()
                        loaded += len(batch)
                        if loaded % 10000 == 0:
                            log_progress("Nodes", loaded, total_nodes)
                        batch.clear()

        if batch:
            with conn.cursor() as cur:
                if scenario_id == "P1":
                    execute_batch(cur, "INSERT INTO nodes (id, type, name, building_id, properties) VALUES (%s, %s, %s, %s, %s::jsonb)", batch)
                else:
                    execute_batch(cur, "INSERT INTO nodes_jsonb (id, data) VALUES (%s, %s::jsonb)", batch)
            conn.commit()
            loaded += len(batch)
        log_progress("Nodes complete", loaded, total_nodes)

        # Load edges
        log_progress(f"Loading edges...", 0, total_edges)
        batch = []
        loaded = 0
        with edges_path.open() as f:
            for line in f:
                if line.strip():
                    edge = json.loads(line)
                    batch.append((edge["src"], edge["dst"], edge["rel"]))

                    if len(batch) >= 1000:
                        with conn.cursor() as cur:
                            execute_batch(cur, "INSERT INTO edges (src_id, dst_id, rel_type) VALUES (%s, %s, %s)", batch)
                        conn.commit()
                        loaded += len(batch)
                        if loaded % 10000 == 0:
                            log_progress("Edges", loaded, total_edges)
                        batch.clear()

        if batch:
            with conn.cursor() as cur:
                execute_batch(cur, "INSERT INTO edges (src_id, dst_id, rel_type) VALUES (%s, %s, %s)", batch)
            conn.commit()
            loaded += len(batch)
        log_progress("Edges complete", loaded, total_edges)

        # Load timeseries if file exists (using COPY for speed)
        timeseries_path = data_dir / "timeseries.json"
        ts_count = 0
        if timeseries_path.exists():
            import io
            file_size = timeseries_path.stat().st_size
            total_ts = file_size // 70  # estimate
            log_progress(f"Loading timeseries (~{total_ts:,} estimated) via COPY...", 0, total_ts)

            loaded = 0
            buffer = io.StringIO()
            buffer_count = 0
            BATCH_SIZE = 500000  # 500K rows per COPY batch

            with timeseries_path.open() as f:
                for line in f:
                    if line.strip():
                        ts = json.loads(line)
                        # Tab-separated format for COPY
                        buffer.write(f"{ts['time']}\t{ts['point_id']}\t{ts['value']}\n")
                        buffer_count += 1

                        if buffer_count >= BATCH_SIZE:
                            buffer.seek(0)
                            with conn.cursor() as cur:
                                cur.copy_from(buffer, 'timeseries', columns=('time', 'point_id', 'value'))
                            conn.commit()
                            loaded += buffer_count
                            log_progress("Timeseries", loaded, total_ts)
                            buffer = io.StringIO()
                            buffer_count = 0

            # Final batch
            if buffer_count > 0:
                buffer.seek(0)
                with conn.cursor() as cur:
                    cur.copy_from(buffer, 'timeseries', columns=('time', 'point_id', 'value'))
                conn.commit()
                loaded += buffer_count

            log_progress("Timeseries complete", loaded, total_ts)
            ts_count = loaded

        # Count records
        with conn.cursor() as cur:
            if scenario_id == "P1":
                cur.execute("SELECT COUNT(*) FROM nodes")
            else:
                cur.execute("SELECT COUNT(*) FROM nodes_jsonb")
            nodes_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM edges")
            edges_count = cur.fetchone()[0]

        if ts_count > 0:
            print(f"  Loaded {nodes_count} nodes, {edges_count} edges, {ts_count:,} timeseries")
        else:
            print(f"  Loaded {nodes_count} nodes, {edges_count} edges")
        return True

    finally:
        conn.close()


def _load_memgraph(scenario_id: str, data_dir: Path) -> bool:
    """Load data into Memgraph."""
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver("bolt://localhost:7688", auth=None)

    try:
        with driver.session() as session:
            # Clear existing data
            log_progress("Clearing existing data...")
            session.run("MATCH (n) DETACH DELETE n")

            # Create constraint and index BEFORE loading (critical for performance)
            log_progress("Creating index on Node.id...")
            try:
                session.run("CREATE CONSTRAINT ON (n:Node) ASSERT n.id IS UNIQUE")
            except Exception:
                pass  # Constraint may already exist

            try:
                session.run("CREATE INDEX ON :Node(id)")
            except Exception:
                pass  # Index may already exist

            # Count lines for progress
            nodes_path = data_dir / "nodes.json"
            edges_path = data_dir / "edges.json"
            total_nodes = sum(1 for _ in nodes_path.open())
            total_edges = sum(1 for _ in edges_path.open())

            # Load nodes with all properties
            log_progress("Loading nodes...", 0, total_nodes)
            batch = []
            loaded_nodes = 0

            with nodes_path.open() as f:
                for line in f:
                    if line.strip():
                        node = json.loads(line)
                        # Flatten properties into node for Memgraph
                        flat_node = {
                            "id": node["id"],
                            "type": node["type"],
                            "name": node.get("name", ""),
                            "building_id": node.get("building_id", 0),
                        }
                        # Add all properties as direct attributes
                        props = node.get("properties", {})
                        for k, v in props.items():
                            flat_node[k] = v
                        batch.append(flat_node)

                        if len(batch) >= 1000:
                            # Use APOC-like syntax for dynamic properties
                            session.run(
                                "UNWIND $batch AS row "
                                "CREATE (n:Node) SET n = row",
                                batch=batch
                            )
                            loaded_nodes += len(batch)
                            if loaded_nodes % 10000 == 0:
                                log_progress("Nodes", loaded_nodes, total_nodes)
                            batch.clear()

            if batch:
                session.run(
                    "UNWIND $batch AS row "
                    "CREATE (n:Node) SET n = row",
                    batch=batch
                )
                loaded_nodes += len(batch)
            log_progress("Nodes complete", loaded_nodes, total_nodes)

            # Load edges (with progress)
            log_progress("Loading edges...", 0, total_edges)
            batch = []
            loaded_edges = 0

            with edges_path.open() as f:
                for line in f:
                    if line.strip():
                        edge = json.loads(line)
                        batch.append(edge)

                        if len(batch) >= 500:
                            _flush_memgraph_edges(session, batch)
                            loaded_edges += len(batch)
                            if loaded_edges % 5000 == 0:
                                log_progress("Edges", loaded_edges, total_edges)
                            batch.clear()

            if batch:
                _flush_memgraph_edges(session, batch)
                loaded_edges += len(batch)
            log_progress("Edges complete", loaded_edges, total_edges)

            print(f"  Loaded {loaded_nodes} nodes, {loaded_edges} edges", flush=True)
            return True

    except Exception as e:
        print(f"  [ERROR] Memgraph load failed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False

    finally:
        driver.close()


def _flush_memgraph_edges(session, batch: List[Dict]) -> None:
    """Flush edges to Memgraph grouped by relationship type."""
    by_rel = {}
    for edge in batch:
        rel = edge["rel"]
        if rel not in by_rel:
            by_rel[rel] = []
        by_rel[rel].append(edge)

    for rel, edges in by_rel.items():
        if rel == "MEASURES":
            session.run(
                "UNWIND $batch AS row "
                "MATCH (p:Node {id: row.src}) "
                "SET p.quantity = row.dst",
                batch=edges
            )
        else:
            session.run(
                f"UNWIND $batch AS row "
                f"MATCH (s:Node {{id: row.src}}) "
                f"MATCH (d:Node {{id: row.dst}}) "
                f"CREATE (s)-[:{rel}]->(d)",
                batch=edges
            )


def _load_oxigraph(scenario_id: str, data_dir: Path) -> bool:
    """Load data into Oxigraph."""
    import requests

    endpoint = "http://localhost:7878"

    # Clear existing data
    log_progress("Clearing existing data...")
    try:
        requests.delete(f"{endpoint}/store", timeout=30)
    except Exception:
        pass

    # Count lines for progress
    nodes_path = data_dir / "nodes.json"
    edges_path = data_dir / "edges.json"
    total_nodes = sum(1 for _ in nodes_path.open())
    total_edges = sum(1 for _ in edges_path.open())

    # Convert JSON to simple N-Triples format
    triples = []

    # Load nodes
    log_progress("Building node triples...", 0, total_nodes)
    loaded = 0
    with nodes_path.open() as f:
        for line in f:
            if line.strip():
                node = json.loads(line)
                node_uri = f"<http://benchmark.org/node/{node['id']}>"
                triples.append(f'{node_uri} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://benchmark.org/type/{node["type"]}> .')
                if node.get("name"):
                    name_escaped = node["name"].replace('"', '\\"')
                    triples.append(f'{node_uri} <http://benchmark.org/name> "{name_escaped}" .')
                loaded += 1
                if loaded % 20000 == 0:
                    log_progress("Nodes", loaded, total_nodes)
    log_progress("Nodes complete", loaded, total_nodes)

    # Load edges
    log_progress("Building edge triples...", 0, total_edges)
    loaded = 0
    with edges_path.open() as f:
        for line in f:
            if line.strip():
                edge = json.loads(line)
                src_uri = f"<http://benchmark.org/node/{edge['src']}>"
                dst_uri = f"<http://benchmark.org/node/{edge['dst']}>"
                rel_uri = f"<http://benchmark.org/rel/{edge['rel']}>"
                triples.append(f"{src_uri} {rel_uri} {dst_uri} .")
                loaded += 1
                if loaded % 20000 == 0:
                    log_progress("Edges", loaded, total_edges)
    log_progress("Edges complete", loaded, total_edges)

    # Post to Oxigraph
    log_progress(f"Uploading {len(triples):,} triples to Oxigraph...")
    payload = "\n".join(triples)
    response = requests.post(
        f"{endpoint}/store",
        headers={"Content-Type": "application/n-triples"},
        data=payload.encode("utf-8"),
        timeout=300
    )

    if response.status_code >= 400:
        print(f"  [ERROR] Oxigraph load error: {response.status_code} - {response.text}")
        return False

    # Count triples
    query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
    response = requests.post(
        f"{endpoint}/query",
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=30
    )

    if response.status_code == 200:
        count = response.json()["results"]["bindings"][0]["count"]["value"]
        print(f"  [OK] Loaded {count} triples")

    return True


# Query definitions per scenario type
QUERIES_DIR = PROJECT_ROOT / "src" / "basetype_benchmark" / "queries"

# Which queries to run per engine type
ACTIVE_QUERIES = {
    "pg": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12"],
    "memgraph": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q8", "Q9", "Q10", "Q11", "Q12"],
    "oxigraph": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q8", "Q9", "Q10", "Q11", "Q12"],
}


def run_scenario_queries(scenario_id: str, profile: str) -> Dict[str, Dict[str, float]]:
    """Run benchmark queries for a scenario using real query files."""
    results = {}

    try:
        if scenario_id in ["P1", "P2"]:
            results = _run_postgres_queries(scenario_id)
        elif scenario_id in ["M1", "M2"]:
            results = _run_memgraph_queries(scenario_id)
        elif scenario_id in ["O1", "O2"]:
            results = _run_oxigraph_queries(scenario_id)
    except Exception as e:
        print(f"Query error: {e}")
        import traceback
        traceback.print_exc()
        results = {"error": {"message": str(e)}}

    return results


def _run_postgres_queries(scenario_id: str) -> Dict[str, Dict[str, float]]:
    """Run PostgreSQL benchmark queries from SQL files."""
    import psycopg2

    results = {}
    conn = psycopg2.connect(
        host="localhost", port=5432,
        user="benchmark", password="benchmark", database="benchmark"
    )
    conn.autocommit = True

    sql_dir = QUERIES_DIR / "sql"
    active = ACTIVE_QUERIES["pg"]

    try:
        with conn.cursor() as cur:
            for query_id in active:
                # Find query file
                query_files = list(sql_dir.glob(f"{query_id}_*.sql"))
                if not query_files:
                    print(f"  [SKIP] {query_id}: no SQL file found")
                    continue

                query_file = query_files[0]
                query_name = query_file.stem

                # Read query
                query_sql = query_file.read_text()

                # Execute with timing
                t0 = time.time()
                try:
                    cur.execute(query_sql)
                    rows = cur.fetchall()
                    elapsed_ms = (time.time() - t0) * 1000
                    row_count = len(rows)

                    results[query_name] = {
                        "p50_ms": elapsed_ms,
                        "row_count": row_count,
                    }
                    print(f"  [OK] {query_id}: {elapsed_ms:.2f}ms, {row_count} rows")

                except Exception as e:
                    elapsed_ms = (time.time() - t0) * 1000
                    results[query_name] = {
                        "p50_ms": elapsed_ms,
                        "error": str(e),
                    }
                    print(f"  [ERR] {query_id}: {e}")

    finally:
        conn.close()

    return results


def _run_memgraph_queries(scenario_id: str) -> Dict[str, Dict[str, float]]:
    """Run Memgraph benchmark queries from Cypher files."""
    from neo4j import GraphDatabase

    results = {}
    driver = GraphDatabase.driver("bolt://localhost:7688", auth=None)

    cypher_dir = QUERIES_DIR / "cypher"
    active = ACTIVE_QUERIES["memgraph"]

    try:
        with driver.session() as session:
            for query_id in active:
                # Find query file
                query_files = list(cypher_dir.glob(f"{query_id}_*.cypher"))
                if not query_files:
                    print(f"  [SKIP] {query_id}: no Cypher file found")
                    continue

                query_file = query_files[0]
                query_name = query_file.stem

                # Read query
                query_cypher = query_file.read_text()

                # Execute with timing
                t0 = time.time()
                try:
                    result = session.run(query_cypher)
                    records = list(result)
                    elapsed_ms = (time.time() - t0) * 1000
                    row_count = len(records)

                    results[query_name] = {
                        "p50_ms": elapsed_ms,
                        "row_count": row_count,
                    }
                    print(f"  [OK] {query_id}: {elapsed_ms:.2f}ms, {row_count} rows")

                except Exception as e:
                    elapsed_ms = (time.time() - t0) * 1000
                    results[query_name] = {
                        "p50_ms": elapsed_ms,
                        "error": str(e),
                    }
                    print(f"  [ERR] {query_id}: {e}")

    finally:
        driver.close()

    return results


def _run_oxigraph_queries(scenario_id: str) -> Dict[str, Dict[str, float]]:
    """Run Oxigraph benchmark queries from SPARQL files."""
    import requests

    results = {}
    endpoint = "http://localhost:7878"

    sparql_dir = QUERIES_DIR / "sparql"
    active = ACTIVE_QUERIES["oxigraph"]

    for query_id in active:
        # Find query file
        query_files = list(sparql_dir.glob(f"{query_id}_*.sparql"))
        if not query_files:
            print(f"  [SKIP] {query_id}: no SPARQL file found")
            continue

        query_file = query_files[0]
        query_name = query_file.stem

        # Read query
        query_sparql = query_file.read_text()

        # Execute with timing
        t0 = time.time()
        try:
            response = requests.post(
                f"{endpoint}/query",
                data={"query": query_sparql},
                headers={"Accept": "application/sparql-results+json"},
                timeout=120
            )
            elapsed_ms = (time.time() - t0) * 1000

            if response.status_code == 200:
                try:
                    data = response.json()
                    row_count = len(data.get("results", {}).get("bindings", []))
                except:
                    row_count = 0

                results[query_name] = {
                    "p50_ms": elapsed_ms,
                    "row_count": row_count,
                }
                print(f"  [OK] {query_id}: {elapsed_ms:.2f}ms, {row_count} rows")
            else:
                results[query_name] = {
                    "p50_ms": elapsed_ms,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}",
                }
                print(f"  [ERR] {query_id}: HTTP {response.status_code}")

        except Exception as e:
            elapsed_ms = (time.time() - t0) * 1000
            results[query_name] = {
                "p50_ms": elapsed_ms,
                "error": str(e),
            }
            print(f"  [ERR] {query_id}: {e}")

    return results


def get_disk_usage_mb(containers: List[str]) -> float:
    """Get disk usage for containers."""
    total_mb = 0.0
    for container in containers:
        container_name = f"btb_{container}"
        result = run_command(
            ["docker", "exec", container_name, "du", "-sm", "/var/lib"],
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                total_mb += float(result.stdout.split()[0])
            except (ValueError, IndexError):
                pass
    return total_mb


def run_scenario(scenario_id: str, profile: str) -> BenchmarkResult:
    """Run a single benchmark scenario with detailed metrics."""
    scenario = SCENARIOS[scenario_id]
    timestamp = datetime.now().isoformat()

    print(f"\n{'='*60}")
    print(f"SCENARIO: {scenario_id} - {scenario['name']}")
    print(f"Profile: {profile}")
    print(f"Containers: {', '.join(scenario['containers'])}")
    print(f"{'='*60}")

    result = BenchmarkResult(
        scenario=scenario_id,
        profile=profile,
        timestamp=timestamp,
        success=False,
    )

    # Track peak values during execution
    peak_ram_mb = 0.0
    peak_cpu_percent = 0.0
    cpu_samples = []

    try:
        # 1. Stop all containers (clean state)
        stop_all_containers()

        # 2. Start required containers
        if not start_containers(scenario["containers"]):
            result.error = "Failed to start containers"
            return result

        # 3. Get initial stats (before loading)
        initial_stats = get_container_stats(scenario["containers"])
        result.ram_initial_mb = initial_stats["ram_mb"]
        result.ram_steady_mb = initial_stats["ram_mb"]  # backwards compat
        peak_ram_mb = initial_stats["ram_mb"]

        # 4. Load data
        print("Loading data...")
        t0 = time.time()
        load_success = load_scenario_data(scenario_id, profile)
        result.ingestion_time_s = time.time() - t0

        if not load_success:
            result.error = "Data loading failed"
            return result

        # 5. Get stats after data load
        after_load_stats = get_container_stats(scenario["containers"])
        result.ram_after_load_mb = after_load_stats["ram_mb"]
        peak_ram_mb = max(peak_ram_mb, after_load_stats["ram_mb"])
        cpu_samples.append(after_load_stats["cpu_percent"])

        # Count loaded data
        data_dir = DATA_DIR / profile / "json"
        if (data_dir / "nodes.json").exists():
            with (data_dir / "nodes.json").open() as f:
                result.nodes_count = sum(1 for _ in f)
        if (data_dir / "edges.json").exists():
            with (data_dir / "edges.json").open() as f:
                result.edges_count = sum(1 for _ in f)
        if (data_dir / "timeseries.json").exists():
            result.timeseries_count = (data_dir / "timeseries.json").stat().st_size // 70  # estimate

        # 6. Run queries with periodic stats collection
        print("Running queries...")
        result.query_results = run_scenario_queries(scenario_id, profile)

        # Collect stats after each major phase
        during_query_stats = get_container_stats(scenario["containers"])
        peak_ram_mb = max(peak_ram_mb, during_query_stats["ram_mb"])
        cpu_samples.append(during_query_stats["cpu_percent"])
        peak_cpu_percent = max(peak_cpu_percent, during_query_stats["cpu_percent"])

        # 7. Get final stats
        final_stats = get_container_stats(scenario["containers"])
        peak_ram_mb = max(peak_ram_mb, final_stats["ram_mb"])
        cpu_samples.append(final_stats["cpu_percent"])
        peak_cpu_percent = max(peak_cpu_percent, final_stats["cpu_percent"])

        # Calculate averages and peaks
        result.ram_peak_mb = peak_ram_mb
        result.cpu_peak_percent = peak_cpu_percent
        result.cpu_avg_percent = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0

        # I/O metrics
        result.net_io_mb = final_stats.get("net_io_mb", 0.0)
        result.block_io_read_mb = final_stats.get("block_io_mb", 0.0)

        # Per-container breakdown
        result.per_container_stats = final_stats.get("per_container", {})

        # Disk usage
        result.disk_mb = get_disk_usage_mb(scenario["containers"])

        result.success = True
        print(f"Scenario {scenario_id} completed successfully")

        # Print summary
        print(f"\n--- Resource Summary ---")
        print(f"  RAM: {result.ram_initial_mb:.0f}MB initial -> {result.ram_after_load_mb:.0f}MB loaded -> {result.ram_peak_mb:.0f}MB peak")
        print(f"  CPU: {result.cpu_avg_percent:.1f}% avg, {result.cpu_peak_percent:.1f}% peak")
        print(f"  Net I/O: {result.net_io_mb:.1f}MB")
        print(f"  Block I/O: {result.block_io_read_mb:.1f}MB")
        print(f"  Disk: {result.disk_mb:.0f}MB")
        print(f"  Data: {result.nodes_count:,} nodes, {result.edges_count:,} edges, ~{result.timeseries_count:,} ts samples")

    except Exception as e:
        result.error = str(e)
        print(f"Error in scenario {scenario_id}: {e}")

    finally:
        # Always cleanup
        stop_all_containers()

    return result


def save_result(result: BenchmarkResult, results_dir: Path) -> Path:
    """Save individual result to JSON file."""
    results_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{result.scenario}_{result.profile}_{result.timestamp.replace(':', '-')}.json"
    filepath = results_dir / filename

    with filepath.open("w") as f:
        json.dump(asdict(result), f, indent=2)

    print(f"Result saved: {filepath}")
    return filepath


def save_suite(suite: BenchmarkSuite, results_dir: Path) -> Path:
    """Save complete suite results."""
    results_dir.mkdir(parents=True, exist_ok=True)
    filename = f"suite_{suite.profile}_{suite.started_at.replace(':', '-')}.json"
    filepath = results_dir / filename

    with filepath.open("w") as f:
        json.dump(suite.to_dict(), f, indent=2)

    print(f"Suite saved: {filepath}")
    return filepath


def generate_synthesis(suite: BenchmarkSuite) -> str:
    """Generate detailed synthesis report with resource metrics."""
    lines = [
        "=" * 80,
        "BENCHMARK SYNTHESIS - DETAILED RESOURCE METRICS",
        "=" * 80,
        f"Profile: {suite.profile}",
        f"Started: {suite.started_at}",
        f"Completed: {suite.completed_at}",
        f"Scenarios: {', '.join(suite.scenarios_requested)}",
        "",
    ]

    # Summary table header
    lines.extend([
        "RESOURCE COMPARISON TABLE:",
        "-" * 80,
        f"{'Scenario':<10} {'Ingestion':>10} {'RAM Init':>10} {'RAM Load':>10} {'RAM Peak':>10} {'CPU Avg':>8} {'Disk':>8}",
        "-" * 80,
    ])

    for result in suite.results:
        if result.success:
            lines.append(
                f"{result.scenario:<10} {result.ingestion_time_s:>9.1f}s {result.ram_initial_mb:>9.0f}MB "
                f"{result.ram_after_load_mb:>9.0f}MB {result.ram_peak_mb:>9.0f}MB "
                f"{result.cpu_avg_percent:>7.1f}% {result.disk_mb:>7.0f}MB"
            )
        else:
            lines.append(f"{result.scenario:<10} FAILED: {result.error}")

    lines.extend(["", "-" * 80, ""])

    # Detailed results per scenario
    lines.extend(["DETAILED RESULTS:", "-" * 80])

    for result in suite.results:
        status = "OK" if result.success else f"FAILED: {result.error}"
        lines.append(f"\n  {result.scenario} - {SCENARIOS[result.scenario]['name']}: {status}")

        if result.success:
            lines.extend([
                f"    Data loaded: {result.nodes_count:,} nodes, {result.edges_count:,} edges, ~{result.timeseries_count:,} ts samples",
                f"    Ingestion time: {result.ingestion_time_s:.2f}s",
                f"    Memory:",
                f"      - Initial: {result.ram_initial_mb:.0f}MB",
                f"      - After load: {result.ram_after_load_mb:.0f}MB",
                f"      - Peak: {result.ram_peak_mb:.0f}MB",
                f"    CPU: {result.cpu_avg_percent:.1f}% avg, {result.cpu_peak_percent:.1f}% peak",
                f"    I/O: Net {result.net_io_mb:.1f}MB, Block {result.block_io_read_mb:.1f}MB",
                f"    Disk usage: {result.disk_mb:.0f}MB",
            ])

            # Per-container breakdown
            if result.per_container_stats:
                lines.append("    Per-container:")
                for container, stats in result.per_container_stats.items():
                    lines.append(f"      - {container}: {stats.get('ram_mb', 0):.0f}MB RAM, {stats.get('cpu_percent', 0):.1f}% CPU")

            # Query summary
            if result.query_results:
                lines.append("    Queries:")
                total_time = 0
                for qid, qdata in sorted(result.query_results.items()):
                    if qdata.get("success", False):
                        time_ms = qdata.get("median_ms", qdata.get("p50_ms", 0))
                        rows = qdata.get("rows", 0)
                        total_time += time_ms
                        lines.append(f"      {qid}: {time_ms:.1f}ms ({rows} rows)")
                    else:
                        lines.append(f"      {qid}: ERROR - {qdata.get('error', 'unknown')}")
                lines.append(f"    Total query time: {total_time:.1f}ms")

    lines.extend(["", "=" * 80])

    return "\n".join(lines)


def get_available_ram_mb() -> float:
    """Get available RAM on the system."""
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return float(line.split()[1]) / 1024  # KB to MB
    except Exception:
        pass
    return 16000  # Default assumption


def interactive_setup() -> tuple:
    """Interactive setup for benchmark configuration."""
    print("\n" + "=" * 60)
    print("BASETYPE BENCHMARK - Interactive Setup")
    print("=" * 60)

    # 1. Check/configure author
    print("\n[1/5] Author Configuration")
    author = input(f"Author name [{DEFAULT_AUTHOR}]: ").strip() or DEFAULT_AUTHOR

    if author == DEFAULT_AUTHOR:
        orcid = DEFAULT_ORCID
        print(f"Using ORCID: {orcid}")
    else:
        orcid = input("ORCID (leave empty if none): ").strip()

    # 2. Select profile
    print("\n[2/5] Dataset Profile")
    print("Available scales:", ", ".join(SCALES))
    scale = input(f"Scale [small]: ").strip() or "small"
    if scale not in SCALES:
        print(f"Invalid scale, using 'small'")
        scale = "small"

    print("Available durations:", ", ".join(DURATIONS))
    duration = input(f"Duration [2d]: ").strip() or "2d"
    if duration not in DURATIONS:
        print(f"Invalid duration, using '2d'")
        duration = "2d"

    profile = f"{scale}-{duration}"

    # 3. Check dataset
    print(f"\n[3/5] Dataset Check: {profile}")
    if check_dataset_exists(profile):
        print(f"Dataset {profile} exists locally")
    else:
        print(f"Dataset {profile} not found locally")
        generate = input("Generate it now? [Y/n]: ").strip().lower()
        if generate != "n":
            if not generate_dataset(profile, author, orcid):
                print("Failed to generate dataset")
                sys.exit(1)

    # 4. Select scenarios
    print("\n[4/5] Scenario Selection")
    print("Available scenarios:")
    available_ram = get_available_ram_mb()
    ram_multiplier = SCALE_RAM_MULTIPLIER.get(scale, 1.0)

    for sid, sinfo in SCENARIOS.items():
        estimated_ram = sinfo["ram_estimate_mb"] * ram_multiplier
        status = "OK" if estimated_ram < available_ram * 0.8 else "WARNING: may exceed RAM"
        print(f"  {sid}: {sinfo['name']}")
        print(f"      Structure: {sinfo['structure']}, Timeseries: {sinfo['timeseries']}")
        print(f"      Estimated RAM: {estimated_ram:.0f}MB ({status})")

    print("\nEnter scenarios to test (comma-separated, or 'all'):")
    scenarios_input = input(f"Scenarios [P1]: ").strip() or "P1"

    if scenarios_input.lower() == "all":
        scenarios = list(SCENARIOS.keys())
    else:
        scenarios = [s.strip().upper() for s in scenarios_input.split(",")]
        scenarios = [s for s in scenarios if s in SCENARIOS]

    if not scenarios:
        print("No valid scenarios selected")
        sys.exit(1)

    # 5. Confirmation
    print("\n[5/5] Confirmation")
    print(f"  Profile: {profile}")
    print(f"  Scenarios: {', '.join(scenarios)}")
    print(f"  Author: {author}")

    confirm = input("\nProceed? [Y/n]: ").strip().lower()
    if confirm == "n":
        print("Aborted")
        sys.exit(0)

    return profile, scenarios, author, orcid


def run_benchmark_suite(profile: str, scenarios: List[str]) -> BenchmarkSuite:
    """Run complete benchmark suite."""
    suite = BenchmarkSuite(
        started_at=datetime.now().isoformat(),
        profile=profile,
        scenarios_requested=scenarios,
    )

    # Ensure JSON export exists for graph databases
    if any(s in ["M1", "M2", "O1", "O2"] for s in scenarios):
        export_json_format(profile)

    # Run each scenario
    for scenario_id in scenarios:
        result = run_scenario(scenario_id, profile)
        suite.results.append(result)

        # Save individual result
        save_result(result, RESULTS_DIR / profile)

    suite.completed_at = datetime.now().isoformat()

    # Save suite and generate synthesis
    save_suite(suite, RESULTS_DIR)
    synthesis = generate_synthesis(suite)
    print("\n" + synthesis)

    # Save synthesis
    synthesis_path = RESULTS_DIR / f"synthesis_{profile}_{suite.started_at.replace(':', '-')}.txt"
    synthesis_path.write_text(synthesis)
    print(f"\nSynthesis saved: {synthesis_path}")

    return suite


def main():
    parser = argparse.ArgumentParser(
        description="BaseType Benchmark Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python -m scripts.run_benchmark --interactive

  Direct mode:
    python -m scripts.run_benchmark --profile small-2d --scenarios P1,P2

  Full matrix (all combinations):
    python -m scripts.run_benchmark --full-matrix
        """
    )

    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive setup mode")
    parser.add_argument("--profile", type=str,
                        help="Dataset profile (e.g., small-2d, medium-1m)")
    parser.add_argument("--scenarios", type=str,
                        help="Comma-separated scenario IDs (P1,P2,M1,M2,O1,O2)")
    parser.add_argument("--full-matrix", action="store_true",
                        help="Run all 72 combinations (6 scenarios x 3 scales x 4 durations)")
    parser.add_argument("--generate-only", type=str,
                        help="Only generate dataset for given profile")

    args = parser.parse_args()

    if args.generate_only:
        generate_dataset(args.generate_only, DEFAULT_AUTHOR, DEFAULT_ORCID)
        return

    if args.full_matrix:
        print("Full matrix mode: 72 combinations")
        print("This should be run on a dedicated server (B3-256)")
        confirm = input("Continue? [y/N]: ").strip().lower()
        if confirm != "y":
            return

        for scale in SCALES:
            for duration in DURATIONS[1:]:  # Skip 2d for full matrix
                profile = f"{scale}-{duration}"
                if not check_dataset_exists(profile):
                    generate_dataset(profile, DEFAULT_AUTHOR, DEFAULT_ORCID)
                run_benchmark_suite(profile, list(SCENARIOS.keys()))
        return

    if args.interactive or (not args.profile and not args.scenarios):
        profile, scenarios, author, orcid = interactive_setup()
    else:
        if not args.profile:
            print("Error: --profile required in non-interactive mode")
            sys.exit(1)

        profile = args.profile
        scenarios = args.scenarios.split(",") if args.scenarios else ["P1"]
        scenarios = [s.strip().upper() for s in scenarios]

    run_benchmark_suite(profile, scenarios)


if __name__ == "__main__":
    main()
