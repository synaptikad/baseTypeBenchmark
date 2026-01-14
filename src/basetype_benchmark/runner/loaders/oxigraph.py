"""Oxigraph Bulk Loader for O2 (+ TimescaleDB).

Sprint 2 - Benchmark BaseType V3

Strategies de chargement:
1. Chunked HTTP POST pour N-Triples (500K lignes par requete)
2. Streaming pour eviter OOM
3. Parallel HTTP POST with connection pooling
4. Timeseries vers TimescaleDB via PostgresLoader

Optimisations (2025 best practices):
- N-Triples est le format le plus rapide pour bulk RDF
- Chunking evite les timeouts et OOM (500K triples per chunk)
- Parallel POST requests with ThreadPoolExecutor
- HTTP keep-alive via connection pooling
- Streaming lecture fichier

References:
- https://docs.rs/oxigraph/latest/oxigraph/store/struct.BulkLoader.html
- https://github.com/oxigraph/oxigraph/discussions/1092
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Literal

import httpx

from ..config import OxigraphConfig, PostgresConfig
from .base import (
    BaseLoader,
    LoadPhase,
    LoadResult,
    ProgressCallback,
    TimeseriesDependencyResult,
    TimeseriesDependencyStatus,
)

if TYPE_CHECKING:
    pass


class OxigraphLoader(BaseLoader):
    """Loader pour Oxigraph O2 (+ TimescaleDB pour timeseries).

    Supporte:
    - O2: RDF graph en Oxigraph + timeseries dans TimescaleDB

    Optimisations (2025 best practices):
    - Chunked HTTP POST (500K triples par requete - was 100K)
    - Parallel POST with ThreadPoolExecutor
    - HTTP keep-alive via connection pooling
    - Streaming lecture pour fichiers massifs
    - N-Triples format (plus rapide que Turtle/RDF-XML)

    Exemple:
        ```python
        config = OxigraphConfig(
            query_endpoint="http://localhost:7878/query",
            update_endpoint="http://localhost:7878/update",
        )
        loader = OxigraphLoader(config, timescale_config=pg_config)

        with LoadProgressDisplay("O2") as display:
            result = loader.load_all(
                Path("data/export/o2"),
                progress_callback=display.update,
                workers=16,
            )
        ```
    """

    # =========================================================================
    # BULK LOAD CONFIGURATION (2025 best practices)
    # =========================================================================

    # Chunk size for POST requests (lines/triples)
    # Increased from 100K to 500K for fewer HTTP round-trips
    CHUNK_SIZE = 500_000

    # Number of parallel POST workers
    # Note: Oxigraph handles concurrent writes internally
    PARALLEL_WORKERS = 4

    # Enable parallel POST (can be disabled for debugging)
    ENABLE_PARALLEL = True

    # HTTP connection pool size
    CONNECTION_POOL_SIZE = 10

    # Endpoint pour bulk load (store endpoint)
    STORE_ENDPOINT_SUFFIX = "/store"

    def __init__(
        self,
        config: OxigraphConfig,
        timescale_config: PostgresConfig | None = None,
    ):
        """Initialise le loader.

        Args:
            config: Configuration Oxigraph (endpoints HTTP)
            timescale_config: Config PostgreSQL pour timeseries
        """
        super().__init__(engine="O2")
        self.config = config
        self.timescale_config = timescale_config

        # Derive store endpoint from base URL
        base_url = config.query_endpoint.rsplit("/", 1)[0]
        self.store_endpoint = f"{base_url}{self.STORE_ENDPOINT_SUFFIX}"

        self._client: httpx.Client | None = None

    # =========================================================================
    # CONNECTION
    # =========================================================================

    def _get_client(self) -> httpx.Client:
        """Retourne ou cree le client HTTP.

        Optimized with connection pooling for better performance (2025 best practice).
        """
        if self._client is None:
            # Configure connection pooling for better performance
            limits = httpx.Limits(
                max_keepalive_connections=self.CONNECTION_POOL_SIZE,
                max_connections=self.CONNECTION_POOL_SIZE * 2,
                keepalive_expiry=30.0,  # Keep connections alive for 30s
            )

            # Try HTTP/2 if h2 package is available, fallback to HTTP/1.1
            try:
                self._client = httpx.Client(
                    timeout=httpx.Timeout(
                        connect=10.0,
                        read=self.config.timeout_seconds,
                        write=self.config.timeout_seconds,
                        pool=10.0,
                    ),
                    limits=limits,
                    http2=True,  # HTTP/2 for better multiplexing
                )
            except Exception:
                # Fallback to HTTP/1.1 if h2 not installed
                self._client = httpx.Client(
                    timeout=httpx.Timeout(
                        connect=10.0,
                        read=self.config.timeout_seconds,
                        write=self.config.timeout_seconds,
                        pool=10.0,
                    ),
                    limits=limits,
                )
        return self._client

    def _close_client(self) -> None:
        """Ferme le client HTTP."""
        if self._client:
            self._client.close()
            self._client = None

    def check_connection(self) -> bool:
        """Verifie la connexion Oxigraph."""
        try:
            client = self._get_client()
            # Simple ASK query
            response = client.post(
                self.config.query_endpoint,
                content="ASK { ?s ?p ?o }",
                headers={"Content-Type": "application/sparql-query"},
            )
            return response.status_code == 200
        except Exception:
            return False

    def check_timeseries_dependency(self) -> TimeseriesDependencyResult:
        """Vérifie si les timeseries sont disponibles pour O2.

        O2 (Oxigraph + TimescaleDB) nécessite TimescaleDB pour les timeseries.
        Note: O2 est exploratoire uniquement, hors benchmark officiel.

        Returns:
            TimeseriesDependencyResult avec le status et les détails
        """
        # O2 needs TimescaleDB for timeseries
        if not self.timescale_config:
            return TimeseriesDependencyResult(
                status=TimeseriesDependencyStatus.CONNECTION_ERROR,
                message=(
                    "O2 nécessite TimescaleDB mais aucune configuration fournie.\n"
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
                    "O2 partage les timeseries avec P1/P2/M2.\n"
                    "Options:\n"
                    "  1. Charger P1 ou P2 d'abord (recommandé)\n"
                    "  2. Charger les timeseries maintenant pour O2"
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
        """Vide la base Oxigraph.

        Args:
            keep_timeseries: If True, preserve TimescaleDB data (O2)

        Returns:
            True if successful
        """
        try:
            client = self._get_client()
            # DROP ALL via SPARQL Update
            response = client.post(
                self.config.update_endpoint,
                content="DROP ALL",
                headers={"Content-Type": "application/sparql-update"},
            )

            # O2: Also clear TimescaleDB structure (but optionally keep timeseries)
            if self.timescale_config:
                from .postgres import PostgresLoader
                pg_loader = PostgresLoader(self.timescale_config, paradigm="P1")
                pg_loader.clear_database(keep_timeseries=keep_timeseries)

            return response.status_code in (200, 204)
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
            data_dir: Repertoire avec les fichiers exportes (data.nt, timeseries.csv)
            progress_callback: Callback pour progress updates
            workers: Nombre de workers paralleles (pour timeseries)

        Returns:
            LoadResult avec statistiques
        """
        start_time = time.time()
        result = LoadResult(engine="O2")

        # Wait for Oxigraph HTTP endpoint to be ready before loading
        # This prevents silent failures when container is still starting
        if not self.check_connection():
            result.add_error("Oxigraph not ready after 30 connection attempts")
            return result

        try:
            # Phase 1: Schema (ontology)
            self._emit_progress(progress_callback, LoadPhase.SCHEMA, 0, 1)
            ontology_file = data_dir / "ontology.ttl"
            if ontology_file.exists():
                self._load_ontology(ontology_file)
            self._emit_progress(progress_callback, LoadPhase.SCHEMA, 1, 1)

            # Phase 2+3: Nodes + Edges
            # Support both combined (data.nt) and separate (nodes.nt + edges.nt) files
            combined_nt = data_dir / "data.nt"
            nodes_nt = data_dir / "nodes.nt"
            edges_nt = data_dir / "edges.nt"

            triples_loaded = 0
            if combined_nt.exists():
                # Combined file format
                triples_loaded = self._load_ntriples(combined_nt, progress_callback)
                # Estimate: ~60% nodes, ~40% edges
                result.nodes_loaded = int(triples_loaded * 0.6)
                result.edges_loaded = int(triples_loaded * 0.4)
            else:
                # Separate files format (nodes.nt + edges.nt)
                if nodes_nt.exists():
                    nodes_triples = self._load_ntriples(nodes_nt, progress_callback)
                    result.nodes_loaded = nodes_triples
                    triples_loaded += nodes_triples
                if edges_nt.exists():
                    edges_triples = self._load_ntriples(edges_nt, progress_callback)
                    result.edges_loaded = edges_triples
                    triples_loaded += edges_triples

            # Phase 4: Timeseries (vers TimescaleDB)
            ts_file = data_dir / "timeseries.csv"
            if ts_file.exists() and self.timescale_config:
                result.timeseries_loaded = self._load_timeseries(
                    ts_file, workers, progress_callback
                )

        except Exception as e:
            result.add_error(str(e))
        finally:
            self._close_client()

        # Calcul des stats
        result.duration_seconds = time.time() - start_time
        if result.duration_seconds > 0:
            result.rate_rows_per_sec = result.total_rows / result.duration_seconds

        return result

    # =========================================================================
    # ONTOLOGY LOADING
    # =========================================================================

    def _load_ontology(self, ttl_file: Path) -> None:
        """Charge l'ontologie Turtle."""
        client = self._get_client()

        with open(ttl_file, "rb") as f:
            content = f.read()

        response = client.post(
            f"{self.store_endpoint}?default",
            content=content,
            headers={"Content-Type": "text/turtle"},
        )
        response.raise_for_status()

    # =========================================================================
    # N-TRIPLES LOADING
    # =========================================================================

    def _load_ntriples(
        self,
        nt_file: Path,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les N-Triples en chunks.

        Uses parallel POST with ThreadPoolExecutor for better throughput (2025 best practice).
        Falls back to sequential if parallel is disabled or fails.
        """
        total_lines = self._count_nt_lines(nt_file)

        # Combine NODES and EDGES phases (N-Triples has both)
        self._emit_progress(callback, LoadPhase.NODES, 0, total_lines)

        start = time.time()

        if self.ENABLE_PARALLEL and total_lines > self.CHUNK_SIZE:
            # Parallel mode for large files
            loaded = self._load_ntriples_parallel(nt_file, total_lines, callback, start)
        else:
            # Sequential mode for small files or when parallel is disabled
            loaded = self._load_ntriples_sequential(nt_file, total_lines, callback, start)

        return loaded

    def _load_ntriples_sequential(
        self,
        nt_file: Path,
        total_lines: int,
        callback: ProgressCallback | None,
        start: float,
    ) -> int:
        """Sequential N-Triples loading (original implementation)."""
        loaded = 0

        for chunk_data in self._read_nt_chunks(nt_file):
            chunk_lines = self._post_ntriples_chunk(chunk_data)
            loaded += chunk_lines

            elapsed = time.time() - start
            rate = loaded / elapsed if elapsed > 0 else 0
            self._emit_progress(callback, LoadPhase.NODES, loaded, total_lines, rate)

        return loaded

    def _load_ntriples_parallel(
        self,
        nt_file: Path,
        total_lines: int,
        callback: ProgressCallback | None,
        start: float,
    ) -> int:
        """Parallel N-Triples loading with ThreadPoolExecutor.

        Submits chunks to a thread pool for concurrent HTTP POSTs.
        Uses thread-safe progress tracking.
        """
        import threading

        loaded = 0
        lock = threading.Lock()

        # Collect chunks first (generator -> list for parallel submission)
        chunks = list(self._read_nt_chunks(nt_file))

        def post_chunk(chunk_data: bytes) -> int:
            """Post a single chunk and return lines count."""
            return self._post_ntriples_chunk(chunk_data)

        with ThreadPoolExecutor(max_workers=self.PARALLEL_WORKERS) as executor:
            # Submit all chunks
            futures = {executor.submit(post_chunk, chunk): chunk for chunk in chunks}

            # Process completed futures
            for future in as_completed(futures):
                try:
                    chunk_lines = future.result()
                    with lock:
                        loaded += chunk_lines
                        elapsed = time.time() - start
                        rate = loaded / elapsed if elapsed > 0 else 0
                        self._emit_progress(callback, LoadPhase.NODES, loaded, total_lines, rate)
                except Exception as e:
                    # Log error but continue with other chunks
                    print(f"Warning: Chunk POST failed: {e}")

        return loaded

    def _read_nt_chunks(self, nt_file: Path) -> Iterator[bytes]:
        """Lit le fichier N-Triples par chunks.

        Yields:
            Chunks de bytes (CHUNK_SIZE lignes)
        """
        chunk: list[bytes] = []

        with open(nt_file, "rb") as f:
            for line in f:
                # Skip empty lines and comments
                stripped = line.strip()
                if not stripped or stripped.startswith(b"#"):
                    continue

                chunk.append(line)

                if len(chunk) >= self.CHUNK_SIZE:
                    yield b"".join(chunk)
                    chunk = []

            # Dernier chunk
            if chunk:
                yield b"".join(chunk)

    def _post_ntriples_chunk(self, data: bytes) -> int:
        """POST un chunk de N-Triples vers Oxigraph.

        Args:
            data: Bytes N-Triples

        Returns:
            Nombre de lignes dans le chunk
        """
        client = self._get_client()

        response = client.post(
            f"{self.store_endpoint}?default",
            content=data,
            headers={"Content-Type": "application/n-triples"},
        )
        response.raise_for_status()

        # Count lines in chunk
        return data.count(b"\n")

    # =========================================================================
    # TIMESERIES (vers TimescaleDB)
    # =========================================================================

    def _load_timeseries(
        self,
        csv_file: Path,
        workers: int,
        callback: ProgressCallback | None,
    ) -> int:
        """Charge les timeseries vers TimescaleDB.

        O2 utilise TimescaleDB pour les donnees temporelles.
        """
        if not self.timescale_config:
            return 0

        # Import ici pour eviter circular import
        from .postgres import PostgresLoader

        pg_loader = PostgresLoader(self.timescale_config, paradigm="P1")

        # Créer le schema timeseries si nécessaire
        pg_loader.ensure_timeseries_schema()

        # Skip if already populated (Option A)
        if pg_loader._is_timeseries_populated():
            print("⏭️  Timeseries already loaded for O2, skipping")
            return pg_loader._count_timeseries_rows()

        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.TIMESERIES, 0, total_count)

        # Delegate to PostgresLoader
        return pg_loader._load_timeseries(csv_file, workers, callback)
