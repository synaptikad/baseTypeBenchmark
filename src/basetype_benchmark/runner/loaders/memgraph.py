"""Memgraph Bulk Loader for M1 (Standalone) and M2 (+ TimescaleDB).

Sprint 2 - Benchmark BaseType V3

Strategies de chargement:
1. IN_MEMORY_ANALYTICAL mode pour ingestion rapide (6x plus rapide)
2. LOAD CSV en parallele (split files)
3. Index creation avant relations
4. M2: Timeseries vers TimescaleDB via PostgresLoader

Optimisations:
- Mode analytique desactive les Delta objects
- Split CSV par node_type pour parallelisme
- Index sur id avant chargement des edges
"""
from __future__ import annotations

import csv
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Literal

from neo4j import GraphDatabase

from ..config import MemgraphConfig, PostgresConfig
from .base import BaseLoader, LoadPhase, LoadResult, ProgressCallback

if TYPE_CHECKING:
    from neo4j import Driver, Session


class MemgraphLoader(BaseLoader):
    """Loader pour Memgraph (M1 standalone, M2 avec TimescaleDB).

    Supporte:
    - M1: Graph complet en memoire (nodes + edges + timeseries)
    - M2: Graph en memoire + timeseries dans TimescaleDB

    Optimisations:
    - IN_MEMORY_ANALYTICAL mode pour ingestion 6x plus rapide
    - Parallel LOAD CSV
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

    # =========================================================================
    # PUBLIC INTERFACE
    # =========================================================================

    def clear_database(self) -> bool:
        """Vide la base Memgraph."""
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
                    # Phase 2: Nodes
                    nodes_file = data_dir / "nodes.csv"
                    if nodes_file.exists():
                        result.nodes_loaded = self._load_nodes(
                            session, nodes_file, workers, progress_callback
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

    def _load_nodes(
        self,
        session: Session,
        csv_file: Path,
        workers: int,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les nodes depuis nodes.csv."""
        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.NODES, 0, total_count)

        start = time.time()

        # Group nodes by type for better loading
        nodes_by_type = self._group_nodes_by_type(csv_file)

        loaded = 0
        for node_type, rows in nodes_by_type.items():
            batch_loaded = self._load_nodes_batch(session, node_type, rows)
            loaded += batch_loaded

            elapsed = time.time() - start
            rate = loaded / elapsed if elapsed > 0 else 0
            self._emit_progress(callback, LoadPhase.NODES, loaded, total_count, rate)

        return loaded

    def _group_nodes_by_type(self, csv_file: Path) -> dict[str, list[dict]]:
        """Groupe les nodes par type."""
        nodes_by_type: dict[str, list[dict]] = {}

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_type = row.get("node_type", "Unknown")
                if node_type not in nodes_by_type:
                    nodes_by_type[node_type] = []
                nodes_by_type[node_type].append(row)

        return nodes_by_type

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

        # Clean rows (convert empty strings to null)
        clean_rows = []
        for row in rows:
            clean_row = {
                k: (v if v else None) for k, v in row.items()
                if k != "node_type"
            }
            clean_rows.append(clean_row)

        # Execute in batches of 5000
        batch_size = 5000
        loaded = 0

        for i in range(0, len(clean_rows), batch_size):
            batch = clean_rows[i:i + batch_size]
            session.run(query, rows=batch)
            loaded += len(batch)

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
        """Charge les edges depuis edges.csv."""
        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.EDGES, 0, total_count)

        start = time.time()

        # Group edges by rel_type
        edges_by_type = self._group_edges_by_type(csv_file)

        loaded = 0
        for rel_type, rows in edges_by_type.items():
            batch_loaded = self._load_edges_batch(session, rel_type, rows)
            loaded += batch_loaded

            elapsed = time.time() - start
            rate = loaded / elapsed if elapsed > 0 else 0
            self._emit_progress(callback, LoadPhase.EDGES, loaded, total_count, rate)

        return loaded

    def _group_edges_by_type(self, csv_file: Path) -> dict[str, list[dict]]:
        """Groupe les edges par type de relation."""
        edges_by_type: dict[str, list[dict]] = {}

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rel_type = row.get("rel_type", "RELATED_TO")
                if rel_type not in edges_by_type:
                    edges_by_type[rel_type] = []
                edges_by_type[rel_type].append(row)

        return edges_by_type

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
            session.run(query, rows=batch)
            loaded += len(batch)

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

    def _create_ts_chunks(self, session: Session, chunks: list[dict]) -> None:
        """Create TimeseriesChunk nodes and link to Points."""
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
        session.run(query, chunks=chunks)

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

        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.TIMESERIES, 0, total_count)

        # Delegate to PostgresLoader
        return pg_loader._load_timeseries(csv_file, workers, callback)
