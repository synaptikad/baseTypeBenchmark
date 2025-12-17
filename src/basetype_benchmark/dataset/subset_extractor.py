"""Extraction de sous-ensembles depuis un dataset master.

Ce module permet d'extraire des sous-ensembles (scale + fenetre temporelle)
depuis un dataset plus grand, evitant de regenerer les donnees.

Exemple: depuis large-1y, on peut extraire:
- small-2d, small-1w, small-1m, small-6m, small-1y
- medium-2d, medium-1w, medium-1m, medium-6m, medium-1y
- large-2d, large-1w, large-1m, large-6m

Hierarchie:
- Scale: large > medium > small (nombre de buildings/floors)
- Duration: 1y > 6m > 1m > 1w > 2d (jours de timeseries)
"""
from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from basetype_benchmark.dataset.config import PROFILES, get_profile


# Hierarchies pour extraction
SCALE_ORDER = {"small": 0, "medium": 1, "large": 2}
DURATION_ORDER = {"2d": 0, "1w": 1, "1m": 2, "6m": 3, "1y": 4}
DURATION_DAYS = {"2d": 2, "1w": 7, "1m": 30, "6m": 180, "1y": 365}


def parse_profile(profile_name: str) -> Tuple[str, str]:
    """Parse un nom de profil en (scale, duration)."""
    parts = profile_name.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid profile name: {profile_name}")
    return parts[0], parts[1]


def can_extract(source_profile: str, target_profile: str) -> bool:
    """Verifie si target peut etre extrait de source.

    Args:
        source_profile: Profil source (ex: 'large-1y')
        target_profile: Profil cible (ex: 'small-1m')

    Returns:
        True si extraction possible
    """
    try:
        src_scale, src_duration = parse_profile(source_profile)
        tgt_scale, tgt_duration = parse_profile(target_profile)
    except ValueError:
        return False

    src_scale_idx = SCALE_ORDER.get(src_scale, -1)
    tgt_scale_idx = SCALE_ORDER.get(tgt_scale, -1)
    src_duration_idx = DURATION_ORDER.get(src_duration, -1)
    tgt_duration_idx = DURATION_ORDER.get(tgt_duration, -1)

    # Source doit etre >= target sur les deux axes
    return src_scale_idx >= tgt_scale_idx and src_duration_idx >= tgt_duration_idx


def get_extractable_profiles(source_profile: str) -> List[str]:
    """Liste tous les profils extractibles depuis source.

    Args:
        source_profile: Profil source (ex: 'large-1y')

    Returns:
        Liste des profils extractibles (excluant source lui-meme)
    """
    try:
        src_scale, src_duration = parse_profile(source_profile)
    except ValueError:
        return []

    src_scale_idx = SCALE_ORDER.get(src_scale, -1)
    src_duration_idx = DURATION_ORDER.get(src_duration, -1)

    extractable = []
    for scale, scale_idx in SCALE_ORDER.items():
        if scale_idx <= src_scale_idx:
            for duration, duration_idx in DURATION_ORDER.items():
                if duration_idx <= src_duration_idx:
                    profile = f"{scale}-{duration}"
                    if profile != source_profile:
                        extractable.append(profile)

    return sorted(extractable)


def get_available_scales(source_profile: str) -> List[str]:
    """Liste les scales disponibles depuis source."""
    src_scale, _ = parse_profile(source_profile)
    src_scale_idx = SCALE_ORDER.get(src_scale, -1)
    return [s for s, idx in SCALE_ORDER.items() if idx <= src_scale_idx]


def get_available_durations(source_profile: str) -> List[str]:
    """Liste les durations disponibles depuis source."""
    _, src_duration = parse_profile(source_profile)
    src_duration_idx = DURATION_ORDER.get(src_duration, -1)
    return [d for d, idx in DURATION_ORDER.items() if idx <= src_duration_idx]


class SubsetExtractor:
    """Extracteur de sous-ensembles depuis un dataset master."""

    def __init__(self, source_dir: Path):
        """
        Args:
            source_dir: Repertoire du dataset source (ex: exports/large-1y_seed42)
        """
        self.source_dir = Path(source_dir)
        if not self.source_dir.exists():
            raise ValueError(f"Source directory not found: {source_dir}")

        # Detecter le profil source depuis le nom du repertoire
        self.source_name = self.source_dir.name  # ex: "large-1y_seed42"
        parts = self.source_name.rsplit("_seed", 1)
        self.source_profile = parts[0]  # ex: "large-1y"
        self.seed = int(parts[1]) if len(parts) > 1 else 42

        self.source_scale, self.source_duration = parse_profile(self.source_profile)
        self.source_config = get_profile(self.source_profile)

    def extract(self, target_profile: str, output_dir: Path = None) -> Path:
        """Extrait un sous-ensemble vers un nouveau repertoire.

        Args:
            target_profile: Profil cible (ex: 'small-1m')
            output_dir: Repertoire de sortie (defaut: meme parent que source)

        Returns:
            Path du repertoire cree
        """
        if not can_extract(self.source_profile, target_profile):
            raise ValueError(
                f"Cannot extract {target_profile} from {self.source_profile}. "
                f"Source must be >= target on both scale and duration."
            )

        target_scale, target_duration = parse_profile(target_profile)
        target_config = get_profile(target_profile)

        # Repertoire de sortie
        if output_dir is None:
            output_dir = self.source_dir.parent / f"{target_profile}_seed{self.seed}"
        output_dir = Path(output_dir)

        # Si deja existe et complet, skip
        if output_dir.exists() and self._is_complete(output_dir):
            print(f"[i] {target_profile} already extracted at {output_dir}")
            return output_dir

        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"[i] Extracting {target_profile} from {self.source_profile}")
        print(f"    Scale: {self.source_scale} -> {target_scale}")
        print(f"    Duration: {self.source_duration} -> {target_duration}")

        # Calculer les filtres
        max_building_id = self._get_max_building_id(target_scale)
        max_days = DURATION_DAYS[target_duration]

        print(f"    Filters: building_id <= {max_building_id}, duration <= {max_days} days")

        # Extraire chaque format
        stats = {}

        # CSV (PostgreSQL)
        if (self.source_dir / "nodes.csv").exists():
            stats["csv"] = self._extract_csv(output_dir, max_building_id, max_days)

        # JSON (Property Graph)
        if (self.source_dir / "nodes.json").exists():
            stats["json"] = self._extract_json(output_dir, max_building_id, max_days)

        # JSON-LD (RDF)
        if (self.source_dir / "graph.jsonld").exists():
            stats["jsonld"] = self._extract_jsonld(output_dir, max_building_id, max_days)

        # Timeseries chunks
        if (self.source_dir / "timeseries_chunks.json").exists():
            stats["chunks"] = self._extract_chunks(output_dir, max_building_id, max_days)

        # Calculer taille
        total_size_mb = sum(
            f.stat().st_size for f in output_dir.rglob('*') if f.is_file()
        ) / (1024 * 1024)

        print(f"[OK] Extracted {target_profile}: {total_size_mb:.1f} MB")
        print(f"     Stats: {stats}")

        return output_dir

    def _get_max_building_id(self, target_scale: str) -> int:
        """Retourne le building_id max pour un scale donne.

        La logique: le dataset est genere avec building_id de 0 a N-1.
        - small: 1 building (id 0)
        - medium: 2 buildings (id 0-1)
        - large: 4 buildings (id 0-3)
        """
        scale_buildings = {"small": 1, "medium": 2, "large": 4}
        return scale_buildings.get(target_scale, 1) - 1

    def _is_complete(self, output_dir: Path) -> bool:
        """Verifie si l'extraction est complete."""
        # Au minimum nodes.csv ou nodes.json
        has_csv = (output_dir / "nodes.csv").exists()
        has_json = (output_dir / "nodes.json").exists()
        return has_csv or has_json

    def _extract_csv(self, output_dir: Path, max_building_id: int, max_days: int) -> Dict:
        """Extrait les fichiers CSV."""
        stats = {"nodes": 0, "edges": 0, "timeseries": 0}

        # Nodes: filtrer par building_id
        nodes_file = self.source_dir / "nodes.csv"
        if nodes_file.exists():
            kept_node_ids = set()
            with open(nodes_file, 'r', encoding='utf-8') as src, \
                 open(output_dir / "nodes.csv", 'w', encoding='utf-8', newline='') as dst:
                reader = csv.DictReader(src)
                writer = None
                for row in reader:
                    building_id = int(row.get('building_id', 0) or 0)
                    if building_id <= max_building_id:
                        if writer is None:
                            writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
                            writer.writeheader()
                        writer.writerow(row)
                        kept_node_ids.add(row['id'])
                        stats["nodes"] += 1

        # Edges: filtrer par src/dst dans kept_node_ids
        edges_file = self.source_dir / "edges.csv"
        if edges_file.exists() and kept_node_ids:
            with open(edges_file, 'r', encoding='utf-8') as src, \
                 open(output_dir / "edges.csv", 'w', encoding='utf-8', newline='') as dst:
                reader = csv.DictReader(src)
                writer = None
                for row in reader:
                    if row['src_id'] in kept_node_ids and row['dst_id'] in kept_node_ids:
                        if writer is None:
                            writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
                            writer.writeheader()
                        writer.writerow(row)
                        stats["edges"] += 1

        # Timeseries: filtrer par point_id et date
        ts_file = self.source_dir / "timeseries.csv"
        if ts_file.exists() and kept_node_ids:
            cutoff_date = self._get_cutoff_date(max_days)
            with open(ts_file, 'r', encoding='utf-8') as src, \
                 open(output_dir / "timeseries.csv", 'w', encoding='utf-8', newline='') as dst:
                reader = csv.DictReader(src)
                writer = None
                for row in reader:
                    if row['point_id'] in kept_node_ids:
                        # Filtrer par date
                        ts_date = self._parse_timestamp(row['time'])
                        if ts_date and ts_date >= cutoff_date:
                            if writer is None:
                                writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
                                writer.writeheader()
                            writer.writerow(row)
                            stats["timeseries"] += 1

        return stats

    def _extract_json(self, output_dir: Path, max_building_id: int, max_days: int) -> Dict:
        """Extrait les fichiers JSON (property graph)."""
        stats = {"nodes": 0, "edges": 0}

        # Nodes
        nodes_file = self.source_dir / "nodes.json"
        if nodes_file.exists():
            kept_node_ids = set()
            with open(nodes_file, 'r', encoding='utf-8') as src, \
                 open(output_dir / "nodes.json", 'w', encoding='utf-8') as dst:
                for line in src:
                    line = line.strip()
                    if not line:
                        continue
                    node = json.loads(line)
                    building_id = node.get('building_id', 0) or 0
                    if building_id <= max_building_id:
                        dst.write(json.dumps(node) + '\n')
                        kept_node_ids.add(node['id'])
                        stats["nodes"] += 1

        # Edges
        edges_file = self.source_dir / "edges.json"
        if edges_file.exists() and kept_node_ids:
            with open(edges_file, 'r', encoding='utf-8') as src, \
                 open(output_dir / "edges.json", 'w', encoding='utf-8') as dst:
                for line in src:
                    line = line.strip()
                    if not line:
                        continue
                    edge = json.loads(line)
                    if edge['src'] in kept_node_ids and edge['dst'] in kept_node_ids:
                        dst.write(json.dumps(edge) + '\n')
                        stats["edges"] += 1

        return stats

    def _extract_chunks(self, output_dir: Path, max_building_id: int, max_days: int) -> Dict:
        """Extrait les chunks de timeseries."""
        stats = {"chunks": 0, "edges": 0}

        # D'abord, lire les node_ids valides depuis nodes.json ou nodes.csv
        kept_node_ids = self._get_kept_node_ids(output_dir)
        if not kept_node_ids:
            return stats

        chunks_file = self.source_dir / "timeseries_chunks.json"
        if not chunks_file.exists():
            return stats

        cutoff_timestamp = self._get_cutoff_timestamp(max_days)

        with open(chunks_file, 'r', encoding='utf-8') as src, \
             open(output_dir / "timeseries_chunks.json", 'w', encoding='utf-8') as dst:
            for line in src:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)

                if obj.get('type') == 'TimeseriesChunk':
                    # Chunk node: filtrer par point_id et end_time
                    point_id = obj.get('point_id', '')
                    if point_id in kept_node_ids:
                        end_time = obj.get('end_time', 0)
                        if end_time >= cutoff_timestamp:
                            # Filtrer les valeurs si necessaire
                            start_time = obj.get('start_time', 0)
                            if start_time < cutoff_timestamp:
                                # Tronquer le debut du chunk
                                obj = self._truncate_chunk(obj, cutoff_timestamp)
                            dst.write(json.dumps(obj) + '\n')
                            stats["chunks"] += 1

                elif obj.get('rel') == 'HAS_CHUNK':
                    # Edge HAS_CHUNK: filtrer par src (point_id)
                    if obj['src'] in kept_node_ids:
                        dst.write(json.dumps(obj) + '\n')
                        stats["edges"] += 1

        return stats

    def _extract_jsonld(self, output_dir: Path, max_building_id: int, max_days: int) -> Dict:
        """Extrait le fichier JSON-LD (RDF)."""
        stats = {"triples": 0}

        jsonld_file = self.source_dir / "graph.jsonld"
        if not jsonld_file.exists():
            return stats

        # JSON-LD est plus complexe - pour l'instant, copie complete si small scale
        # TODO: Implementer filtrage RDF propre
        if max_building_id == 0:
            # Small scale - filtrage necessaire
            # Pour l'instant, on ne copie pas le JSON-LD pour les extractions
            return stats
        else:
            # Copie complete
            shutil.copy(jsonld_file, output_dir / "graph.jsonld")
            stats["triples"] = -1  # Indique copie complete

        return stats

    def _get_kept_node_ids(self, output_dir: Path) -> Set[str]:
        """Recupere les IDs des nodes gardes depuis les fichiers extraits."""
        kept_ids = set()

        # Essayer JSON d'abord
        nodes_json = output_dir / "nodes.json"
        if nodes_json.exists():
            with open(nodes_json, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        node = json.loads(line)
                        kept_ids.add(node['id'])
            return kept_ids

        # Sinon CSV
        nodes_csv = output_dir / "nodes.csv"
        if nodes_csv.exists():
            with open(nodes_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    kept_ids.add(row['id'])

        return kept_ids

    def _get_cutoff_date(self, max_days: int) -> datetime:
        """Calcule la date de coupure pour les timeseries."""
        # Les donnees sont generees jusqu'a "maintenant", on garde les N derniers jours
        return datetime.now() - timedelta(days=max_days)

    def _get_cutoff_timestamp(self, max_days: int) -> int:
        """Calcule le timestamp de coupure pour les chunks."""
        cutoff = datetime.now() - timedelta(days=max_days)
        return int(cutoff.timestamp())

    def _parse_timestamp(self, ts_str: str) -> Optional[datetime]:
        """Parse un timestamp string en datetime."""
        try:
            # Format ISO
            return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    def _truncate_chunk(self, chunk: Dict, cutoff_timestamp: int) -> Dict:
        """Tronque un chunk pour ne garder que les valeurs apres cutoff."""
        start_time = chunk.get('start_time', 0)
        frequency = chunk.get('frequency_seconds', 60)
        values = chunk.get('values', [])

        if not values or frequency <= 0:
            return chunk

        # Calculer l'index de debut
        time_diff = cutoff_timestamp - start_time
        start_idx = max(0, int(time_diff / frequency))

        if start_idx >= len(values):
            # Tout le chunk est avant la coupure
            return {**chunk, 'values': []}

        # Tronquer
        new_values = values[start_idx:]
        new_start_time = start_time + (start_idx * frequency)

        return {
            **chunk,
            'start_time': new_start_time,
            'values': new_values
        }


def extract_subset(source_dir: Path, target_profile: str, output_dir: Path = None) -> Path:
    """Fonction utilitaire pour extraire un sous-ensemble.

    Args:
        source_dir: Repertoire du dataset source
        target_profile: Profil cible (ex: 'small-1m')
        output_dir: Repertoire de sortie (optionnel)

    Returns:
        Path du repertoire cree
    """
    extractor = SubsetExtractor(source_dir)
    return extractor.extract(target_profile, output_dir)


def main():
    """CLI pour extraction de sous-ensembles."""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python subset_extractor.py <source_dir> <target_profile> [output_dir]")
        print()
        print("Example:")
        print("  python subset_extractor.py exports/large-1y_seed42 small-1m")
        print()
        print("This will extract small-1m from large-1y dataset")
        return

    source_dir = Path(sys.argv[1])
    target_profile = sys.argv[2]
    output_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    try:
        result_path = extract_subset(source_dir, target_profile, output_dir)
        print(f"[OK] Extracted to: {result_path}")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
