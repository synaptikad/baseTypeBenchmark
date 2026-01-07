"""Oxigraph Bulk Loader for O2 (+ TimescaleDB).

Sprint 2 - Benchmark BaseType V3

Strategies de chargement:
1. Chunked HTTP POST pour N-Triples (100K lignes par requete)
2. Streaming pour eviter OOM
3. Timeseries vers TimescaleDB via PostgresLoader

Optimisations:
- N-Triples est le format le plus rapide pour bulk RDF
- Chunking evite les timeouts et OOM
- Streaming lecture fichier
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Literal

import httpx

from ..config import OxigraphConfig, PostgresConfig
from .base import BaseLoader, LoadPhase, LoadResult, ProgressCallback

if TYPE_CHECKING:
    pass


class OxigraphLoader(BaseLoader):
    """Loader pour Oxigraph O2 (+ TimescaleDB pour timeseries).

    Supporte:
    - O2: RDF graph en Oxigraph + timeseries dans TimescaleDB

    Optimisations:
    - Chunked HTTP POST (100K triples par requete)
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

    # Taille des chunks pour POST (lignes)
    CHUNK_SIZE = 100_000

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
        """Retourne ou cree le client HTTP."""
        if self._client is None:
            self._client = httpx.Client(
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=self.config.timeout_seconds,
                    write=self.config.timeout_seconds,
                    pool=10.0,
                )
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

    # =========================================================================
    # PUBLIC INTERFACE
    # =========================================================================

    def clear_database(self) -> bool:
        """Vide la base Oxigraph."""
        try:
            client = self._get_client()
            # DROP ALL via SPARQL Update
            response = client.post(
                self.config.update_endpoint,
                content="DROP ALL",
                headers={"Content-Type": "application/sparql-update"},
            )
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

        try:
            # Phase 1: Schema (ontology)
            self._emit_progress(progress_callback, LoadPhase.SCHEMA, 0, 1)
            ontology_file = data_dir / "ontology.ttl"
            if ontology_file.exists():
                self._load_ontology(ontology_file)
            self._emit_progress(progress_callback, LoadPhase.SCHEMA, 1, 1)

            # Phase 2+3: Nodes + Edges (combined in data.nt)
            nt_file = data_dir / "data.nt"
            if nt_file.exists():
                triples_loaded = self._load_ntriples(
                    nt_file, progress_callback
                )
                # N-Triples combines nodes and edges
                # Estimate: ~60% nodes, ~40% edges
                result.nodes_loaded = int(triples_loaded * 0.6)
                result.edges_loaded = int(triples_loaded * 0.4)

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
            self.store_endpoint,
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
        """Charge les N-Triples en chunks."""
        total_lines = self._count_nt_lines(nt_file)

        # Combine NODES and EDGES phases (N-Triples has both)
        self._emit_progress(callback, LoadPhase.NODES, 0, total_lines)

        start = time.time()
        loaded = 0

        for chunk_data in self._read_nt_chunks(nt_file):
            chunk_lines = self._post_ntriples_chunk(chunk_data)
            loaded += chunk_lines

            elapsed = time.time() - start
            rate = loaded / elapsed if elapsed > 0 else 0
            self._emit_progress(callback, LoadPhase.NODES, loaded, total_lines, rate)

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
            self.store_endpoint,
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

        total_count = self._count_csv_rows(csv_file)
        self._emit_progress(callback, LoadPhase.TIMESERIES, 0, total_count)

        # Delegate to PostgresLoader
        return pg_loader._load_timeseries(csv_file, workers, callback)
