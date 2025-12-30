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
        """Create only the timeseries table (no nodes/edges)."""
        with self.conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS timeseries CASCADE")
            cur.execute("""
                CREATE UNLOGGED TABLE timeseries (
                    time TIMESTAMPTZ NOT NULL,
                    point_id TEXT NOT NULL,
                    value DOUBLE PRECISION
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
        """Load timeseries from CSV using COPY (client-side)."""
        t0 = time.time()
        total_bytes = ts_file.stat().st_size

        with self.conn.cursor() as cur:
            cur.execute("SET LOCAL synchronous_commit TO OFF")
            with open(ts_file, "rb") as f:
                cur.copy_expert(
                    "COPY timeseries (point_id, time, value) FROM STDIN WITH CSV HEADER",
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

        Args:
            container_path: Path to CSV file inside the container (e.g., /data/timeseries.csv)

        Returns:
            Total rows loaded
        """
        t0 = time.time()

        with self.conn.cursor() as cur:
            cur.execute("SET LOCAL synchronous_commit TO OFF")
            cur.execute(f"""
                COPY timeseries (point_id, time, value)
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
