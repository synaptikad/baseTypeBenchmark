"""Load dataset into PostgreSQL/TimescaleDB.

Supports two schema modes:
- P1 (relational): Normalized tables with foreign keys
- P2 (JSONB): Flexible document schema
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import psycopg2
from psycopg2.extras import execute_batch


def get_connection(
    host: str = "localhost",
    port: int = 5432,
    user: str = "benchmark",
    password: str = "benchmark",
    database: str = "benchmark",
    max_retries: Optional[int] = None,
    retry_delay: float = 3.0
):
    """Create a PostgreSQL connection with retry logic.

    Args:
        host: PostgreSQL host
        port: PostgreSQL port
        user: PostgreSQL user
        password: PostgreSQL password
        database: PostgreSQL database
        max_retries: Maximum connection attempts
        retry_delay: Seconds to wait between retries

    Returns:
        psycopg2 connection object

    Raises:
        psycopg2.OperationalError: If connection fails after all retries
    """
    # TimescaleDB (especially on first boot with empty volumes) can take longer
    # than ~30s to become ready. Default to a time-based budget (~180s) while
    # allowing callers to override explicitly.
    if max_retries is None:
        max_wait_s = float(os.getenv("BTB_PG_CONNECT_TIMEOUT_S", "180"))
        retry_delay = float(os.getenv("BTB_PG_CONNECT_RETRY_DELAY_S", str(retry_delay)))
        max_retries = max(1, int(math.ceil(max_wait_s / max(retry_delay, 0.1))))

    last_error = None
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            return conn
        except psycopg2.OperationalError as e:
            last_error = e
            if attempt < max_retries - 1:
                print(f"[INFO] PostgreSQL not ready (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"[ERROR] PostgreSQL connection failed after {max_retries} attempts")
    raise last_error


def clear_database(conn) -> None:
    """Drop all tables and recreate schema."""
    with conn.cursor() as cur:
        cur.execute("""
            DROP TABLE IF EXISTS timeseries CASCADE;
            DROP TABLE IF EXISTS edges CASCADE;
            DROP TABLE IF EXISTS nodes CASCADE;
        """)
    conn.commit()


# =============================================================================
# P1: Relational Schema
# =============================================================================

def create_schema_relational(conn) -> None:
    """Create optimized relational schema (P1).

    Optimizations:
    - No FK on edges (integrity ensured by generator, 10-30% INSERT gain)
    - Composite indexes for efficient graph traversals
    - TimescaleDB with automatic compression after 7 days
    """
    with conn.cursor() as cur:
        # Nodes table with optimized indexes
        cur.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT,
                building_id INTEGER DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
            CREATE INDEX IF NOT EXISTS idx_nodes_building ON nodes(building_id);
            CREATE INDEX IF NOT EXISTS idx_nodes_type_building ON nodes(type, building_id);
        """)

        # Edges table WITHOUT FK for performance
        cur.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                src_id TEXT NOT NULL,
                dst_id TEXT NOT NULL,
                rel_type TEXT NOT NULL,
                PRIMARY KEY (src_id, dst_id, rel_type)
            );
            -- Composite indexes for graph traversals in both directions
            CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, rel_type);
            CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, rel_type);
            CREATE INDEX IF NOT EXISTS idx_edges_rel ON edges(rel_type);
        """)

        # Timeseries hypertable
        cur.execute("""
            CREATE TABLE IF NOT EXISTS timeseries (
                time TIMESTAMPTZ NOT NULL,
                point_id TEXT NOT NULL,
                value DOUBLE PRECISION
            );
        """)

        # Convert to hypertable with 1-day chunks
        cur.execute("""
            SELECT create_hypertable('timeseries', 'time',
                                     if_not_exists => TRUE,
                                     chunk_time_interval => INTERVAL '1 day');
        """)

        # Optimized indexes for timeseries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_ts_point_time ON timeseries(point_id, time DESC);
            CREATE INDEX IF NOT EXISTS idx_ts_time ON timeseries(time);
        """)

        # Enable compression for data older than 7 days
        cur.execute("""
            ALTER TABLE timeseries SET (
                timescaledb.compress,
                timescaledb.compress_segmentby = 'point_id',
                timescaledb.compress_orderby = 'time DESC'
            );
        """)

        # Add compression policy (ignore if already exists)
        try:
            cur.execute("""
                SELECT add_compression_policy('timeseries', INTERVAL '7 days', if_not_exists => TRUE);
            """)
        except Exception:
            pass  # Policy may already exist

    conn.commit()


def load_nodes_relational(conn, nodes_path: Path, batch_size: int = 1000) -> int:
    """Load nodes from JSON lines into relational schema."""
    total = 0
    batch = []
    t0 = time.perf_counter()

    with nodes_path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            node = json.loads(line)
            batch.append((
                node["id"],
                node["type"],
                node.get("name", ""),
                node.get("building_id", 0)
            ))

            if len(batch) >= batch_size:
                with conn.cursor() as cur:
                    execute_batch(cur, """
                        INSERT INTO nodes (id, type, name, building_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, batch)
                conn.commit()
                total += len(batch)
                batch.clear()

    if batch:
        with conn.cursor() as cur:
            execute_batch(cur, """
                INSERT INTO nodes (id, type, name, building_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, batch)
        conn.commit()
        total += len(batch)

    elapsed = time.perf_counter() - t0
    print(f"Nodes inserted: {total} in {elapsed:.2f}s")
    return total


def load_edges_relational(conn, edges_path: Path, batch_size: int = 1000) -> int:
    """Load edges from JSON lines into relational schema."""
    total = 0
    batch = []
    t0 = time.perf_counter()

    with edges_path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            edge = json.loads(line)
            batch.append((
                edge["src"],
                edge["dst"],
                edge["rel"]
            ))

            if len(batch) >= batch_size:
                with conn.cursor() as cur:
                    execute_batch(cur, """
                        INSERT INTO edges (src_id, dst_id, rel_type)
                        VALUES (%s, %s, %s)
                    """, batch)
                conn.commit()
                total += len(batch)
                batch.clear()

    if batch:
        with conn.cursor() as cur:
            execute_batch(cur, """
                INSERT INTO edges (src_id, dst_id, rel_type)
                VALUES (%s, %s, %s)
            """, batch)
        conn.commit()
        total += len(batch)

    elapsed = time.perf_counter() - t0
    print(f"Edges inserted: {total} in {elapsed:.2f}s")
    return total


def load_timeseries_relational(conn, chunks_path: Path, batch_size: int = 5000) -> int:
    """Load timeseries from chunks JSON into hypertable."""
    total = 0
    batch = []
    t0 = time.perf_counter()

    with chunks_path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)

            # Skip edge records (HAS_CHUNK)
            if data.get("rel") == "HAS_CHUNK":
                continue

            # Process chunk node
            if data.get("type") == "TimeseriesChunk":
                point_id = data["point_id"]
                start_time = data["start_time"]
                freq = data["frequency_seconds"]

                for i, value in enumerate(data["values"]):
                    ts = start_time + i * freq
                    batch.append((
                        f"to_timestamp({ts})",
                        point_id,
                        value
                    ))

                    if len(batch) >= batch_size:
                        _flush_timeseries_batch(conn, batch)
                        total += len(batch)
                        batch.clear()

    if batch:
        _flush_timeseries_batch(conn, batch)
        total += len(batch)

    elapsed = time.perf_counter() - t0
    print(f"Timeseries samples inserted: {total} in {elapsed:.2f}s")
    return total


def _flush_timeseries_batch(conn, batch: List) -> None:
    """Flush timeseries batch using COPY for performance."""
    with conn.cursor() as cur:
        # Build values list
        values = []
        for ts_expr, point_id, value in batch:
            values.append(f"({ts_expr}, '{point_id}', {value})")

        if values:
            cur.execute(f"""
                INSERT INTO timeseries (time, point_id, value)
                VALUES {','.join(values)}
            """)
    conn.commit()


# =============================================================================
# P2: JSONB Schema
# =============================================================================

def create_schema_jsonb(conn) -> None:
    """Create optimized JSONB document schema (P2).

    Optimizations:
    - Extracted columns from JSONB for fast B-tree index lookups
    - GIN index with jsonb_path_ops (compact, supports @> queries)
    - Optional JSONB on edges for extended properties
    """
    with conn.cursor() as cur:
        # JSONB nodes table with extracted columns for fast filtering
        cur.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT,
                building_id INTEGER DEFAULT 0,
                data JSONB NOT NULL DEFAULT '{}'::jsonb
            );
            -- B-tree indexes on extracted columns (fast for equality/range)
            CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
            CREATE INDEX IF NOT EXISTS idx_nodes_building ON nodes(building_id);
            CREATE INDEX IF NOT EXISTS idx_nodes_type_building ON nodes(type, building_id);
            -- GIN index for searches within JSONB document
            CREATE INDEX IF NOT EXISTS idx_nodes_gin ON nodes USING GIN (data jsonb_path_ops);
        """)

        # Edges with optional JSONB properties
        cur.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                src_id TEXT NOT NULL,
                dst_id TEXT NOT NULL,
                rel_type TEXT NOT NULL,
                props JSONB DEFAULT NULL,
                PRIMARY KEY (src_id, dst_id, rel_type)
            );
            -- Composite indexes for graph traversals
            CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, rel_type);
            CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, rel_type);
            CREATE INDEX IF NOT EXISTS idx_edges_rel ON edges(rel_type);
            -- Partial GIN index on edge properties (only if used)
            CREATE INDEX IF NOT EXISTS idx_edges_props_gin ON edges USING GIN (props jsonb_path_ops)
                WHERE props IS NOT NULL;
        """)

        # Timeseries hypertable with optional metadata
        cur.execute("""
            CREATE TABLE IF NOT EXISTS timeseries (
                time TIMESTAMPTZ NOT NULL,
                point_id TEXT NOT NULL,
                value DOUBLE PRECISION,
                metadata JSONB DEFAULT NULL
            );
        """)

        cur.execute("""
            SELECT create_hypertable('timeseries', 'time',
                                     if_not_exists => TRUE,
                                     chunk_time_interval => INTERVAL '1 day');
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_ts_point_time ON timeseries(point_id, time DESC);
            CREATE INDEX IF NOT EXISTS idx_ts_time ON timeseries(time);
        """)

        # Compression with metadata support
        cur.execute("""
            ALTER TABLE timeseries SET (
                timescaledb.compress,
                timescaledb.compress_segmentby = 'point_id',
                timescaledb.compress_orderby = 'time DESC'
            );
        """)

        try:
            cur.execute("""
                SELECT add_compression_policy('timeseries', INTERVAL '7 days', if_not_exists => TRUE);
            """)
        except Exception:
            pass

    conn.commit()


def load_nodes_jsonb(conn, nodes_path: Path, batch_size: int = 1000) -> int:
    """Load nodes with extracted columns + JSONB data (P2 optimized).

    Extracts type, name, building_id for fast B-tree indexes while
    keeping full document in JSONB for flexible queries.
    """
    total = 0
    batch = []
    t0 = time.perf_counter()

    with nodes_path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            node = json.loads(line)
            # Extract columns + keep full JSONB
            batch.append((
                node["id"],
                node["type"],
                node.get("name", ""),
                node.get("building_id", 0),
                json.dumps(node)
            ))

            if len(batch) >= batch_size:
                with conn.cursor() as cur:
                    execute_batch(cur, """
                        INSERT INTO nodes (id, type, name, building_id, data)
                        VALUES (%s, %s, %s, %s, %s::jsonb)
                        ON CONFLICT (id) DO UPDATE SET
                            type = EXCLUDED.type,
                            name = EXCLUDED.name,
                            building_id = EXCLUDED.building_id,
                            data = EXCLUDED.data
                    """, batch)
                conn.commit()
                total += len(batch)
                batch.clear()

    if batch:
        with conn.cursor() as cur:
            execute_batch(cur, """
                INSERT INTO nodes (id, type, name, building_id, data)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (id) DO UPDATE SET
                    type = EXCLUDED.type,
                    name = EXCLUDED.name,
                    building_id = EXCLUDED.building_id,
                    data = EXCLUDED.data
            """, batch)
        conn.commit()
        total += len(batch)

    elapsed = time.perf_counter() - t0
    print(f"JSONB nodes inserted: {total} in {elapsed:.2f}s")
    return total


# =============================================================================
# Main entry point
# =============================================================================

def load_p1(
    conn,
    data_dir: Path,
    skip_timeseries: bool = False
) -> Dict[str, int]:
    """Load dataset with P1 (relational) schema."""
    print("\n[P1] Loading with relational schema...")

    create_schema_relational(conn)

    results = {
        "nodes": load_nodes_relational(conn, data_dir / "nodes.json"),
        "edges": load_edges_relational(conn, data_dir / "edges.json"),
        "timeseries": 0,
    }

    if not skip_timeseries:
        chunks_path = data_dir / "timeseries_chunks.json"
        if chunks_path.exists():
            results["timeseries"] = load_timeseries_relational(conn, chunks_path)

    return results


def load_p2(
    conn,
    data_dir: Path,
    skip_timeseries: bool = False
) -> Dict[str, int]:
    """Load dataset with P2 (JSONB) schema."""
    print("\n[P2] Loading with JSONB schema...")

    create_schema_jsonb(conn)

    results = {
        "nodes": load_nodes_jsonb(conn, data_dir / "nodes.json"),
        "edges": load_edges_relational(conn, data_dir / "edges.json"),
        "timeseries": 0,
    }

    if not skip_timeseries:
        chunks_path = data_dir / "timeseries_chunks.json"
        if chunks_path.exists():
            results["timeseries"] = load_timeseries_relational(conn, chunks_path)

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PostgreSQL/TimescaleDB loader for BaseType Benchmark"
    )
    parser.add_argument(
        "--mode",
        choices=["P1", "P2"],
        default="P1",
        help="Schema mode: P1 (relational) or P2 (JSONB)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="PostgreSQL host"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5432,
        help="PostgreSQL port"
    )
    parser.add_argument(
        "--user",
        default="benchmark",
        help="PostgreSQL user"
    )
    parser.add_argument(
        "--password",
        default="benchmark",
        help="PostgreSQL password"
    )
    parser.add_argument(
        "--database",
        default="benchmark",
        help="PostgreSQL database"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Directory containing nodes.json, edges.json, timeseries_chunks.json"
    )
    parser.add_argument(
        "--skip-clear",
        action="store_true",
        help="Don't clear existing data"
    )
    parser.add_argument(
        "--skip-timeseries",
        action="store_true",
        help="Skip loading timeseries data"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    conn = get_connection(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database
    )

    try:
        if not args.skip_clear:
            print("Clearing existing data...")
            clear_database(conn)

        t0 = time.perf_counter()

        if args.mode == "P1":
            results = load_p1(conn, args.data_dir, args.skip_timeseries)
        else:
            results = load_p2(conn, args.data_dir, args.skip_timeseries)

        elapsed = time.perf_counter() - t0

        print(f"\n[OK] Loading complete in {elapsed:.2f}s")
        print(f"  Nodes: {results['nodes']}")
        print(f"  Edges: {results['edges']}")
        print(f"  Timeseries samples: {results['timeseries']}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
