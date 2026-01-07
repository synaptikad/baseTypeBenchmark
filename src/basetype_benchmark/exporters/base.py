"""
Base Extractor - Benchmark BaseType V3
Infrastructure commune pour l'extraction vers tous les paradigmes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple
import csv
import json
import sys

# Ajouter le chemin pour importer golden
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.basetype_benchmark.dataset.golden import GoldenDataset, Node, Edge, TimeseriesPoint


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

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dataset: GoldenDataset = None

    @property
    @abstractmethod
    def paradigm_name(self) -> str:
        """Nom du paradigme (p1, p2, m1, m2, o2)"""
        pass

    def load_dataset(self) -> GoldenDataset:
        """Charge le golden dataset"""
        self.dataset = GoldenDataset()
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

    def export_all(self) -> ExportResult:
        """Export complet vers le paradigme cible"""
        if not self.dataset:
            self.load_dataset()

        files = []
        files.extend(self.extract_nodes())
        files.extend(self.extract_edges())
        files.extend(self.extract_timeseries())

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
