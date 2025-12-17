"""Benchmark executor - Execute queries against database engines.

This module handles:
1. Loading data into databases
2. Executing benchmark queries (Q1-Q8)
3. Measuring latencies with warmup
4. Computing statistics (p50, p95, min, max)
"""
from __future__ import annotations

import time
import statistics
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import csv

# Database clients
import psycopg2
import requests


# =============================================================================
# CONFIGURATION
# =============================================================================

# Benchmark protocol
N_WARMUP = 3      # Warmup runs (not counted)
N_RUNS = 10       # Measured runs per query

# Database connection defaults
POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "benchmark",
    "password": "benchmark",
    "database": "benchmark"
}

MEMGRAPH_CONFIG = {
    "host": "localhost",
    "port": 7687
}

OXIGRAPH_CONFIG = {
    "host": "localhost",
    "port": 7878
}

# Queries to run per scenario
QUERIES_BY_SCENARIO = {
    "P1": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"],  # All SQL queries
    "P2": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"],  # All SQL queries (JSONB)
    "M1": ["Q1", "Q2", "Q3", "Q4", "Q5"],  # Graph queries only (no timeseries)
    "M2": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q8"],  # Graph + hybrid
    "O1": ["Q1", "Q2", "Q3", "Q4", "Q5"],  # SPARQL queries only
    "O2": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q8"],  # SPARQL + hybrid
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class QueryResult:
    """Result of a single query execution."""
    query_id: str
    latency_ms: float
    row_count: int
    success: bool
    error: Optional[str] = None


@dataclass
class QueryStats:
    """Statistics for a query across multiple runs."""
    query_id: str
    latencies_ms: List[float]
    row_counts: List[int]
    success_count: int
    error_count: int

    @property
    def p50(self) -> float:
        """Median latency in ms."""
        if not self.latencies_ms:
            return 0.0
        return statistics.median(self.latencies_ms)

    @property
    def p95(self) -> float:
        """95th percentile latency in ms."""
        if not self.latencies_ms:
            return 0.0
        sorted_latencies = sorted(self.latencies_ms)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]

    @property
    def min_latency(self) -> float:
        return min(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def max_latency(self) -> float:
        return max(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def avg_latency(self) -> float:
        return statistics.mean(self.latencies_ms) if self.latencies_ms else 0.0


@dataclass
class BenchmarkResult:
    """Complete benchmark result for a scenario/RAM combination."""
    scenario: str
    ram_gb: int
    dataset: str
    query_stats: Dict[str, QueryStats] = field(default_factory=dict)
    load_time_s: float = 0.0
    total_time_s: float = 0.0
    status: str = "pending"  # pending, completed, oom, error
    error: Optional[str] = None

    @property
    def overall_p50(self) -> float:
        """Average p50 across all queries."""
        p50s = [qs.p50 for qs in self.query_stats.values() if qs.latencies_ms]
        return statistics.mean(p50s) if p50s else 0.0

    @property
    def overall_p95(self) -> float:
        """Average p95 across all queries."""
        p95s = [qs.p95 for qs in self.query_stats.values() if qs.latencies_ms]
        return statistics.mean(p95s) if p95s else 0.0

    @property
    def worst_p95(self) -> Tuple[str, float]:
        """Query with worst p95."""
        worst = ("", 0.0)
        for qid, qs in self.query_stats.items():
            if qs.p95 > worst[1]:
                worst = (qid, qs.p95)
        return worst


# =============================================================================
# DATABASE LOADERS
# =============================================================================

class PostgresLoader:
    """Load data into PostgreSQL/TimescaleDB."""

    def __init__(self, config: dict = None):
        self.config = config or POSTGRES_CONFIG
        self.conn = None

    def connect(self) -> bool:
        """Connect to PostgreSQL."""
        try:
            self.conn = psycopg2.connect(**self.config)
            return True
        except Exception as e:
            print(f"[ERROR] PostgreSQL connection failed: {e}")
            return False

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def create_schema(self, schema_type: str = "relational"):
        """Create database schema.

        Args:
            schema_type: 'relational' for P1, 'jsonb' for P2
        """
        if not self.conn:
            return False

        cur = self.conn.cursor()

        # Drop existing tables
        cur.execute("DROP TABLE IF EXISTS timeseries CASCADE")
        cur.execute("DROP TABLE IF EXISTS edges CASCADE")
        cur.execute("DROP TABLE IF EXISTS nodes CASCADE")

        if schema_type == "relational":
            # P1: Relational schema (no FK constraints - data may have refs to external IDs)
            cur.execute("""
                CREATE TABLE nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    name TEXT,
                    building_id INTEGER,
                    properties JSONB DEFAULT '{}'
                )
            """)
            cur.execute("""
                CREATE TABLE edges (
                    id SERIAL PRIMARY KEY,
                    src_id TEXT NOT NULL,
                    dst_id TEXT NOT NULL,
                    rel_type TEXT NOT NULL
                )
            """)
        else:
            # P2: JSONB schema
            cur.execute("""
                CREATE TABLE nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    name TEXT,
                    building_id INTEGER,
                    properties JSONB DEFAULT '{}'
                )
            """)
            cur.execute("""
                CREATE TABLE edges (
                    id SERIAL PRIMARY KEY,
                    src_id TEXT NOT NULL,
                    dst_id TEXT NOT NULL,
                    rel_type TEXT NOT NULL,
                    properties JSONB DEFAULT '{}'
                )
            """)

        # Timeseries table (TimescaleDB hypertable)
        cur.execute("""
            CREATE TABLE timeseries (
                time TIMESTAMPTZ NOT NULL,
                point_id TEXT NOT NULL,
                value DOUBLE PRECISION
            )
        """)

        # Try to create hypertable (if TimescaleDB extension exists)
        try:
            cur.execute("SELECT create_hypertable('timeseries', 'time', if_not_exists => TRUE)")
        except:
            pass  # TimescaleDB not installed, use regular table

        # Create indexes
        cur.execute("CREATE INDEX idx_nodes_type ON nodes(type)")
        cur.execute("CREATE INDEX idx_nodes_building ON nodes(building_id)")
        cur.execute("CREATE INDEX idx_edges_src ON edges(src_id)")
        cur.execute("CREATE INDEX idx_edges_dst ON edges(dst_id)")
        cur.execute("CREATE INDEX idx_edges_rel ON edges(rel_type)")
        cur.execute("CREATE INDEX idx_timeseries_point ON timeseries(point_id, time)")

        self.conn.commit()
        cur.close()
        return True

    def load_data(self, export_dir: Path) -> Tuple[bool, float]:
        """Load CSV data into PostgreSQL.

        Returns:
            Tuple of (success, load_time_seconds)
        """
        if not self.conn:
            return False, 0.0

        start = time.time()
        cur = self.conn.cursor()

        try:
            # Load nodes
            nodes_file = export_dir / "nodes.csv"
            if nodes_file.exists():
                with open(nodes_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cur.execute(
                            "INSERT INTO nodes (id, type, name, building_id, properties) VALUES (%s, %s, %s, %s, %s)",
                            (row['id'], row['type'], row.get('name'),
                             int(row['building_id']) if row.get('building_id') else None,
                             row.get('properties', '{}'))
                        )

            # Load edges
            edges_file = export_dir / "edges.csv"
            if edges_file.exists():
                with open(edges_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cur.execute(
                            "INSERT INTO edges (src_id, dst_id, rel_type) VALUES (%s, %s, %s)",
                            (row['src_id'], row['dst_id'], row['rel_type'])
                        )

            # Load timeseries
            ts_file = export_dir / "timeseries.csv"
            if ts_file.exists():
                with open(ts_file, 'r', encoding='utf-8') as f:
                    # Use COPY for bulk load
                    cur.copy_expert(
                        "COPY timeseries (time, point_id, value) FROM STDIN WITH CSV HEADER",
                        f
                    )

            self.conn.commit()
            load_time = time.time() - start
            cur.close()
            return True, load_time

        except Exception as e:
            self.conn.rollback()
            cur.close()
            print(f"[ERROR] Data loading failed: {e}")
            return False, time.time() - start

    def execute_query(self, query: str) -> QueryResult:
        """Execute a query and measure latency."""
        if not self.conn:
            return QueryResult("", 0, 0, False, "Not connected")

        cur = self.conn.cursor()
        start = time.time()

        try:
            cur.execute(query)
            rows = cur.fetchall()
            latency_ms = (time.time() - start) * 1000
            cur.close()
            return QueryResult("", latency_ms, len(rows), True)
        except Exception as e:
            cur.close()
            return QueryResult("", 0, 0, False, str(e))


class MemgraphLoader:
    """Load data into Memgraph."""

    def __init__(self, config: dict = None):
        self.config = config or MEMGRAPH_CONFIG
        self.driver = None

    def connect(self, max_retries: int = 10, retry_delay: float = 3.0) -> bool:
        """Connect to Memgraph via Bolt protocol with retry logic."""
        from neo4j import GraphDatabase
        uri = f"bolt://{self.config['host']}:{self.config['port']}"

        for attempt in range(max_retries):
            try:
                self.driver = GraphDatabase.driver(uri)
                # Test connection
                with self.driver.session() as session:
                    session.run("RETURN 1")
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[INFO] Memgraph not ready (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"[ERROR] Memgraph connection failed after {max_retries} attempts: {e}")
                    return False
        return False

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None

    def clear_database(self):
        """Clear all data from Memgraph."""
        if not self.driver:
            return
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def load_data(self, export_dir: Path) -> Tuple[bool, float]:
        """Load CSV data into Memgraph."""
        if not self.driver:
            return False, 0.0

        start = time.time()

        try:
            with self.driver.session() as session:
                # Load nodes
                nodes_file = export_dir / "nodes.csv"
                if nodes_file.exists():
                    with open(nodes_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            props = {
                                'id': row['id'],
                                'type': row['type'],
                                'name': row.get('name', ''),
                                'building_id': int(row['building_id']) if row.get('building_id') else 0
                            }
                            session.run(
                                "CREATE (n:Node {id: $id, type: $type, name: $name, building_id: $building_id})",
                                props
                            )

                # Create index on id
                session.run("CREATE INDEX ON :Node(id)")
                session.run("CREATE INDEX ON :Node(type)")

                # Load edges
                edges_file = export_dir / "edges.csv"
                if edges_file.exists():
                    with open(edges_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            session.run(
                                f"MATCH (a:Node {{id: $src}}), (b:Node {{id: $dst}}) "
                                f"CREATE (a)-[:{row['rel_type']}]->(b)",
                                {"src": row['src_id'], "dst": row['dst_id']}
                            )

            load_time = time.time() - start
            return True, load_time

        except Exception as e:
            print(f"[ERROR] Memgraph loading failed: {e}")
            return False, time.time() - start

    def execute_query(self, query: str) -> QueryResult:
        """Execute a Cypher query and measure latency."""
        if not self.driver:
            return QueryResult("", 0, 0, False, "Not connected")

        start = time.time()

        try:
            with self.driver.session() as session:
                result = session.run(query)
                records = list(result)
                latency_ms = (time.time() - start) * 1000
                return QueryResult("", latency_ms, len(records), True)
        except Exception as e:
            return QueryResult("", 0, 0, False, str(e))


class OxigraphLoader:
    """Load data into Oxigraph."""

    def __init__(self, config: dict = None):
        self.config = config or OXIGRAPH_CONFIG
        self.base_url = f"http://{self.config['host']}:{self.config['port']}"

    def connect(self, max_retries: int = 10, retry_delay: float = 3.0) -> bool:
        """Test connection to Oxigraph with retry logic."""
        for attempt in range(max_retries):
            try:
                resp = requests.get(f"{self.base_url}/query", params={"query": "SELECT * WHERE { ?s ?p ?o } LIMIT 1"}, timeout=10)
                if resp.status_code in [200, 204]:
                    return True
            except Exception as e:
                pass

            if attempt < max_retries - 1:
                print(f"[INFO] Oxigraph not ready (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"[ERROR] Oxigraph connection failed after {max_retries} attempts")
                return False
        return False

    def close(self):
        pass  # HTTP, no persistent connection

    def clear_database(self):
        """Clear all data from Oxigraph."""
        try:
            requests.post(f"{self.base_url}/update", data="DELETE WHERE { ?s ?p ?o }")
        except:
            pass

    def load_data(self, export_dir: Path) -> Tuple[bool, float]:
        """Load data into Oxigraph from CSV files by converting to N-Triples."""
        start = time.time()

        try:
            # First try JSON-LD if available
            jsonld_file = export_dir / "graph.jsonld"
            if not jsonld_file.exists():
                jsonld_file = export_dir / "rdf" / "graph.jsonld"

            if jsonld_file.exists():
                with open(jsonld_file, 'r', encoding='utf-8') as f:
                    data = f.read()
                resp = requests.post(
                    f"{self.base_url}/store",
                    data=data,
                    headers={"Content-Type": "application/ld+json"},
                    timeout=300
                )
                if resp.status_code in [200, 204]:
                    return True, time.time() - start

            # Otherwise, generate N-Triples from CSV
            ntriples = self._csv_to_ntriples(export_dir)
            if not ntriples:
                print(f"[WARN] No data to load for Oxigraph")
                return True, time.time() - start

            # Load N-Triples into Oxigraph
            resp = requests.post(
                f"{self.base_url}/store",
                data=ntriples.encode('utf-8'),
                headers={"Content-Type": "application/n-triples"},
                timeout=300
            )

            if resp.status_code not in [200, 204]:
                print(f"[ERROR] Oxigraph load failed: HTTP {resp.status_code}")
                return False, time.time() - start

            return True, time.time() - start

        except Exception as e:
            print(f"[ERROR] Oxigraph loading failed: {e}")
            return False, time.time() - start

    def _csv_to_ntriples(self, export_dir: Path) -> str:
        """Convert CSV files to N-Triples format for Oxigraph."""
        lines = []
        base = "http://example.org/id/"
        type_base = "http://example.org/type/"
        pred_base = "http://example.org/"

        # Load nodes
        nodes_file = export_dir / "nodes.csv"
        if nodes_file.exists():
            with open(nodes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    node_uri = f"<{base}{row['id']}>"
                    node_type = row.get('type', 'Node')

                    # rdf:type
                    lines.append(f"{node_uri} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <{type_base}{node_type}> .")

                    # Properties
                    if row.get('name'):
                        name_escaped = row['name'].replace('\\', '\\\\').replace('"', '\\"')
                        lines.append(f'{node_uri} <{pred_base}name> "{name_escaped}" .')

                    if row.get('building_id'):
                        lines.append(f'{node_uri} <{pred_base}building_id> "{row["building_id"]}" .')

        # Load edges
        edges_file = export_dir / "edges.csv"
        if edges_file.exists():
            with open(edges_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    src_uri = f"<{base}{row['src_id']}>"
                    dst_uri = f"<{base}{row['dst_id']}>"
                    rel_type = row.get('rel_type', 'RELATED_TO')
                    lines.append(f"{src_uri} <{pred_base}{rel_type}> {dst_uri} .")

        return "\n".join(lines)

    def execute_query(self, query: str) -> QueryResult:
        """Execute a SPARQL query and measure latency."""
        start = time.time()

        try:
            resp = requests.get(
                f"{self.base_url}/query",
                params={"query": query},
                headers={"Accept": "application/sparql-results+json"}
            )
            latency_ms = (time.time() - start) * 1000

            if resp.status_code == 200:
                results = resp.json()
                row_count = len(results.get("results", {}).get("bindings", []))
                return QueryResult("", latency_ms, row_count, True)
            else:
                return QueryResult("", latency_ms, 0, False, f"HTTP {resp.status_code}")

        except Exception as e:
            return QueryResult("", 0, 0, False, str(e))


# =============================================================================
# BENCHMARK EXECUTOR
# =============================================================================

class BenchmarkExecutor:
    """Execute benchmarks against database engines."""

    def __init__(self, queries_dir: Path = None):
        self.queries_dir = queries_dir or Path(__file__).parent / "queries"
        self.queries_cache: Dict[str, Dict[str, str]] = {}  # {format: {query_id: query_text}}
        self._load_queries()

    def _load_queries(self):
        """Load all query files into cache."""
        for fmt in ["sql", "cypher", "sparql"]:
            self.queries_cache[fmt] = {}
            fmt_dir = self.queries_dir / fmt
            if fmt_dir.exists():
                for qfile in fmt_dir.glob("Q*.sql" if fmt == "sql" else f"Q*.{fmt}"):
                    query_id = qfile.stem.split("_")[0]  # Q1, Q2, etc.
                    with open(qfile, 'r', encoding='utf-8') as f:
                        self.queries_cache[fmt][query_id] = f.read()

    def get_loader(self, scenario: str):
        """Get appropriate loader for scenario."""
        if scenario in ["P1", "P2"]:
            return PostgresLoader()
        elif scenario in ["M1", "M2"]:
            return MemgraphLoader()
        elif scenario in ["O1", "O2"]:
            return OxigraphLoader()
        else:
            raise ValueError(f"Unknown scenario: {scenario}")

    def get_query_format(self, scenario: str) -> str:
        """Get query format for scenario."""
        if scenario in ["P1", "P2"]:
            return "sql"
        elif scenario in ["M1", "M2"]:
            return "cypher"
        elif scenario in ["O1", "O2"]:
            return "sparql"
        else:
            raise ValueError(f"Unknown scenario: {scenario}")

    def run_benchmark(self, scenario: str, dataset_dir: Path,
                      ram_gb: int, callback=None) -> BenchmarkResult:
        """Run complete benchmark for a scenario.

        Args:
            scenario: P1, P2, M1, M2, O1, O2
            dataset_dir: Path to exported dataset
            ram_gb: RAM allocation (for reference)
            callback: Optional callback(phase, message) for progress

        Returns:
            BenchmarkResult with all measurements
        """
        result = BenchmarkResult(
            scenario=scenario,
            ram_gb=ram_gb,
            dataset=dataset_dir.name
        )

        start_total = time.time()

        # Get loader and connect
        loader = self.get_loader(scenario)

        if callback:
            callback("connect", f"Connecting to {scenario}...")

        if not loader.connect():
            result.status = "error"
            result.error = "Connection failed"
            return result

        try:
            # Create schema (for PostgreSQL)
            if scenario in ["P1", "P2"]:
                schema_type = "relational" if scenario == "P1" else "jsonb"
                if callback:
                    callback("schema", f"Creating {schema_type} schema...")
                loader.create_schema(schema_type)
            elif hasattr(loader, 'clear_database'):
                if callback:
                    callback("clear", "Clearing database...")
                loader.clear_database()

            # Load data
            if callback:
                callback("load", "Loading data...")

            success, load_time = loader.load_data(dataset_dir)
            result.load_time_s = load_time

            if not success:
                result.status = "error"
                result.error = "Data loading failed"
                return result

            if callback:
                callback("load_done", f"Data loaded in {load_time:.1f}s")

            # Execute queries
            query_format = self.get_query_format(scenario)
            queries_to_run = QUERIES_BY_SCENARIO.get(scenario, [])

            for query_id in queries_to_run:
                if query_id not in self.queries_cache.get(query_format, {}):
                    continue

                query_text = self.queries_cache[query_format][query_id]

                if callback:
                    callback("query", f"Running {query_id}...")

                # Warmup
                for _ in range(N_WARMUP):
                    loader.execute_query(query_text)

                # Measured runs
                latencies = []
                row_counts = []
                errors = 0

                for run in range(N_RUNS):
                    qr = loader.execute_query(query_text)
                    if qr.success:
                        latencies.append(qr.latency_ms)
                        row_counts.append(qr.row_count)
                    else:
                        errors += 1

                result.query_stats[query_id] = QueryStats(
                    query_id=query_id,
                    latencies_ms=latencies,
                    row_counts=row_counts,
                    success_count=len(latencies),
                    error_count=errors
                )

                if callback and latencies:
                    stats = result.query_stats[query_id]
                    callback("query_done", f"{query_id}: p50={stats.p50:.1f}ms, p95={stats.p95:.1f}ms")

            result.status = "completed"

        except MemoryError:
            result.status = "oom"
            result.error = "Out of memory"
        except Exception as e:
            if "out of memory" in str(e).lower() or "oom" in str(e).lower():
                result.status = "oom"
            else:
                result.status = "error"
            result.error = str(e)
        finally:
            loader.close()
            result.total_time_s = time.time() - start_total

        return result


# =============================================================================
# UTILITIES
# =============================================================================

def format_result_table(results: List[BenchmarkResult]) -> str:
    """Format benchmark results as a table."""
    lines = []

    # Header
    header = (
        f"{'Scenario':<8} | {'RAM':<6} | {'Status':<8} | "
        f"{'Load(s)':<8} | {'p50(ms)':<10} | {'p95(ms)':<10} | "
        f"{'Worst Query':<12}"
    )
    sep = "-" * len(header)

    lines.append(sep)
    lines.append(header)
    lines.append(sep)

    for r in results:
        if r.status == "completed":
            worst_q, worst_p95 = r.worst_p95
            lines.append(
                f"{r.scenario:<8} | {r.ram_gb:<6} | {'OK':<8} | "
                f"{r.load_time_s:<8.1f} | {r.overall_p50:<10.1f} | {r.overall_p95:<10.1f} | "
                f"{worst_q}={worst_p95:.0f}ms"
            )
        else:
            lines.append(
                f"{r.scenario:<8} | {r.ram_gb:<6} | {r.status:<8} | "
                f"{'-':<8} | {'-':<10} | {'-':<10} | "
                f"{r.error or '-'}"
            )

    lines.append(sep)
    return "\n".join(lines)


def format_detailed_results(result: BenchmarkResult) -> str:
    """Format detailed results for a single benchmark run."""
    lines = [
        f"\n{'='*60}",
        f"  {result.scenario} @ {result.ram_gb}GB RAM",
        f"{'='*60}",
        f"  Status: {result.status}",
        f"  Load time: {result.load_time_s:.1f}s",
        f"  Total time: {result.total_time_s:.1f}s",
        "",
        f"  {'Query':<6} | {'p50(ms)':<10} | {'p95(ms)':<10} | {'min':<10} | {'max':<10} | {'rows':<8}",
        f"  {'-'*70}"
    ]

    for qid, qs in sorted(result.query_stats.items()):
        if qs.latencies_ms:
            avg_rows = int(statistics.mean(qs.row_counts)) if qs.row_counts else 0
            lines.append(
                f"  {qid:<6} | {qs.p50:<10.1f} | {qs.p95:<10.1f} | "
                f"{qs.min_latency:<10.1f} | {qs.max_latency:<10.1f} | {avg_rows:<8}"
            )
        else:
            lines.append(f"  {qid:<6} | {'FAILED':<10} | {'-':<10} | {'-':<10} | {'-':<10} | {'-':<8}")

    lines.append(f"  {'-'*70}")
    lines.append(f"  Overall p50: {result.overall_p50:.1f}ms")
    lines.append(f"  Overall p95: {result.overall_p95:.1f}ms")

    return "\n".join(lines)
