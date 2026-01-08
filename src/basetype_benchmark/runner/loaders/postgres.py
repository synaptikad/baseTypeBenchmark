"""PostgreSQL Bulk Loader for P1 (Relational) and P2 (JSONB).

Sprint 2 - Benchmark BaseType V3

Strategies de chargement:
1. timescaledb-parallel-copy (si disponible) - optimal pour timeseries
2. psycopg3 binary COPY multi-thread - fallback performant
3. psycopg3 text COPY - fallback simple

Optimisations:
- Binary COPY pour 10-30% plus rapide sur timestamps/floats
- Parallel workers pour timeseries massives
- Progress callback pour UI interactive
"""
from __future__ import annotations

import csv
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Literal

import psycopg

from ..config import PostgresConfig
from .base import BaseLoader, LoadPhase, LoadProgress, LoadResult, ProgressCallback

if TYPE_CHECKING:
    pass


class PostgresLoader(BaseLoader):
    """Loader pour PostgreSQL (P1 relationnel, P2 JSONB).

    Supporte:
    - P1: Tables separees (sites, buildings, equipment, etc.)
    - P2: Table unique avec JSONB
    - TimescaleDB hypertable pour timeseries

    Exemple:
        ```python
        config = PostgresConfig(dsn="postgresql://localhost/benchmark")
        loader = PostgresLoader(config, paradigm="P1")

        with LoadProgressDisplay("P1") as display:
            result = loader.load_all(
                Path("data/export/p1"),
                progress_callback=display.update,
                workers=16,
            )
        ```
    """

    # Tables P1 dans l'ordre de chargement (respecte les FK)
    P1_TABLES = [
        "sites",
        "buildings",
        "floors",
        "spaces",
        "equipment",
        "points",
        "tenants",
        "zones",
        "contracts",
    ]

    def __init__(
        self,
        config: PostgresConfig,
        paradigm: Literal["P1", "P2"],
    ):
        """Initialise le loader.

        Args:
            config: Configuration PostgreSQL
            paradigm: "P1" (relationnel) ou "P2" (JSONB)
        """
        super().__init__(engine=paradigm)
        self.config = config
        self.paradigm = paradigm

        # Detecte timescaledb-parallel-copy
        self._parallel_copy_bin = shutil.which("timescaledb-parallel-copy")

    # =========================================================================
    # PUBLIC INTERFACE
    # =========================================================================

    def check_connection(self) -> bool:
        """Verifie la connexion PostgreSQL."""
        try:
            with psycopg.connect(self.config.dsn) as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    def clear_database(self, keep_timeseries: bool = False) -> bool:
        """Vide toutes les tables (ignore if tables don't exist).

        Args:
            keep_timeseries: If True, preserve timeseries table for Option A

        Returns:
            True if successful
        """
        try:
            with psycopg.connect(self.config.dsn) as conn:
                with conn.cursor() as cur:
                    # Desactive les FK temporairement
                    cur.execute("SET session_replication_role = replica")

                    # Truncate timeseries (only if not keeping)
                    if not keep_timeseries:
                        cur.execute(
                            "TRUNCATE TABLE timeseries CASCADE"
                            if self._table_exists(cur, "timeseries")
                            else "SELECT 1"
                        )

                    # Truncate edges (ignore if not exists)
                    cur.execute(
                        "TRUNCATE TABLE edges CASCADE"
                        if self._table_exists(cur, "edges")
                        else "SELECT 1"
                    )

                    if self.paradigm == "P1":
                        # Truncate toutes les tables P1
                        for table in reversed(self.P1_TABLES):
                            if self._table_exists(cur, table):
                                cur.execute(f"TRUNCATE TABLE {table} CASCADE")
                    else:
                        # P2: une seule table nodes
                        if self._table_exists(cur, "nodes"):
                            cur.execute("TRUNCATE TABLE nodes CASCADE")

                    # Reactive les FK
                    cur.execute("SET session_replication_role = DEFAULT")

                conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False

    def _table_exists(self, cur, table_name: str) -> bool:
        """Check if a table exists in the database."""
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = %s)",
            (table_name,)
        )
        return cur.fetchone()[0]

    def load_all(
        self,
        data_dir: Path,
        progress_callback: ProgressCallback | None = None,
        workers: int = 16,
    ) -> LoadResult:
        """Charge toutes les donnees depuis un repertoire d'export.

        Args:
            data_dir: Repertoire avec les fichiers CSV exportes
            progress_callback: Callback pour progress updates
            workers: Nombre de workers paralleles (pour timeseries)

        Returns:
            LoadResult avec statistiques
        """
        start_time = time.time()
        result = LoadResult(engine=self.paradigm)

        try:
            # Phase 1: Schema (required)
            self._emit_progress(progress_callback, LoadPhase.SCHEMA, 0, 1)
            self._load_schema(data_dir)
            self._emit_progress(progress_callback, LoadPhase.SCHEMA, 1, 1)

            # Phase 2: Nodes
            if self.paradigm == "P1":
                result.nodes_loaded = self._load_nodes_p1(
                    data_dir, progress_callback
                )
            else:
                result.nodes_loaded = self._load_nodes_p2(
                    data_dir, progress_callback
                )

            # Phase 3: Edges
            edges_file = data_dir / "edges.csv"
            if edges_file.exists():
                result.edges_loaded = self._load_edges(
                    edges_file, progress_callback
                )

            # Phase 4: Timeseries (la plus lourde)
            ts_file = data_dir / "timeseries.csv"
            if ts_file.exists():
                result.timeseries_loaded = self._load_timeseries(
                    ts_file, workers, progress_callback
                )

        except Exception as e:
            result.add_error(str(e))

        # Calcul des stats
        result.duration_seconds = time.time() - start_time
        if result.duration_seconds > 0:
            result.rate_rows_per_sec = result.total_rows / result.duration_seconds

        return result

    # =========================================================================
    # P1 LOADING (Multiple tables)
    # =========================================================================

    def _load_nodes_p1(
        self,
        data_dir: Path,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les nodes P1 (tables separees)."""
        total_rows = 0

        # Compte total pour progress
        total_count = sum(
            self._count_csv_rows(data_dir / f"{table}.csv")
            for table in self.P1_TABLES
        )
        self._emit_progress(callback, LoadPhase.NODES, 0, total_count)

        loaded = 0
        start = time.time()

        with psycopg.connect(self.config.dsn) as conn:
            for table in self.P1_TABLES:
                csv_file = data_dir / f"{table}.csv"
                if not csv_file.exists():
                    continue

                rows = self._copy_csv_to_table(conn, table, csv_file)
                loaded += rows
                total_rows += rows

                # Progress update
                elapsed = time.time() - start
                rate = loaded / elapsed if elapsed > 0 else 0
                self._emit_progress(callback, LoadPhase.NODES, loaded, total_count, rate)

            conn.commit()

        return total_rows

    # =========================================================================
    # P2 LOADING (Single JSONB table)
    # =========================================================================

    def _load_nodes_p2(
        self,
        data_dir: Path,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les nodes P2 (table unique avec JSONB)."""
        csv_file = data_dir / "nodes.csv"
        if not csv_file.exists():
            return 0

        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.NODES, 0, total_count)

        start = time.time()

        with psycopg.connect(self.config.dsn) as conn:
            rows = self._copy_csv_to_table(conn, "nodes", csv_file)
            conn.commit()

        elapsed = time.time() - start
        rate = rows / elapsed if elapsed > 0 else 0
        self._emit_progress(callback, LoadPhase.NODES, rows, total_count, rate)

        return rows

    # =========================================================================
    # EDGES LOADING
    # =========================================================================

    def _load_edges(
        self,
        csv_file: Path,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les edges."""
        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.EDGES, 0, total_count)

        start = time.time()

        with psycopg.connect(self.config.dsn) as conn:
            rows = self._copy_csv_to_table(conn, "edges", csv_file)
            conn.commit()

        elapsed = time.time() - start
        rate = rows / elapsed if elapsed > 0 else 0
        self._emit_progress(callback, LoadPhase.EDGES, rows, total_count, rate)

        return rows

    # =========================================================================
    # TIMESERIES LOADING (Optimized)
    # =========================================================================

    def _load_timeseries(
        self,
        csv_file: Path,
        workers: int,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les timeseries avec la methode la plus rapide disponible.

        Strategies par ordre de preference:
        1. timescaledb-parallel-copy (subprocess)
        2. psycopg3 binary COPY multi-thread
        3. psycopg3 text COPY simple
        """
        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.TIMESERIES, 0, total_count)

        if self._parallel_copy_bin and workers > 1:
            # Strategy 1: timescaledb-parallel-copy
            return self._load_timeseries_parallel_copy(
                csv_file, workers, total_count, callback
            )
        elif workers > 1:
            # Strategy 2: psycopg3 binary COPY multi-thread
            return self._load_timeseries_threaded(
                csv_file, workers, total_count, callback
            )
        else:
            # Strategy 3: psycopg3 simple COPY
            return self._load_timeseries_simple(csv_file, total_count, callback)

    def _load_timeseries_parallel_copy(
        self,
        csv_file: Path,
        workers: int,
        total_count: int,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge avec timescaledb-parallel-copy (optimal)."""
        cmd = [
            self._parallel_copy_bin,
            "--connection", self.config.dsn,
            "--table", "timeseries",
            "--file", str(csv_file),
            "--workers", str(workers),
            "--batch-size", "10000",
            "--skip-header",
            "--reporting-period", "2s",
        ]

        start = time.time()
        loaded = 0

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            # Parse output pour progress
            for line in process.stdout:
                # Format: "at 123456, rate 45678.90 rows/sec"
                if "rate" in line.lower():
                    try:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "at":
                                loaded = int(parts[i + 1].rstrip(","))
                            elif part == "rate":
                                rate = float(parts[i + 1])
                                self._emit_progress(
                                    callback, LoadPhase.TIMESERIES,
                                    loaded, total_count, rate
                                )
                    except (IndexError, ValueError):
                        pass

            process.wait()

            if process.returncode != 0:
                raise RuntimeError(f"timescaledb-parallel-copy failed: {process.returncode}")

            # Final progress
            elapsed = time.time() - start
            rate = total_count / elapsed if elapsed > 0 else 0
            self._emit_progress(callback, LoadPhase.TIMESERIES, total_count, total_count, rate)

            return total_count

        except Exception as e:
            # Fallback sur methode simple
            print(f"parallel-copy failed ({e}), falling back to simple COPY")
            return self._load_timeseries_simple(csv_file, total_count, callback)

    def _load_timeseries_threaded(
        self,
        csv_file: Path,
        workers: int,
        total_count: int,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge avec psycopg3 binary COPY en multi-thread."""
        # Split le CSV en chunks
        chunk_files = self._split_csv(csv_file, workers)

        start = time.time()
        loaded = 0
        lock = None  # Pour thread-safe progress updates

        try:
            import threading
            lock = threading.Lock()

            def load_chunk(chunk_file: Path) -> int:
                """Charge un chunk avec binary COPY."""
                nonlocal loaded
                count = 0

                with psycopg.connect(self.config.dsn) as conn:
                    with conn.cursor() as cur:
                        # Binary COPY pour performance
                        with cur.copy(
                            "COPY timeseries (time, point_id, value) "
                            "FROM STDIN (FORMAT BINARY)"
                        ) as copy:
                            for row in self._read_timeseries_csv(chunk_file):
                                copy.write_row(row)
                                count += 1

                                # Progress update (every 10000 rows)
                                if count % 10000 == 0 and callback:
                                    with lock:
                                        loaded += 10000
                                        elapsed = time.time() - start
                                        rate = loaded / elapsed if elapsed > 0 else 0
                                        self._emit_progress(
                                            callback, LoadPhase.TIMESERIES,
                                            loaded, total_count, rate
                                        )

                    conn.commit()

                return count

            # Execute en parallele
            total_loaded = 0
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [
                    executor.submit(load_chunk, chunk)
                    for chunk in chunk_files
                ]

                for future in as_completed(futures):
                    total_loaded += future.result()

            # Final progress
            elapsed = time.time() - start
            rate = total_loaded / elapsed if elapsed > 0 else 0
            self._emit_progress(callback, LoadPhase.TIMESERIES, total_loaded, total_count, rate)

            return total_loaded

        finally:
            # Cleanup temp files
            for chunk in chunk_files:
                try:
                    chunk.unlink()
                except Exception:
                    pass

    def _load_timeseries_simple(
        self,
        csv_file: Path,
        total_count: int,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge avec psycopg3 text COPY simple."""
        start = time.time()
        loaded = 0

        with psycopg.connect(self.config.dsn) as conn:
            with conn.cursor() as cur:
                with open(csv_file, "rb") as f:
                    # Skip header
                    f.readline()

                    with cur.copy(
                        "COPY timeseries (time, point_id, value) "
                        "FROM STDIN WITH (FORMAT csv)"
                    ) as copy:
                        while True:
                            chunk = f.read(1024 * 1024)  # 1MB chunks
                            if not chunk:
                                break
                            copy.write(chunk)

                            # Estimate progress (rough)
                            loaded = min(loaded + 50000, total_count)
                            elapsed = time.time() - start
                            rate = loaded / elapsed if elapsed > 0 else 0
                            self._emit_progress(
                                callback, LoadPhase.TIMESERIES,
                                loaded, total_count, rate
                            )

            conn.commit()

        # Final
        elapsed = time.time() - start
        rate = total_count / elapsed if elapsed > 0 else 0
        self._emit_progress(callback, LoadPhase.TIMESERIES, total_count, total_count, rate)

        return total_count

    # =========================================================================
    # SCHEMA LOADING
    # =========================================================================

    def _load_schema(self, data_dir: Path) -> bool:
        """Load schema SQL file to create tables.

        Looks for schema_p1.sql or schema_p2.sql in data_dir.
        """
        schema_file = data_dir / f"schema_{self.paradigm.lower()}.sql"
        if not schema_file.exists():
            raise FileNotFoundError(
                f"Schema file not found: {schema_file}. "
                f"Run export first to generate schema."
            )

        with psycopg.connect(self.config.dsn) as conn:
            with conn.cursor() as cur:
                # Read and execute schema SQL
                sql = schema_file.read_text(encoding="utf-8")
                cur.execute(sql)
            conn.commit()

        return True

    def ensure_timeseries_schema(self) -> bool:
        """Create timeseries table and hypertable if they don't exist.

        Used by M2/O2 loaders that delegate timeseries to TimescaleDB.
        """
        schema_sql = """
        CREATE EXTENSION IF NOT EXISTS timescaledb;

        CREATE TABLE IF NOT EXISTS timeseries (
            time TIMESTAMPTZ NOT NULL,
            point_id VARCHAR(64) NOT NULL,
            value DOUBLE PRECISION NOT NULL
        );

        SELECT create_hypertable('timeseries', 'time', if_not_exists => TRUE);

        CREATE INDEX IF NOT EXISTS idx_timeseries_point ON timeseries(point_id, time DESC);
        """

        with psycopg.connect(self.config.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()

        return True

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _copy_csv_to_table(
        self,
        conn: psycopg.Connection,
        table: str,
        csv_file: Path,
    ) -> int:
        """COPY un CSV vers une table avec colonnes explicites du header."""
        # Lire le header pour obtenir les noms de colonnes
        with open(csv_file, "r", encoding="utf-8") as f:
            header_line = f.readline().strip()
        columns = header_line.split(",")
        columns_sql = ", ".join(columns)

        with open(csv_file, "rb") as f:
            with conn.cursor() as cur:
                with cur.copy(
                    f"COPY {table} ({columns_sql}) FROM STDIN WITH (FORMAT csv, HEADER true)"
                ) as copy:
                    while True:
                        chunk = f.read(1024 * 1024)
                        if not chunk:
                            break
                        copy.write(chunk)

        return self._count_csv_rows(csv_file)

    def _split_csv(self, csv_file: Path, num_chunks: int) -> list[Path]:
        """Split un CSV en plusieurs fichiers."""
        total_rows = self._count_csv_rows(csv_file)
        rows_per_chunk = max(1, total_rows // num_chunks)

        chunk_files = []
        temp_dir = Path(tempfile.mkdtemp())

        with open(csv_file, "r", encoding="utf-8") as f:
            header = f.readline()
            chunk_num = 0
            current_chunk = None
            current_count = 0

            for line in f:
                if current_chunk is None or current_count >= rows_per_chunk:
                    if current_chunk:
                        current_chunk.close()

                    chunk_path = temp_dir / f"chunk_{chunk_num:04d}.csv"
                    chunk_files.append(chunk_path)
                    current_chunk = open(chunk_path, "w", encoding="utf-8")
                    current_chunk.write(header)
                    chunk_num += 1
                    current_count = 0

                current_chunk.write(line)
                current_count += 1

            if current_chunk:
                current_chunk.close()

        return chunk_files

    def _read_timeseries_csv(
        self,
        csv_file: Path,
    ) -> Iterator[tuple[datetime, str, float]]:
        """Lit un CSV timeseries et yield des tuples types."""
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield (
                    datetime.fromisoformat(row["time"]),
                    row["point_id"],
                    float(row["value"]),
                )
