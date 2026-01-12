"""
Base Extractor - Benchmark BaseType V3
Infrastructure commune pour l'extraction vers tous les paradigmes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Callable
from datetime import datetime
import csv
import json
import sys

# Dataclasses partagées pour la génération de données
from basetype_benchmark.dataset.models import Node, Edge, TimeseriesPoint


# =============================================================================
# EXPORT PROGRESS TYPES
# =============================================================================

class ExportPhase(Enum):
    """Phases d'export."""
    LOADING = "loading"
    NODES = "nodes"
    EDGES = "edges"
    TIMESERIES = "timeseries"


@dataclass
class ExportProgress:
    """Progress update pour l'export."""
    phase: ExportPhase
    current: int
    total: int
    rate: float = 0.0
    message: str = ""

    @property
    def percent(self) -> float:
        """Pourcentage de completion."""
        if self.total <= 0:
            return 0.0
        return (self.current / self.total) * 100.0

    @property
    def is_complete(self) -> bool:
        """Vrai si la phase est terminée."""
        return self.current >= self.total


# Type alias pour le callback
ExportProgressCallback = Callable[[ExportProgress], None]


class ParquetDataset:
    """Dataset chargé depuis des fichiers Parquet générés."""

    def __init__(self, input_dir: Path):
        self.input_dir = Path(input_dir)
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.timeseries: List[TimeseriesPoint] = []
        self._load()

    def _load(self):
        """Charge les données depuis les fichiers Parquet."""
        try:
            import pyarrow.parquet as pq
        except ImportError:
            raise ImportError("pyarrow required to load Parquet files")

        # Load nodes
        nodes_file = self.input_dir / "nodes.parquet"
        if nodes_file.exists():
            table = pq.read_table(nodes_file)
            for row in table.to_pylist():
                self.nodes.append(Node(
                    id=row['id'],
                    type=row['type'],
                    name=row['name'],
                    properties=json.loads(row.get('properties', '{}')),
                    capabilities=json.loads(row.get('capabilities', '[]')),
                    metadata=json.loads(row.get('metadata', '{}')),
                    tags=json.loads(row.get('tags', '[]')),
                    protocol=json.loads(row.get('protocol', '{}')),
                    calibration=json.loads(row.get('calibration', '{}')),
                    range_info=json.loads(row.get('range', '{}'))
                ))

        # Load edges
        edges_file = self.input_dir / "edges.parquet"
        if edges_file.exists():
            table = pq.read_table(edges_file)
            for row in table.to_pylist():
                self.edges.append(Edge(
                    source_id=row['source_id'],
                    target_id=row['target_id'],
                    rel_type=row['rel_type'],
                    properties=json.loads(row.get('properties', '{}'))
                ))

        # Load timeseries
        ts_file = self.input_dir / "timeseries.parquet"
        if ts_file.exists():
            table = pq.read_table(ts_file)
            for row in table.to_pylist():
                self.timeseries.append(TimeseriesPoint(
                    point_id=row['point_id'],
                    timestamp=datetime.fromisoformat(row['time']),
                    value=float(row['value'])
                ))


@dataclass
class ExportResult:
    """Résultat d'une extraction"""
    paradigm: str
    files_created: List[Path]
    total_nodes: int
    total_edges: int
    total_timeseries: int
    load_commands: List[str]


class BaseExtractor(ABC):
    """
    Classe abstraite pour les extracteurs.

    Chaque paradigme implémente:
    - extract_nodes() : transformation des nœuds
    - extract_edges() : transformation des relations
    - extract_timeseries() : transformation des séries temporelles
    - get_load_commands() : commandes de chargement bulk
    """

    def __init__(self, output_dir: Path, input_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.input_dir = Path(input_dir) if input_dir else None
        self.dataset = None

    @property
    @abstractmethod
    def paradigm_name(self) -> str:
        """Nom du paradigme (p1, p2, m1, m2, o2)"""
        pass

    def load_dataset(self):
        """Charge le dataset depuis Parquet.

        Raises:
            FileNotFoundError: Si le répertoire Parquet n'existe pas
        """
        if not self.input_dir:
            raise FileNotFoundError("input_dir is required - use generator to create Parquet dataset")

        nodes_file = self.input_dir / "nodes.parquet"
        if not nodes_file.exists():
            raise FileNotFoundError(f"Parquet dataset not found at {self.input_dir}")

        self.dataset = ParquetDataset(self.input_dir)
        return self.dataset

    @abstractmethod
    def extract_nodes(self) -> List[Path]:
        """Extrait les nœuds vers le format cible"""
        pass

    @abstractmethod
    def extract_edges(self) -> List[Path]:
        """Extrait les relations vers le format cible"""
        pass

    @abstractmethod
    def extract_timeseries(self) -> List[Path]:
        """Extrait les timeseries vers le format cible"""
        pass

    @abstractmethod
    def get_load_commands(self) -> List[str]:
        """Retourne les commandes de chargement bulk"""
        pass

    @abstractmethod
    def get_schema_commands(self) -> List[str]:
        """Retourne les commandes de création de schema"""
        pass

    def _emit_progress(
        self,
        callback: Optional[ExportProgressCallback],
        phase: ExportPhase,
        current: int,
        total: int,
        rate: float = 0.0,
        message: str = "",
    ) -> None:
        """Émet un update de progression si callback fourni."""
        if callback:
            callback(ExportProgress(
                phase=phase,
                current=current,
                total=total,
                rate=rate,
                message=message,
            ))

    def export_all(
        self,
        progress_callback: Optional[ExportProgressCallback] = None,
    ) -> ExportResult:
        """Export complet vers le paradigme cible.

        Args:
            progress_callback: Callback optionnel pour les updates de progression.

        Returns:
            ExportResult avec les statistiques d'export.
        """
        import time

        # Phase 1: Loading Parquet
        self._emit_progress(progress_callback, ExportPhase.LOADING, 0, 1, message="Loading Parquet...")
        if not self.dataset:
            self.load_dataset()
        self._emit_progress(progress_callback, ExportPhase.LOADING, 1, 1, message="Parquet loaded")

        files = []

        # Phase 2: Nodes
        total_nodes = len(self.dataset.nodes)
        self._emit_progress(progress_callback, ExportPhase.NODES, 0, total_nodes, message="Exporting nodes...")
        start = time.perf_counter()
        files.extend(self.extract_nodes())
        elapsed = time.perf_counter() - start
        rate = total_nodes / elapsed if elapsed > 0 else 0
        self._emit_progress(progress_callback, ExportPhase.NODES, total_nodes, total_nodes, rate=rate)

        # Phase 3: Edges
        total_edges = len(self.dataset.edges)
        self._emit_progress(progress_callback, ExportPhase.EDGES, 0, total_edges, message="Exporting edges...")
        start = time.perf_counter()
        files.extend(self.extract_edges())
        elapsed = time.perf_counter() - start
        rate = total_edges / elapsed if elapsed > 0 else 0
        self._emit_progress(progress_callback, ExportPhase.EDGES, total_edges, total_edges, rate=rate)

        # Phase 4: Timeseries
        total_ts = len(self.dataset.timeseries)
        self._emit_progress(progress_callback, ExportPhase.TIMESERIES, 0, total_ts, message="Exporting timeseries...")
        start = time.perf_counter()
        files.extend(self.extract_timeseries())
        elapsed = time.perf_counter() - start
        rate = total_ts / elapsed if elapsed > 0 else 0
        self._emit_progress(progress_callback, ExportPhase.TIMESERIES, total_ts, total_ts, rate=rate)

        # Copy queries_params.yaml if exists
        if self.input_dir:
            params_file = self.input_dir / "queries_params.yaml"
            if params_file.exists():
                import shutil
                dest_file = self.output_dir / "queries_params.yaml"
                shutil.copy(params_file, dest_file)
                files.append(dest_file)

        return ExportResult(
            paradigm=self.paradigm_name,
            files_created=files,
            total_nodes=len(self.dataset.nodes),
            total_edges=len(self.dataset.edges),
            total_timeseries=len(self.dataset.timeseries),
            load_commands=self.get_load_commands()
        )


# ===========================================================================
# HELPERS POUR TRANSFORMATION DES DONNÉES
# ===========================================================================

def flatten_jsonb(node: Node) -> Dict[str, Any]:
    """
    Aplatit les champs JSONB d'un nœud pour M1/M2.

    Exemple:
        metadata: {warranty_end: "2025-01-01"}
        → metadata_warranty_end: "2025-01-01"
    """
    flat = {
        "id": node.id,
        "node_type": node.type,
        "name": node.name,
    }

    # Properties de base
    for key, value in node.properties.items():
        flat[key] = value

    # Listes natives (capabilities, tags)
    if node.capabilities:
        flat["capabilities"] = node.capabilities  # Liste native Cypher
    if node.tags:
        flat["tags"] = node.tags  # Liste native Cypher

    # Aplatissement metadata.*
    for key, value in node.metadata.items():
        flat[f"metadata_{key}"] = value

    # Aplatissement protocol.*
    for key, value in node.protocol.items():
        flat[f"protocol_{key}"] = value

    # Aplatissement calibration.*
    for key, value in node.calibration.items():
        flat[f"calibration_{key}"] = value

    # Aplatissement range.*
    for key, value in node.range_info.items():
        flat[f"range_{key}"] = value

    return flat


def merge_to_jsonb(node: Node) -> Dict[str, Any]:
    """
    Fusionne tous les champs d'un nœud en un seul document JSONB pour P2.
    """
    data = dict(node.properties)

    if node.capabilities:
        data["capabilities"] = node.capabilities
    if node.metadata:
        data["metadata"] = node.metadata
    if node.tags:
        data["tags"] = node.tags
    if node.protocol:
        data["protocol"] = node.protocol
    if node.calibration:
        data["calibration"] = node.calibration
    if node.range_info:
        data["range"] = node.range_info

    return data


def node_to_relational(node: Node, node_type: str) -> Dict[str, Any]:
    """
    Extrait les propriétés relationnelles d'un nœud pour P1.
    Les champs JSONB sont ignorés (IMPOSSIBLE pour P1).
    """
    base = {
        "id": node.id,
        "name": node.name,
    }

    # Ajouter les properties relationnelles
    for key, value in node.properties.items():
        # Ignorer les objets complexes (gps_coords)
        if not isinstance(value, dict):
            base[key] = value

    return base


# ===========================================================================
# HELPERS CSV
# ===========================================================================

def write_csv(filepath: Path, rows: List[Dict], fieldnames: List[str] = None):
    """Écrit un fichier CSV avec les lignes données"""
    if not rows:
        return

    if fieldnames is None:
        # Collecter tous les champs de toutes les lignes
        all_fields = set()
        for row in rows:
            all_fields.update(row.keys())
        fieldnames = sorted(all_fields)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def escape_csv_value(value: Any) -> str:
    """Escape une valeur pour CSV"""
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    print("Base Extractor - Infrastructure commune")
    print("Ce module ne s'exécute pas directement.")
    print("Utilisez les extracteurs spécifiques: p1, p2, m1m2, o2")
