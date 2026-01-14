"""Memgraph Bulk Loader for M1 (Standalone) and M2 (+ TimescaleDB).

Sprint 2 - Benchmark BaseType V3

Strategies de chargement:
1. IN_MEMORY_ANALYTICAL mode pour ingestion rapide (6x plus rapide)
2. LOAD CSV en parallele (split files)
3. Index creation avant relations
4. M2: Timeseries vers TimescaleDB via PostgresLoader

Optimisations (2025 best practices):
- Mode analytique desactive les Delta objects
- Streaming CSV grouping (avoid full file in memory)
- Adaptive batch size based on available RAM
- Index sur id avant chargement des edges

References:
- https://memgraph.com/docs/data-migration/best-practices
- https://memgraph.com/blog/how-to-import-1-milllion-nodes-and-edges-per-second-to-memgraph
"""
from __future__ import annotations

import csv
import json
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Literal

from neo4j import GraphDatabase

from ..config import MemgraphConfig, PostgresConfig
from .base import (
    BaseLoader,
    LoadPhase,
    LoadResult,
    ProgressCallback,
    TimeseriesDependencyResult,
    TimeseriesDependencyStatus,
)

if TYPE_CHECKING:
    from neo4j import Driver, Session


class MemgraphLoader(BaseLoader):
    """Loader pour Memgraph (M1 standalone, M2 avec TimescaleDB).

    Supporte:
    - M1: Graph complet en memoire (nodes + edges + timeseries)
    - M2: Graph en memoire + timeseries dans TimescaleDB

    Optimisations:
    - IN_MEMORY_ANALYTICAL mode pour ingestion 6x plus rapide
    - Streaming CSV grouping (avoid full file in memory)
    - Adaptive batch size based on available RAM
    - Index creation timing

    Exemple:
        ```python
        config = MemgraphConfig(uri="bolt://localhost:7687")
        loader = MemgraphLoader(config, paradigm="M2")

        with LoadProgressDisplay("M2") as display:
            result = loader.load_all(
                Path("data/export/m1m2"),
                progress_callback=display.update,
                workers=16,
            )
        ```
    """

    # Node types attendus
    NODE_TYPES = [
        "Site", "Building", "Floor", "Space",
        "Equipment", "Point", "Tenant", "Zone", "Contract",
    ]

    # =========================================================================
    # BULK LOAD CONFIGURATION (2025 best practices)
    # =========================================================================

    # Default batch size for UNWIND operations
    DEFAULT_BATCH_SIZE = 5000

    # Maximum batch size (avoid OOM on large batches)
    MAX_BATCH_SIZE = 20000

    # Minimum batch size (too small = overhead)
    MIN_BATCH_SIZE = 1000

    # Streaming buffer size for CSV grouping (rows to buffer before flush)
    # This avoids loading entire CSV into memory
    STREAMING_BUFFER_SIZE = 10000

    def __init__(
        self,
        config: MemgraphConfig,
        paradigm: Literal["M1", "M2"],
        timescale_config: PostgresConfig | None = None,
    ):
        """Initialise le loader.

        Args:
            config: Configuration Memgraph (Bolt)
            paradigm: "M1" (standalone) ou "M2" (+ TimescaleDB)
            timescale_config: Config PostgreSQL pour M2 (optional)
        """
        super().__init__(engine=paradigm)
        self.config = config
        self.paradigm = paradigm
        self.timescale_config = timescale_config

        self._driver: Driver | None = None

    # =========================================================================
    # CONNECTION
    # =========================================================================

    def _get_driver(self) -> Driver:
        """Retourne ou cree le driver Neo4j/Memgraph."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.config.uri,
                auth=self.config.auth,
            )
        return self._driver

    def _close_driver(self) -> None:
        """Ferme le driver."""
        if self._driver:
            self._driver.close()
            self._driver = None

    def check_connection(self) -> bool:
        """Verifie la connexion Memgraph."""
        try:
            driver = self._get_driver()
            with driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False

    def check_timeseries_dependency(self) -> TimeseriesDependencyResult:
        """Vérifie si les timeseries sont disponibles pour M1/M2.

        - M1: N'a pas besoin de TimescaleDB (tout en Memgraph)
        - M2: Nécessite TimescaleDB avec ts.timeseries peuplé

        Returns:
            TimeseriesDependencyResult avec le status et les détails
        """
        # M1 doesn't need TimescaleDB - timeseries are stored as graph nodes
        if self.paradigm == "M1":
            return TimeseriesDependencyResult(
                status=TimeseriesDependencyStatus.NOT_NEEDED,
                message="M1 stocke les timeseries dans Memgraph (TimeseriesChunk nodes)",
                can_load=True,
            )

        # M2 needs TimescaleDB
        if not self.timescale_config:
            return TimeseriesDependencyResult(
                status=TimeseriesDependencyStatus.CONNECTION_ERROR,
                message=(
                    "M2 nécessite TimescaleDB mais aucune configuration fournie.\n"
                    "Vérifiez que timescale_config est passé au loader."
                ),
                can_load=False,
            )

        # Check TimescaleDB connection and data
        try:
            from .postgres import PostgresLoader

            pg_loader = PostgresLoader(self.timescale_config, paradigm="P1")

            if not pg_loader.check_connection():
                return TimeseriesDependencyResult(
                    status=TimeseriesDependencyStatus.CONNECTION_ERROR,
                    message=(
                        "Impossible de se connecter à TimescaleDB.\n"
                        "Vérifiez que le service PostgreSQL/TimescaleDB est démarré."
                    ),
                    can_load=False,
                )

            if pg_loader._is_timeseries_populated():
                row_count = pg_loader._count_timeseries_rows()
                return TimeseriesDependencyResult(
                    status=TimeseriesDependencyStatus.AVAILABLE,
                    row_count=row_count,
                    message=f"Timeseries disponibles: {row_count:,} rows dans ts.timeseries",
                    can_load=True,
                )

            # Timeseries missing
            return TimeseriesDependencyResult(
                status=TimeseriesDependencyStatus.MISSING,
                message=(
                    "Timeseries manquantes dans TimescaleDB (ts.timeseries).\n"
                    "M2 partage les timeseries avec P1/P2.\n"
                    "Options:\n"
                    "  1. Charger P1 ou P2 d'abord (recommandé)\n"
                    "  2. Charger les timeseries maintenant pour M2"
                ),
                can_load=True,
            )

        except Exception as e:
            return TimeseriesDependencyResult(
                status=TimeseriesDependencyStatus.CONNECTION_ERROR,
                message=f"Erreur lors de la vérification TimescaleDB: {e}",
                can_load=False,
            )

    # =========================================================================
    # PUBLIC INTERFACE
    # =========================================================================

    def clear_database(self, keep_timeseries: bool = False) -> bool:
        """Vide la base Memgraph.

        Args:
            keep_timeseries: If True, preserve TimescaleDB data (M2 only)

        Returns:
            True if successful
        """
        try:
            driver = self._get_driver()
            with driver.session() as session:
                # Drop all nodes and relationships
                session.run("MATCH (n) DETACH DELETE n")

                # Drop all indexes - must match those created in _create_indexes()
                # Index on id for each node type
                for node_type in self.NODE_TYPES:
                    try:
                        session.run(f"DROP INDEX ON :{node_type}(id)")
                    except Exception:
                        pass  # Index may not exist

                # Additional indexes
                additional_indexes = [
                    ("Equipment", "equipment_type"),
                    ("Equipment", "domain"),
                    ("Point", "quantity"),
                    ("Space", "space_type"),
                ]
                for node_type, prop in additional_indexes:
                    try:
                        session.run(f"DROP INDEX ON :{node_type}({prop})")
                    except Exception:
                        pass  # Index may not exist

            # M2: Also clear TimescaleDB structure (but optionally keep timeseries)
            if self.paradigm == "M2" and self.timescale_config:
                from .postgres import PostgresLoader
                pg_loader = PostgresLoader(self.timescale_config, paradigm="P1")
                pg_loader.clear_database(keep_timeseries=keep_timeseries)

            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False

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
            workers: Nombre de workers paralleles

        Returns:
            LoadResult avec statistiques
        """
        start_time = time.time()
        result = LoadResult(engine=self.paradigm)

        try:
            driver = self._get_driver()

            with driver.session() as session:
                # Phase 1: Schema (mode analytique + indexes)
                self._emit_progress(progress_callback, LoadPhase.SCHEMA, 0, 1)
                self._setup_schema(session)
                self._emit_progress(progress_callback, LoadPhase.SCHEMA, 1, 1)

                # Switch to analytical mode for fast import
                self._set_storage_mode(session, "IN_MEMORY_ANALYTICAL")

                try:
                    # Phase 2: Nodes (prefer JSON format for native lists)
                    nodes_json = data_dir / "nodes.json"
                    nodes_csv = data_dir / "nodes.csv"
                    if nodes_json.exists():
                        result.nodes_loaded = self._load_nodes_json(
                            session, nodes_json, workers, progress_callback
                        )
                    elif nodes_csv.exists():
                        result.nodes_loaded = self._load_nodes(
                            session, nodes_csv, workers, progress_callback
                        )

                    # Phase 3: Edges
                    edges_file = data_dir / "edges.csv"
                    if edges_file.exists():
                        result.edges_loaded = self._load_edges(
                            session, edges_file, workers, progress_callback
                        )

                finally:
                    # Always switch back to transactional mode
                    self._set_storage_mode(session, "IN_MEMORY_TRANSACTIONAL")

            # Phase 4: Timeseries
            ts_file = data_dir / "timeseries.csv"
            if ts_file.exists():
                if self.paradigm == "M2" and self.timescale_config:
                    # M2: Load to TimescaleDB
                    result.timeseries_loaded = self._load_timeseries_m2(
                        ts_file, workers, progress_callback
                    )
                elif self.paradigm == "M1":
                    # M1: Load as daily chunk nodes in Memgraph
                    driver = self._get_driver()
                    with driver.session() as session:
                        result.timeseries_loaded = self._load_timeseries_m1(
                            session, ts_file, workers, progress_callback
                        )

        except Exception as e:
            result.add_error(str(e))
        finally:
            self._close_driver()

        # Validate actual counts in database vs reported counts
        # Note: Exclude TimeseriesChunk from node count (they are loaded separately)
        # and exclude HAS_CHUNK from edge count
        try:
            driver = self._get_driver()
            with driver.session() as session:
                # Count only data nodes, not TimeseriesChunk
                actual_nodes = session.run(
                    "MATCH (n) WHERE NOT n:TimeseriesChunk RETURN count(n) as c"
                ).single()["c"]
                # Count only data edges, not HAS_CHUNK
                actual_edges = session.run(
                    "MATCH ()-[r]->() WHERE type(r) <> 'HAS_CHUNK' RETURN count(r) as c"
                ).single()["c"]

                if actual_nodes != result.nodes_loaded:
                    result.add_error(
                        f"Node count mismatch: reported {result.nodes_loaded}, actual {actual_nodes}"
                    )
                    result.nodes_loaded = actual_nodes  # Correct to actual

                if actual_edges != result.edges_loaded:
                    result.add_error(
                        f"Edge count mismatch: reported {result.edges_loaded}, actual {actual_edges}"
                    )
                    result.edges_loaded = actual_edges  # Correct to actual
        except Exception as e:
            result.add_error(f"Post-load validation failed: {e}")
        finally:
            self._close_driver()

        # Calcul des stats
        result.duration_seconds = time.time() - start_time
        if result.duration_seconds > 0:
            result.rate_rows_per_sec = result.total_rows / result.duration_seconds

        return result

    # =========================================================================
    # SCHEMA SETUP
    # =========================================================================

    def _setup_schema(self, session: Session) -> None:
        """Configure les index et contraintes."""
        # Index sur id pour chaque type de node
        for node_type in self.NODE_TYPES:
            try:
                session.run(
                    f"CREATE INDEX ON :{node_type}(id)"
                )
            except Exception:
                pass  # Index may already exist

        # Index additionnels pour queries frequentes
        try:
            session.run("CREATE INDEX ON :Equipment(equipment_type)")
            session.run("CREATE INDEX ON :Equipment(domain)")
            session.run("CREATE INDEX ON :Point(quantity)")
            session.run("CREATE INDEX ON :Space(space_type)")
        except Exception:
            pass

    def _set_storage_mode(self, session: Session, mode: str) -> None:
        """Change le mode de stockage Memgraph."""
        try:
            session.run(f"STORAGE MODE {mode}")
        except Exception as e:
            # Mode may not be supported in older versions
            print(f"Warning: Could not set storage mode {mode}: {e}")

    # =========================================================================
    # NODES LOADING
    # =========================================================================

    def _load_nodes_json(
        self,
        session: Session,
        json_file: Path,
        workers: int,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les nodes depuis nodes.json (format prefere).

        Le JSON contient les listes natives Python, pas de parsing necessaire.
        Format: {"NodeType": [{"id": "...", "capabilities": ["a", "b"], ...}, ...], ...}
        """
        with open(json_file, "r", encoding="utf-8") as f:
            nodes_by_type: dict[str, list[dict]] = json.load(f)

        total_count = sum(len(nodes) for nodes in nodes_by_type.values())
        self._emit_progress(callback, LoadPhase.NODES, 0, total_count)

        start = time.time()
        loaded = 0

        for node_type, nodes in nodes_by_type.items():
            batch_loaded = self._load_nodes_batch_json(session, node_type, nodes)
            loaded += batch_loaded

            elapsed = time.time() - start
            rate = loaded / elapsed if elapsed > 0 else 0
            self._emit_progress(callback, LoadPhase.NODES, loaded, total_count, rate)

        return loaded

    def _load_nodes_batch_json(
        self,
        session: Session,
        node_type: str,
        nodes: list[dict],
    ) -> int:
        """Charge un batch de nodes depuis JSON (listes natives, pas de parsing)."""
        if not nodes:
            return 0

        # Build properties list from ALL nodes
        all_props = set()
        for node in nodes:
            all_props.update(k for k, v in node.items() if k != "node_type" and v is not None)
        props = sorted(all_props)

        # Build Cypher query with UNWIND
        prop_assignments = ", ".join(f"{prop}: row.{prop}" for prop in props)

        query = f"""
        UNWIND $rows AS row
        CREATE (n:{node_type} {{{prop_assignments}}})
        """

        # Execute in batches of 5000
        batch_size = 5000
        loaded = 0

        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i + batch_size]
            try:
                result = session.run(query, rows=batch)
                summary = result.consume()
                actual_created = summary.counters.nodes_created
                loaded += actual_created
                if actual_created < len(batch):
                    print(f"Warning: JSON nodes batch {i//batch_size}: only {actual_created}/{len(batch)} created")
            except Exception as e:
                print(f"Error loading JSON nodes batch {i//batch_size} ({node_type}): {e}")

        return loaded

    def _load_nodes(
        self,
        session: Session,
        csv_file: Path,
        workers: int,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les nodes depuis nodes.csv (fallback si nodes.json absent).

        Uses streaming grouping for memory efficiency on large files (2025 best practice).
        """
        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.NODES, 0, total_count)

        start = time.time()
        loaded = 0

        # Use streaming for large files (> 100K rows), legacy for small
        if total_count > 100_000:
            # Streaming mode: memory-efficient
            for node_type, rows in self._stream_nodes_by_type(csv_file):
                batch_loaded = self._load_nodes_batch(session, node_type, rows)
                loaded += batch_loaded

                elapsed = time.time() - start
                rate = loaded / elapsed if elapsed > 0 else 0
                self._emit_progress(callback, LoadPhase.NODES, loaded, total_count, rate)
        else:
            # Legacy mode: faster for small files
            nodes_by_type = self._group_nodes_by_type(csv_file)

            for node_type, rows in nodes_by_type.items():
                batch_loaded = self._load_nodes_batch(session, node_type, rows)
                loaded += batch_loaded

                elapsed = time.time() - start
                rate = loaded / elapsed if elapsed > 0 else 0
                self._emit_progress(callback, LoadPhase.NODES, loaded, total_count, rate)

        return loaded

    def _group_nodes_by_type(self, csv_file: Path) -> dict[str, list[dict]]:
        """Groupe les nodes par type (legacy - loads all into memory).

        Note: For large files, use _stream_nodes_by_type() instead.
        """
        nodes_by_type: dict[str, list[dict]] = {}

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_type = row.get("node_type", "Unknown")
                if node_type not in nodes_by_type:
                    nodes_by_type[node_type] = []
                nodes_by_type[node_type].append(row)

        return nodes_by_type

    def _stream_nodes_by_type(
        self, csv_file: Path
    ) -> Iterator[tuple[str, list[dict]]]:
        """Stream nodes grouped by type without loading entire file.

        This is memory-efficient for large CSV files.
        Yields (node_type, batch) tuples when buffer is full or type changes.

        2025 best practice: Stream processing for large datasets.
        """
        buffer: dict[str, list[dict]] = {}
        buffer_size = 0

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_type = row.get("node_type", "Unknown")
                if node_type not in buffer:
                    buffer[node_type] = []
                buffer[node_type].append(row)
                buffer_size += 1

                # Flush buffer when it reaches limit
                if buffer_size >= self.STREAMING_BUFFER_SIZE:
                    for ntype, rows in buffer.items():
                        if rows:
                            yield (ntype, rows)
                    buffer = {}
                    buffer_size = 0

        # Flush remaining
        for ntype, rows in buffer.items():
            if rows:
                yield (ntype, rows)

    # Properties that should be parsed as JSON arrays (exported as JSON strings in CSV)
    JSON_ARRAY_PROPERTIES = {"capabilities", "tags", "maintenance_history", "capabilities_list"}

    def _load_nodes_batch(
        self,
        session: Session,
        node_type: str,
        rows: list[dict],
    ) -> int:
        """Charge un batch de nodes d'un meme type."""
        if not rows:
            return 0

        # Build properties list from ALL rows (excluding node_type)
        # Must consider all rows because first row might have empty values
        all_props = set()
        for row in rows:
            for k, v in row.items():
                if k != "node_type" and v:  # Property exists with value
                    all_props.add(k)
        props = sorted(all_props)  # Sorted for consistent ordering

        # Build Cypher query with UNWIND
        prop_assignments = ", ".join(
            f"{prop}: row.{prop}" for prop in props
        )

        query = f"""
        UNWIND $rows AS row
        CREATE (n:{node_type} {{{prop_assignments}}})
        """

        # Clean rows (convert empty strings to null, parse JSON arrays)
        clean_rows = []
        for row in rows:
            clean_row = {}
            for k, v in row.items():
                if k == "node_type":
                    continue
                if not v:
                    clean_row[k] = None
                elif k in self.JSON_ARRAY_PROPERTIES:
                    # Parse JSON string back to native Cypher list
                    try:
                        clean_row[k] = json.loads(v) if isinstance(v, str) else v
                    except (json.JSONDecodeError, TypeError) as e:
                        preview = v[:50] if isinstance(v, str) else str(v)[:50]
                        print(f"Warning: JSON parse failed for {k}={preview}...: {e}")
                        clean_row[k] = v  # Keep as string if parsing fails
                else:
                    clean_row[k] = v
            clean_rows.append(clean_row)

        # Execute in batches of 5000
        batch_size = 5000
        loaded = 0

        for i in range(0, len(clean_rows), batch_size):
            batch = clean_rows[i:i + batch_size]
            try:
                result = session.run(query, rows=batch)
                summary = result.consume()
                actual_created = summary.counters.nodes_created
                loaded += actual_created
                if actual_created < len(batch):
                    print(f"Warning: Nodes batch {i//batch_size}: only {actual_created}/{len(batch)} created")
            except Exception as e:
                print(f"Error loading nodes batch {i//batch_size} ({node_type}): {e}")
                # Continue with next batch instead of crashing

        return loaded

    # =========================================================================
    # EDGES LOADING
    # =========================================================================

    def _load_edges(
        self,
        session: Session,
        csv_file: Path,
        workers: int,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les edges depuis edges.csv.

        Uses streaming grouping for memory efficiency on large files (2025 best practice).
        """
        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.EDGES, 0, total_count)

        start = time.time()
        loaded = 0

        # Use streaming for large files (> 100K rows), legacy for small
        if total_count > 100_000:
            # Streaming mode: memory-efficient
            for rel_type, rows in self._stream_edges_by_type(csv_file):
                batch_loaded = self._load_edges_batch(session, rel_type, rows)
                loaded += batch_loaded

                elapsed = time.time() - start
                rate = loaded / elapsed if elapsed > 0 else 0
                self._emit_progress(callback, LoadPhase.EDGES, loaded, total_count, rate)
        else:
            # Legacy mode: faster for small files
            edges_by_type = self._group_edges_by_type(csv_file)

            for rel_type, rows in edges_by_type.items():
                batch_loaded = self._load_edges_batch(session, rel_type, rows)
                loaded += batch_loaded

                elapsed = time.time() - start
                rate = loaded / elapsed if elapsed > 0 else 0
                self._emit_progress(callback, LoadPhase.EDGES, loaded, total_count, rate)

        return loaded

    def _group_edges_by_type(self, csv_file: Path) -> dict[str, list[dict]]:
        """Groupe les edges par type de relation (legacy - loads all into memory).

        Note: For large files, use _stream_edges_by_type() instead.
        """
        edges_by_type: dict[str, list[dict]] = {}

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rel_type = row.get("rel_type", "RELATED_TO")
                if rel_type not in edges_by_type:
                    edges_by_type[rel_type] = []
                edges_by_type[rel_type].append(row)

        return edges_by_type

    def _stream_edges_by_type(
        self, csv_file: Path
    ) -> Iterator[tuple[str, list[dict]]]:
        """Stream edges grouped by type without loading entire file.

        Memory-efficient for large CSV files (2025 best practice).
        """
        buffer: dict[str, list[dict]] = {}
        buffer_size = 0

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rel_type = row.get("rel_type", "RELATED_TO")
                if rel_type not in buffer:
                    buffer[rel_type] = []
                buffer[rel_type].append(row)
                buffer_size += 1

                # Flush buffer when it reaches limit
                if buffer_size >= self.STREAMING_BUFFER_SIZE:
                    for rtype, rows in buffer.items():
                        if rows:
                            yield (rtype, rows)
                    buffer = {}
                    buffer_size = 0

        # Flush remaining
        for rtype, rows in buffer.items():
            if rows:
                yield (rtype, rows)

    def _load_edges_batch(
        self,
        session: Session,
        rel_type: str,
        rows: list[dict],
    ) -> int:
        """Charge un batch d'edges d'un meme type."""
        if not rows:
            return 0

        # Cypher query avec UNWIND et MATCH
        query = f"""
        UNWIND $rows AS row
        MATCH (source {{id: row.source_id}})
        MATCH (target {{id: row.target_id}})
        CREATE (source)-[:{rel_type}]->(target)
        """

        # Execute in batches of 5000
        batch_size = 5000
        loaded = 0

        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            try:
                result = session.run(query, rows=batch)
                summary = result.consume()
                actual_created = summary.counters.relationships_created
                loaded += actual_created
                if actual_created < len(batch):
                    print(f"Warning: Edges batch {i//batch_size} ({rel_type}): only {actual_created}/{len(batch)} created (missing source/target nodes?)")
            except Exception as e:
                print(f"Error loading edges batch {i//batch_size} ({rel_type}): {e}")

        return loaded

    # =========================================================================
    # TIMESERIES
    # =========================================================================

    def _load_timeseries_m1(
        self,
        session: Session,
        csv_file: Path,
        workers: int,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les timeseries comme daily chunk nodes (M1 seulement).

        Modèle de données:
        - Un node TimeseriesChunk par (point_id, date)
        - Properties: point_id, date, values[], timestamps[]
        - Relation: (Point)-[:HAS_CHUNK]->(TimeseriesChunk)
        """
        from collections import defaultdict
        from datetime import datetime

        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.TIMESERIES, 0, total_count)

        start = time.time()

        # Group timeseries by (point_id, date)
        chunks = defaultdict(lambda: {"timestamps": [], "values": []})

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse timestamp (format: "2024-01-15T08:00:00Z")
                ts_str = row["time"]
                value = float(row["value"])
                point_id = row["point_id"]

                # Extract date (YYYY-MM-DD)
                date = ts_str[:10]

                # Group by (point_id, date)
                key = (point_id, date)
                chunks[key]["timestamps"].append(ts_str)
                chunks[key]["values"].append(value)

        # Create TimeseriesChunk nodes
        loaded = 0
        batch_size = 1000
        chunk_rows = []

        for (point_id, date), data in chunks.items():
            chunk_rows.append({
                "point_id": point_id,
                "date": date,
                "timestamps": data["timestamps"],
                "values": data["values"],
            })

            if len(chunk_rows) >= batch_size:
                self._create_ts_chunks(session, chunk_rows)
                loaded += len(chunk_rows)

                elapsed = time.time() - start
                rate = loaded / elapsed if elapsed > 0 else 0
                self._emit_progress(callback, LoadPhase.TIMESERIES, loaded, total_count, rate)

                chunk_rows = []

        # Load remaining chunks
        if chunk_rows:
            self._create_ts_chunks(session, chunk_rows)
            loaded += len(chunk_rows)

        elapsed = time.time() - start
        rate = loaded / elapsed if elapsed > 0 else 0
        self._emit_progress(callback, LoadPhase.TIMESERIES, total_count, total_count, rate)

        return total_count

    def _create_ts_chunks(self, session: Session, chunks: list[dict]) -> int:
        """Create TimeseriesChunk nodes and link to Points.

        Returns:
            Number of chunks actually created
        """
        query = """
        UNWIND $chunks AS chunk
        MATCH (p:Point {id: chunk.point_id})
        CREATE (ts:TimeseriesChunk {
            point_id: chunk.point_id,
            date: chunk.date,
            timestamps: chunk.timestamps,
            values: chunk.values
        })
        CREATE (p)-[:HAS_CHUNK]->(ts)
        """
        try:
            result = session.run(query, chunks=chunks)
            summary = result.consume()
            actual_created = summary.counters.nodes_created
            if actual_created < len(chunks):
                print(f"Warning: TS chunks: only {actual_created}/{len(chunks)} created (missing Point nodes?)")
            return actual_created
        except Exception as e:
            print(f"Error creating timeseries chunks: {e}")
            return 0

    def _load_timeseries_m2(
        self,
        csv_file: Path,
        workers: int,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les timeseries vers TimescaleDB (M2 seulement)."""
        if not self.timescale_config:
            return 0

        # Import ici pour eviter circular import
        from .postgres import PostgresLoader

        pg_loader = PostgresLoader(self.timescale_config, paradigm="P1")

        # Créer le schema timeseries si nécessaire
        pg_loader.ensure_timeseries_schema()

        # Skip if already populated (Option A)
        if pg_loader._is_timeseries_populated():
            print("⏭️  Timeseries already loaded for M2, skipping")
            return pg_loader._count_timeseries_rows()

        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.TIMESERIES, 0, total_count)

        # Delegate to PostgresLoader
        return pg_loader._load_timeseries(csv_file, workers, callback)
