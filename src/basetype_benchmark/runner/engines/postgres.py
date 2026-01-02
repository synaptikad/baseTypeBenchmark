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
    user: str = "benchmark",
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

            # Timeseries table with denormalized building_id for Digital Twin patterns
            # This avoids expensive JOIN on 30M+ rows for building-level queries (Q7, Q12)
            cur.execute("""
                CREATE TABLE timeseries (
                    time TIMESTAMPTZ NOT NULL,
                    point_id TEXT NOT NULL,
                    building_id TEXT NOT NULL,
                    value REAL
                )
            """)

            # Create hypertable with space partitioning by building_id
            # This enables chunk pruning for building-level queries (Q7, Q12)
            try:
                cur.execute("""
                    SELECT create_hypertable(
                        'timeseries', 
                        'time',
                        partitioning_column => 'building_id',
                        number_partitions => 4,
                        if_not_exists => TRUE
                    )
                """)
            except Exception:
                # Fallback to time-only partitioning
                try:
                    cur.execute("""
                        SELECT create_hypertable('timeseries', 'time', if_not_exists => TRUE)
                    """)
                except Exception:
                    pass

            # Indexes for Digital Twin query patterns
            cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_building ON nodes(building_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, rel_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, rel_type)")

        self.conn.commit()

    def _create_ts_index(self) -> None:
        """Create timeseries indexes after bulk load for Digital Twin query patterns."""
        with self.conn.cursor() as cur:
            # Index for point-level queries (Q1, Q2, Q6)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ts_point_time ON timeseries(point_id, time DESC)")
            # Index for building-level queries (Q7, Q12) - critical for Digital Twin dashboards
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ts_building_time ON timeseries(building_id, time DESC)")
        self.conn.commit()

    def load_timeseries_direct(self, ts_file: Path) -> int:
        """Load timeseries using optimized bulk loading strategy.
        
        Strategy: Load into regular UNLOGGED table first, then convert to hypertable.
        This is 5-10x faster than loading directly into hypertable because:
        1. No chunk routing overhead during COPY
        2. UNLOGGED = no WAL writes
        3. Single bulk conversion to hypertable at the end
        
        Args:
            ts_file: Path to CSV file (point_id,time,building_id,value)
            
        Returns:
            Total rows loaded
        """
        t0 = time.time()
        total_bytes = ts_file.stat().st_size
        mb = total_bytes / (1024 * 1024)
        
        with self.conn.cursor() as cur:
            # Drop existing hypertable
            cur.execute("DROP TABLE IF EXISTS timeseries CASCADE")
            
            # Create UNLOGGED table (no WAL = fastest possible writes)
            cur.execute("""
                CREATE UNLOGGED TABLE timeseries (
                    time TIMESTAMPTZ NOT NULL,
                    point_id TEXT NOT NULL,
                    building_id TEXT NOT NULL,
                    value REAL
                )
            """)
        self.conn.commit()
        
        print(f"  [LOAD] Timeseries: COPY {mb:.0f} MB into unlogged table...")
        t_copy = time.time()
        
        with self.conn.cursor() as cur:
            # Maximum speed settings
            cur.execute("SET LOCAL synchronous_commit TO OFF")
            
            # COPY into unlogged table (blazing fast)
            with open(ts_file, "rb") as f:
                cur.copy_expert(
                    "COPY timeseries (point_id, time, building_id, value) FROM STDIN WITH CSV HEADER",
                    f
                )
        self.conn.commit()
        
        copy_time = time.time() - t_copy
        
        # Get row count before conversion
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM timeseries")
            total = cur.fetchone()[0]
        
        rate_copy = total / copy_time if copy_time > 0 else 0
        print(f"  [LOAD] COPY done: {total:,} rows in {copy_time:.1f}s ({rate_copy:,.0f}/s)")
        
        # Convert to logged table (required for hypertable)
        print(f"  [LOAD] Converting to logged table...")
        t_convert = time.time()
        with self.conn.cursor() as cur:
            cur.execute("ALTER TABLE timeseries SET LOGGED")
        self.conn.commit()
        convert_time = time.time() - t_convert
        print(f"  [LOAD] Logged in {convert_time:.1f}s")
        
        # Convert to hypertable
        print(f"  [LOAD] Converting to hypertable...")
        t_hyper = time.time()
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT create_hypertable(
                    'timeseries', 
                    'time',
                    chunk_time_interval => INTERVAL '1 day',
                    migrate_data => TRUE,
                    if_not_exists => TRUE
                )
            """)
        self.conn.commit()
        hyper_time = time.time() - t_hyper
        print(f"  [LOAD] Hypertable created in {hyper_time:.1f}s")
        
        # Create indexes
        print(f"  [LOAD] Creating indexes...")
        t_idx = time.time()
        self._create_ts_index()
        idx_time = time.time() - t_idx
        print(f"  [LOAD] Indexes created in {idx_time:.1f}s")
        
        elapsed = time.time() - t0
        rate = total / elapsed if elapsed > 0 else 0
        print(f"  [LOAD] Timeseries: {total:,} rows in {elapsed:.1f}s ({rate:,.0f}/s) [bulk load]")
        return total

    def load_timeseries_server_direct(self, container_path: str) -> int:
        """Load timeseries using server-side COPY with bulk loading strategy.
        
        Fastest method: server-side COPY + UNLOGGED table + convert to hypertable.
        
        Args:
            container_path: Path to CSV file inside container (e.g., /data/timeseries.csv)
            
        Returns:
            Total rows loaded
        """
        t0 = time.time()
        
        with self.conn.cursor() as cur:
            # Drop existing hypertable
            cur.execute("DROP TABLE IF EXISTS timeseries CASCADE")
            
            # Create UNLOGGED table
            cur.execute("""
                CREATE UNLOGGED TABLE timeseries (
                    time TIMESTAMPTZ NOT NULL,
                    point_id TEXT NOT NULL,
                    building_id TEXT NOT NULL,
                    value REAL
                )
            """)
        self.conn.commit()
        
        print(f"  [LOAD] Timeseries: server-side COPY into unlogged table...")
        t_copy = time.time()
        
        with self.conn.cursor() as cur:
            cur.execute("SET LOCAL synchronous_commit TO OFF")
            cur.execute(f"""
                COPY timeseries (point_id, time, building_id, value)
                FROM '{container_path}'
                WITH CSV HEADER
            """)
        self.conn.commit()
        
        copy_time = time.time() - t_copy
        
        # Get row count
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM timeseries")
            total = cur.fetchone()[0]
        
        rate_copy = total / copy_time if copy_time > 0 else 0
        print(f"  [LOAD] COPY done: {total:,} rows in {copy_time:.1f}s ({rate_copy:,.0f}/s)")
        
        # Convert to logged + hypertable
        print(f"  [LOAD] Converting to logged table...")
        with self.conn.cursor() as cur:
            cur.execute("ALTER TABLE timeseries SET LOGGED")
        self.conn.commit()
        
        print(f"  [LOAD] Converting to hypertable...")
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT create_hypertable(
                    'timeseries', 
                    'time',
                    chunk_time_interval => INTERVAL '1 day',
                    migrate_data => TRUE,
                    if_not_exists => TRUE
                )
            """)
        self.conn.commit()
        
        # Create indexes
        print(f"  [LOAD] Creating indexes...")
        self._create_ts_index()
        
        elapsed = time.time() - t0
        rate = total / elapsed if elapsed > 0 else 0
        print(f"  [LOAD] Timeseries: {total:,} rows in {elapsed:.1f}s ({rate:,.0f}/s) [server bulk]")
        return total

    def load_timeseries_parallel_copy(
        self,
        container_path: str,
        container_name: Optional[str] = None,
        workers: Optional[int] = None,
        batch_size: Optional[int] = None,
        csv_columns: Optional[str] = None,
    ) -> int:
        """Load timeseries using `timescaledb-parallel-copy` inside the container.

        This avoids Python streaming and uses the fastest available bulk path.

        Args:
            container_path: Path to CSV file inside container (e.g., /data/timeseries.csv)
            container_name: Docker container name (default: env BTB_TIMESCALE_CONTAINER or btb_timescaledb)
            workers: Parallel workers (default: env BTB_TS_PARALLEL_COPY_WORKERS or 8)
            batch_size: Rows per batch (default: env BTB_TS_PARALLEL_COPY_BATCH_SIZE or 50000)

        Returns:
            Total rows loaded
        """
        from basetype_benchmark.runner import docker as docker_mod

        t0 = time.time()

        if container_name is None:
            container_name = os.getenv("BTB_TIMESCALE_CONTAINER") or docker_mod.get_container_name("timescaledb")

        if workers is None:
            workers = int(os.getenv("BTB_TS_PARALLEL_COPY_WORKERS", "8"))
        if batch_size is None:
            batch_size = int(os.getenv("BTB_TS_PARALLEL_COPY_BATCH_SIZE", "50000"))
        if csv_columns is None:
            csv_columns = os.getenv("BTB_TS_PARALLEL_COPY_COLUMNS") or "point_id,time,building_id,value"

        # Create UNLOGGED table first (no WAL = fastest possible writes)
        with self.conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS timeseries CASCADE")
            cur.execute(
                """
                CREATE UNLOGGED TABLE timeseries (
                    time TIMESTAMPTZ NOT NULL,
                    point_id TEXT NOT NULL,
                    building_id TEXT NOT NULL,
                    value REAL
                )
                """
            )
        self.conn.commit()

        # Build a connection string for in-container access.
        cfg = _resolve_pg_config_defaults("localhost", 5432, "benchmark", "benchmark", "benchmark")
        user = str(cfg["user"])
        password = str(cfg["password"])
        database = str(cfg["database"])
        conn_str = f"postgresql://{user}:{password}@localhost:5432/{database}"

        print(f"  [LOAD] Timeseries: timescaledb-parallel-copy (workers={workers}, batch={batch_size})...")

        # Use explicit CSV column list (matches the order in the CSV file).
        argv = [
            "timescaledb-parallel-copy",
            "--connection",
            conn_str,
            "--table",
            "timeseries",
            "--file",
            container_path,
            "--columns",
            csv_columns,
            "--skip-header",
            "--workers",
            str(workers),
            "--batch-size",
            str(batch_size),
            "--copy-options",
            "CSV",
        ]

        cp = docker_mod.run_in_container(container_name, argv, check=False)
        if cp.returncode != 0:
            msg = (cp.stderr or cp.stdout or "").strip()
            raise RuntimeError(f"timescaledb-parallel-copy failed (exit={cp.returncode}): {msg}")

        # Get row count
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM timeseries")
            total = cur.fetchone()[0]
        self.conn.commit()

        print("  [LOAD] Converting to logged table...")
        with self.conn.cursor() as cur:
            cur.execute("ALTER TABLE timeseries SET LOGGED")
        self.conn.commit()

        print("  [LOAD] Converting to hypertable...")
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT create_hypertable(
                    'timeseries',
                    'time',
                    chunk_time_interval => INTERVAL '1 day',
                    migrate_data => TRUE,
                    if_not_exists => TRUE
                )
                """
            )
        self.conn.commit()

        print("  [LOAD] Creating indexes...")
        self._create_ts_index()

        elapsed = time.time() - t0
        rate = total / elapsed if elapsed > 0 else 0
        print(f"  [LOAD] Timeseries: {total:,} rows in {elapsed:.1f}s ({rate:,.0f}/s) [parallel-copy]")
        return total

    # Legacy methods kept for compatibility
    def _reset_stage_table(self) -> None:
        """Recreate unlogged staging table (DEPRECATED - use direct COPY instead)."""
        with self.conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS timeseries_stage")
            cur.execute("""
                CREATE UNLOGGED TABLE timeseries_stage (
                    time TIMESTAMPTZ NOT NULL,
                    point_id TEXT NOT NULL,
                    building_id TEXT,
                    value REAL
                )
            """)
        self.conn.commit()

    def _move_stage_to_main(self) -> int:
        """Insert staged rows into hypertable (DEPRECATED - very slow for large datasets)."""
        with self.conn.cursor() as cur:
            cur.execute("SET LOCAL synchronous_commit TO OFF")
            cur.execute("INSERT INTO timeseries SELECT * FROM timeseries_stage")
            cur.execute("DROP TABLE IF EXISTS timeseries_stage")
        self.conn.commit()

        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM timeseries")
            total = cur.fetchone()[0]
        return total

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
        """Load timeseries from CSV using direct COPY into hypertable.
        
        This is the optimized method - COPY directly into hypertable without staging.
        Much faster than the old staging approach for large datasets.

        CSV format: point_id,time,building_id,value
        """
        return self.load_timeseries_direct(ts_file)

    def load_timeseries_server_copy(self, container_path: str) -> int:
        """Load timeseries using server-side COPY directly into hypertable.

        Requires the CSV file to be mounted in the container at container_path.
        This is the fastest method - no network transfer, no staging table.

        CSV format: point_id,time,building_id,value

        Args:
            container_path: Path to CSV file inside the container (e.g., /data/timeseries.csv)

        Returns:
            Total rows loaded
        """
        return self.load_timeseries_server_direct(container_path)

    def load_timeseries_from_parquet(self, parquet_file: Path, batch_size: int = 5_000_000) -> int:
        """Load timeseries from pre-enriched CSV (with building_id).
        
        Expects timeseries_enriched.csv in same directory as parquet file.
        This CSV is generated once during dataset export using DuckDB.
        """
        try:
            import duckdb  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "DuckDB is required for Parquet->CSV enrichment. "
                "Either install duckdb or load from timeseries.csv instead. "
                f"Original error: {e}"
            )
        
        t0 = time.time()
        
        # Check for pre-enriched CSV (generated during export)
        enriched_csv = parquet_file.parent / "timeseries_enriched.csv"
        
        if not enriched_csv.exists():
            print(f"  [LOAD] Generating enriched CSV with DuckDB (one-time)...")
            self._generate_enriched_csv(parquet_file, enriched_csv)
        
        # Get row count
        con = duckdb.connect()
        total_rows = con.execute(f"SELECT COUNT(*) FROM read_csv('{enriched_csv}', header=true, sample_size=-1)").fetchone()[0]
        con.close()
        
        print(f"  [LOAD] Timeseries: {total_rows:,} rows via COPY FROM CSV...")

        # Drop and recreate table
        with self.conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS timeseries CASCADE")
            cur.execute("""
                CREATE UNLOGGED TABLE timeseries (
                    time TIMESTAMPTZ NOT NULL,
                    point_id TEXT NOT NULL,
                    building_id TEXT NOT NULL,
                    value REAL
                )
            """)
        self.conn.commit()

        # Prefer in-container parallel-copy if the file is mounted at /data/parquet/
        try:
            ts_rows = self.load_timeseries_parallel_copy(
                "/data/parquet/timeseries_enriched.csv",
                csv_columns="time,point_id,building_id,value",
            )
        except Exception as e:
            print(f"  [WARN] parallel-copy failed ({e}); falling back to client-side COPY...")
            print(f"  [LOAD] COPY FROM file...")
            t_load = time.time()
            with self.conn.cursor() as cur:
                with open(enriched_csv, "rb") as f:
                    cur.copy_expert(
                        "COPY timeseries (time, point_id, building_id, value) FROM STDIN WITH CSV HEADER",
                        f,
                    )
            self.conn.commit()
            load_time = time.time() - t_load
            print(f"  [LOAD] COPY done: {total_rows:,} rows in {load_time:.1f}s ({total_rows/load_time:,.0f}/s)")

        # Convert to LOGGED table
        print(f"  [LOAD] Converting to logged table...")
        t_log = time.time()
        with self.conn.cursor() as cur:
            cur.execute("ALTER TABLE timeseries SET LOGGED")
        self.conn.commit()
        print(f"  [LOAD] Logged in {time.time() - t_log:.1f}s")

        # Convert to hypertable
        print(f"  [LOAD] Creating hypertable...")
        t_hyper = time.time()
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT create_hypertable(
                    'timeseries', 'time',
                    chunk_time_interval => interval '1 day',
                    migrate_data => TRUE,
                    if_not_exists => TRUE
                )
            """)
        self.conn.commit()
        print(f"  [LOAD] Hypertable created in {time.time() - t_hyper:.1f}s")

        # Create indexes
        print(f"  [LOAD] Creating indexes...")
        t_idx = time.time()
        with self.conn.cursor() as cur:
            cur.execute("CREATE INDEX IF NOT EXISTS idx_timeseries_point ON timeseries (point_id, time DESC)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_timeseries_building ON timeseries (building_id, time DESC)")
        self.conn.commit()
        print(f"  [LOAD] Indexes created in {time.time() - t_idx:.1f}s")

        total_time = time.time() - t0
        print(f"  [LOAD] Total timeseries load: {total_time:.1f}s ({total_rows/total_time:,.0f}/s overall)")

        return total_rows

    def _generate_enriched_csv(self, parquet_file: Path, output_csv: Path) -> None:
        """Generate timeseries CSV with building_id using DuckDB."""
        import duckdb  # type: ignore
        
        parquet_dir = parquet_file.parent
        con = duckdb.connect()
        
        con.execute(f"""
            COPY (
                SELECT 
                    ts.timestamp as time,
                    ts.point_id,
                    COALESCE(json_extract_string(n.properties, '$.building_id'), '') as building_id,
                    ts.value
                FROM read_parquet('{parquet_file}') ts
                LEFT JOIN read_parquet('{parquet_dir}/nodes.parquet') n ON ts.point_id = n.id
            ) TO '{output_csv}' (HEADER, DELIMITER ',')
        """)
        con.close()

        # Do not create indexes here: this function only generates the CSV.
        # Index creation belongs to the actual load step.

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
