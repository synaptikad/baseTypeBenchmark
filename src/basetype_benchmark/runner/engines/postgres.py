"""PostgreSQL engine for P1 (relational) and P2 (JSONB) scenarios."""

import csv
import os
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import execute_batch


def _read_env_file(path: Path) -> Dict[str, str]:
    """Read a simple KEY=VALUE env file."""
    data: Dict[str, str] = {}
    try:
        if not path.exists():
            return data
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k:
                data[k] = v
    except Exception:
        return {}
    return data


def _resolve_pg_config_defaults(
    host: str, port: int, user: str, password: str, database: str
) -> Dict[str, object]:
    """Resolve connection defaults from env vars or docker/.env."""
    # Find repo root: postgres.py -> engines(0) -> runner(1) -> basetype_benchmark(2) -> src(3) -> repo(4)
    repo_root = Path(__file__).resolve().parents[4]
    env_file_vars: Dict[str, str] = {}

    # Read env files (docker/.env takes precedence, so read it last)
    for candidate in (repo_root / ".env", repo_root / "docker" / ".env"):
        file_vars = _read_env_file(candidate)
        if file_vars:
            env_file_vars.update(file_vars)

    def _get(key: str, default: str) -> str:
        return os.getenv(key) or env_file_vars.get(key) or default

    return {
        "host": _get("POSTGRES_HOST", host),
        "port": int(_get("POSTGRES_PORT", str(port))),
        "user": _get("POSTGRES_USER", user),
        "password": _get("POSTGRES_PASSWORD", password),
        "database": _get("POSTGRES_DB", database),
    }


def get_connection(
    host: str = "localhost",
    port: int = 5432,
    user: str = "postgres",
    password: str = "benchmark",
    database: str = "benchmark",
    max_retries: int = 30,
    retry_delay: float = 2.0,
):
    """Create PostgreSQL connection with retry logic.

    Reads credentials from environment variables or docker/.env file.
    """
    # Resolve from env files
    cfg = _resolve_pg_config_defaults(host, port, user, password, database)
    host = str(cfg["host"])
    port = int(cfg["port"])  # type: ignore
    user = str(cfg["user"])
    password = str(cfg["password"])
    database = str(cfg["database"])

    last_error = None
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=host, port=port, user=user,
                password=password, database=database
            )
            return conn
        except psycopg2.OperationalError as e:
            last_error = e
            # Check for non-transient errors
            msg = str(e).lower()
            if any(s in msg for s in ("password authentication failed", "role", "does not exist")):
                print(f"  [ERROR] PostgreSQL auth failed: {e}")
                raise e
            if attempt < max_retries - 1:
                print(f"  [WAIT] PostgreSQL not ready ({attempt + 1}/{max_retries})...")
                time.sleep(retry_delay)

    raise last_error


class PostgresEngine:
    """PostgreSQL engine for P1/P2 benchmarks."""

    def __init__(self, scenario: str = "P1"):
        """Initialize engine.

        Args:
            scenario: P1 (relational) or P2 (JSONB)
        """
        self.scenario = scenario.upper()
        self.conn = None

    def connect(self) -> None:
        """Establish database connection."""
        self.conn = get_connection()

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def clear(self) -> None:
        """Clear all tables."""
        with self.conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS timeseries CASCADE")
            cur.execute("DROP TABLE IF EXISTS edges CASCADE")
            cur.execute("DROP TABLE IF EXISTS nodes CASCADE")
        self.conn.commit()

    def create_schema(self) -> None:
        """Create schema based on scenario."""
        with self.conn.cursor() as cur:
            if self.scenario == "P1":
                # Relational schema with explicit columns
                cur.execute("""
                    CREATE TABLE nodes (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        name TEXT,
                        domain TEXT,
                        equipment_type TEXT,
                        space_type TEXT,
                        building_id TEXT,
                        floor_id TEXT,
                        space_id TEXT,
                        quantity TEXT,
                        properties JSONB DEFAULT '{}'
                    )
                """)
            else:  # P2
                # JSONB schema with minimal extracted columns
                cur.execute("""
                    CREATE TABLE nodes (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        name TEXT,
                        building_id TEXT,
                        properties JSONB DEFAULT '{}'
                    )
                """)

            # Edges table (same for both)
            cur.execute("""
                CREATE TABLE edges (
                    src_id TEXT NOT NULL,
                    dst_id TEXT NOT NULL,
                    rel_type TEXT NOT NULL,
                    PRIMARY KEY (src_id, dst_id, rel_type)
                )
            """)

            # Timeseries table
            cur.execute("""
                CREATE TABLE timeseries (
                    time TIMESTAMPTZ NOT NULL,
                    point_id TEXT NOT NULL,
                    value DOUBLE PRECISION
                )
            """)

            # Create hypertable
            try:
                cur.execute("""
                    SELECT create_hypertable('timeseries', 'time', if_not_exists => TRUE)
                """)
            except Exception:
                pass

            # Indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_building ON nodes(building_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, rel_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, rel_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ts_point_time ON timeseries(point_id, time DESC)")

        self.conn.commit()

    def load_nodes(self, nodes_file: Path, batch_size: int = 1000) -> int:
        """Load nodes from CSV."""
        total = 0
        t0 = time.time()

        with open(nodes_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            batch = []

            for row in reader:
                if self.scenario == "P1":
                    batch.append((
                        row["id"], row["type"], row.get("name", ""),
                        row.get("domain", ""), row.get("equipment_type", ""),
                        row.get("space_type", ""), row.get("building_id", ""),
                        row.get("floor_id", ""), row.get("space_id", ""),
                        row.get("quantity", ""), row.get("data", "{}")
                    ))
                else:  # P2
                    batch.append((
                        row["id"], row["type"], row.get("name", ""),
                        row.get("building_id", ""), row.get("properties", "{}")
                    ))

                if len(batch) >= batch_size:
                    self._insert_nodes_batch(batch)
                    total += len(batch)
                    batch.clear()
                    elapsed = time.time() - t0
                    print(f"\r  [LOAD] Nodes: {total:,} ({total/elapsed:.0f}/s)", end="", flush=True)

            if batch:
                self._insert_nodes_batch(batch)
                total += len(batch)

        print(f"\r  [LOAD] Nodes: {total:,} in {time.time() - t0:.1f}s          ")
        return total

    def _insert_nodes_batch(self, batch: List[Tuple]) -> None:
        """Insert batch of nodes."""
        with self.conn.cursor() as cur:
            if self.scenario == "P1":
                execute_batch(cur, """
                    INSERT INTO nodes (id, type, name, domain, equipment_type, space_type,
                                      building_id, floor_id, space_id, quantity, properties)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, batch)
            else:
                execute_batch(cur, """
                    INSERT INTO nodes (id, type, name, building_id, properties)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, batch)
        self.conn.commit()

    def load_edges(self, edges_file: Path, batch_size: int = 1000) -> int:
        """Load edges from CSV."""
        total = 0
        t0 = time.time()

        with open(edges_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            batch = []

            for row in reader:
                batch.append((row["src_id"], row["dst_id"], row["rel_type"]))

                if len(batch) >= batch_size:
                    with self.conn.cursor() as cur:
                        execute_batch(cur, """
                            INSERT INTO edges (src_id, dst_id, rel_type)
                            VALUES (%s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, batch)
                    self.conn.commit()
                    total += len(batch)
                    batch.clear()
                    elapsed = time.time() - t0
                    print(f"\r  [LOAD] Edges: {total:,} ({total/elapsed:.0f}/s)", end="", flush=True)

            if batch:
                with self.conn.cursor() as cur:
                    execute_batch(cur, """
                        INSERT INTO edges (src_id, dst_id, rel_type)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, batch)
                self.conn.commit()
                total += len(batch)

        print(f"\r  [LOAD] Edges: {total:,} in {time.time() - t0:.1f}s          ")
        return total

    def load_timeseries(self, ts_file: Path) -> int:
        """Load timeseries from CSV using COPY (client-side streaming)."""
        t0 = time.time()
        total_bytes = ts_file.stat().st_size

        with self.conn.cursor() as cur:
            with open(ts_file, "rb") as f:
                # Use COPY for fast bulk loading
                cur.copy_expert(
                    "COPY timeseries (point_id, time, value) FROM STDIN WITH CSV HEADER",
                    f
                )
        self.conn.commit()

        # Count rows
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM timeseries")
            total = cur.fetchone()[0]

        elapsed = time.time() - t0
        mb = total_bytes / (1024 * 1024)
        print(f"  [LOAD] Timeseries: {total:,} rows ({mb:.0f} MB) in {elapsed:.1f}s")
        return total

    def load_timeseries_server_copy(self, container_path: str) -> int:
        """Load timeseries using server-side COPY FROM (10x faster).

        Requires the CSV file to be mounted in the container at container_path.
        This bypasses network transfer entirely - PostgreSQL reads directly from disk.

        Args:
            container_path: Path to CSV file inside the container (e.g., /data/timeseries.csv)

        Returns:
            Total rows loaded
        """
        t0 = time.time()

        with self.conn.cursor() as cur:
            # Server-side COPY - PostgreSQL reads file directly (no network!)
            cur.execute(f"""
                COPY timeseries (point_id, time, value)
                FROM '{container_path}'
                WITH CSV HEADER
            """)
        self.conn.commit()

        # Count rows
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM timeseries")
            total = cur.fetchone()[0]

        elapsed = time.time() - t0
        rate = total / elapsed if elapsed > 0 else 0
        print(f"  [LOAD] Timeseries: {total:,} rows in {elapsed:.1f}s ({rate:,.0f}/s) [server-side COPY]")
        return total

    def load_timeseries_from_parquet(self, parquet_file: Path, batch_size: int = 500_000) -> int:
        """Load timeseries directly from Parquet using streaming COPY.

        This is much faster than CSV for large datasets:
        - No intermediate CSV file (saves disk space)
        - Streams data in batches (low RAM usage)
        - Direct binary pipe to PostgreSQL COPY

        Args:
            parquet_file: Path to timeseries.parquet
            batch_size: Rows per batch (500k = ~50MB RAM)

        Returns:
            Total rows loaded
        """
        import io
        import pyarrow.parquet as pq

        t0 = time.time()

        # Get total rows from metadata (fast, no data read)
        pf = pq.ParquetFile(parquet_file)
        total_rows = pf.metadata.num_rows

        print(f"  [LOAD] Timeseries: streaming {total_rows:,} rows from parquet...")

        rows_loaded = 0
        with self.conn.cursor() as cur:
            for batch in pf.iter_batches(batch_size=batch_size):
                # Convert batch to CSV in memory
                # Get column data as Python lists (fast)
                point_ids = batch.column("point_id").to_pylist()

                # Handle column name: could be 'timestamp' or 'time'
                if "timestamp" in batch.schema.names:
                    timestamps = batch.column("timestamp").to_pylist()
                else:
                    timestamps = batch.column("time").to_pylist()

                values = batch.column("value").to_pylist()

                # Build CSV in memory
                buf = io.StringIO()
                for pid, ts, val in zip(point_ids, timestamps, values):
                    buf.write(f"{pid},{ts},{val}\n")

                # Stream to PostgreSQL COPY
                buf.seek(0)
                cur.copy_expert(
                    "COPY timeseries (point_id, time, value) FROM STDIN WITH CSV",
                    buf
                )

                rows_loaded += len(point_ids)

                # Progress
                elapsed = time.time() - t0
                rate = rows_loaded / elapsed if elapsed > 0 else 0
                pct = rows_loaded / total_rows * 100
                eta = (total_rows - rows_loaded) / rate if rate > 0 else 0
                print(f"\r  [LOAD] Timeseries: {pct:5.1f}% ({rows_loaded:,}/{total_rows:,}) {rate:,.0f}/s ETA:{eta:.0f}s   ", end="", flush=True)

        self.conn.commit()

        elapsed = time.time() - t0
        print(f"\r  [LOAD] Timeseries: {rows_loaded:,} rows in {elapsed:.1f}s ({rows_loaded/elapsed:,.0f}/s)                    ")
        return rows_loaded

    def execute_query(self, query: str) -> Tuple[int, float]:
        """Execute a query and return (row_count, latency_ms).

        Args:
            query: SQL query string

        Returns:
            Tuple of (row_count, latency_ms)
        """
        t0 = time.perf_counter()
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                self.conn.commit()
                latency_ms = (time.perf_counter() - t0) * 1000
                return len(rows), latency_ms
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_executor(self) -> Callable[[str], Tuple[int, float]]:
        """Return query executor function."""
        return self.execute_query
