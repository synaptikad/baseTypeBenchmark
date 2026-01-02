"""TimescaleDB engine for hybrid scenarios (M2, O2).

This module provides timeseries functionality for hybrid architectures
where the graph is in Memgraph/Oxigraph and timeseries in TimescaleDB.
"""

import time
from pathlib import Path
from typing import Callable, List, Tuple

import psycopg2

from .postgres import get_connection


class TimescaleEngine:
    """TimescaleDB engine for M2/O2 hybrid scenarios.

    Handles only the timeseries part - graph is handled by MemgraphEngine/OxigraphEngine.
    """

    def __init__(self):
        self.conn = None

    def connect(self) -> None:
        """Establish database connection."""
        self.conn = get_connection()

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def create_timeseries_schema(self) -> None:
        """Create only the timeseries table (no nodes/edges).

        Includes building_id for consistency with shared timeseries.csv format,
        even though hybrid scenarios do building filtering via graph engine.
        """
        with self.conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS timeseries CASCADE")
            cur.execute("""
                CREATE UNLOGGED TABLE timeseries (
                    time TIMESTAMPTZ NOT NULL,
                    point_id TEXT NOT NULL,
                    building_id TEXT,
                    value REAL
                )
            """)

        self.conn.commit()

    def _create_ts_index(self) -> None:
        """Create timeseries index after bulk load."""
        with self.conn.cursor() as cur:
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ts_point_time ON timeseries(point_id, time DESC)")
        self.conn.commit()

    def _reset_stage_table(self) -> None:
        """Deprecated: staging not used in simple UNLOGGED flow."""
        return

    def _move_stage_to_main(self) -> int:
        """Deprecated: staging not used in simple UNLOGGED flow."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM timeseries")
            total = cur.fetchone()[0]
        return total

    def load_timeseries(self, ts_file: Path) -> int:
        """Load timeseries from CSV using COPY (client-side).

        CSV format: point_id,time,building_id,value
        """
        t0 = time.time()
        total_bytes = ts_file.stat().st_size

        with self.conn.cursor() as cur:
            cur.execute("SET LOCAL synchronous_commit TO OFF")
            with open(ts_file, "rb") as f:
                cur.copy_expert(
                    "COPY timeseries (point_id, time, building_id, value) FROM STDIN WITH CSV HEADER",
                    f
                )
        self.conn.commit()
        self._create_ts_index()

        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM timeseries")
            total = cur.fetchone()[0]

        elapsed = time.time() - t0
        mb = total_bytes / (1024 * 1024)
        print(f"  [LOAD] Timeseries (TS): {total:,} rows ({mb:.0f} MB) in {elapsed:.1f}s")
        return total

    def load_timeseries_server_copy(self, container_path: str) -> int:
        """Load timeseries using server-side COPY FROM (10x faster).

        Requires the CSV file to be mounted in the container at container_path.
        CSV format: point_id,time,building_id,value

        Args:
            container_path: Path to CSV file inside the container (e.g., /data/timeseries.csv)

        Returns:
            Total rows loaded
        """
        t0 = time.time()

        with self.conn.cursor() as cur:
            cur.execute("SET LOCAL synchronous_commit TO OFF")
            cur.execute(f"""
                COPY timeseries (point_id, time, building_id, value)
                FROM '{container_path}'
                WITH CSV HEADER
            """)
        self.conn.commit()
        self._create_ts_index()

        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM timeseries")
            total = cur.fetchone()[0]

        elapsed = time.time() - t0
        rate = total / elapsed if elapsed > 0 else 0
        print(f"  [LOAD] Timeseries (TS): {total:,} rows in {elapsed:.1f}s ({rate:,.0f}/s) [server-side COPY]")
        return total

    def load_timeseries_parallel_copy(
        self,
        container_path: str,
        container_name: str = "btb_timescaledb",
        workers: int = 8,
        batch_size: int = 50000,
        csv_columns: str = "point_id,time,building_id,value",
    ) -> int:
        """Load timeseries using `timescaledb-parallel-copy` inside the container.

        This avoids client-side COPY streaming and typically provides the fastest ingest.
        The CSV is expected to have a header; we rely on auto-column mapping.

        Args:
            container_path: CSV path inside container (e.g., /data/timeseries.csv)
            container_name: Docker container name
            workers: Parallel workers
            batch_size: Rows per batch

        Returns:
            Total rows loaded
        """
        from basetype_benchmark.runner import docker as docker_mod

        # Reuse the same env/.env resolution logic as PostgresEngine
        from .postgres import _resolve_pg_config_defaults  # type: ignore

        t0 = time.time()

        # Connection string inside container (localhost)
        resolved = _resolve_pg_config_defaults("localhost", 5432, "benchmark", "benchmark", "benchmark")
        user = str(resolved["user"])
        password = str(resolved["password"])
        database = str(resolved["database"])
        conn_str = f"postgresql://{user}:{password}@localhost:5432/{database}"

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

        self._create_ts_index()

        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM timeseries")
            total = cur.fetchone()[0]
        self.conn.commit()

        elapsed = time.time() - t0
        rate = total / elapsed if elapsed > 0 else 0
        print(f"  [LOAD] Timeseries (TS): {total:,} rows in {elapsed:.1f}s ({rate:,.0f}/s) [parallel-copy]")
        return total

    def execute_timeseries_query(self, query: str, point_ids: List[str] = None) -> Tuple[int, float]:
        """Execute a timeseries SQL query.

        Args:
            query: SQL query (can contain $POINT_IDS placeholder)
            point_ids: List of point IDs to inject

        Returns:
            Tuple of (row_count, latency_ms)
        """
        # Replace $POINT_IDS placeholder if point_ids provided
        if point_ids and "$POINT_IDS" in query:
            ids_str = ",".join(f"'{pid}'" for pid in point_ids)
            query = query.replace("$POINT_IDS", ids_str)

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
        return lambda q: self.execute_timeseries_query(q)
