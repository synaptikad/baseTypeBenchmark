"""Gestionnaire de datasets avec export direct sur disque.

Le workflow pour les benchmarks est:
1. generate_and_export() -> génère et écrit directement les CSV/JSON sur disque
2. Les benchmarks chargent depuis ces fichiers (I/O disque réaliste)

Pas de cache pickle - cela fausserait les benchmarks.

IMPORTANT: Pour les gros datasets (large-1y = ~550GB), on utilise le mode streaming:
- Le graphe (nodes/edges) est généré en RAM (~quelques GB) puis écrit
- Les timeseries sont générées par chunks (~16GB) et écrites immédiatement
- Cela évite d'exploser la RAM
"""
from __future__ import annotations

import csv
import gc
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, List

from basetype_benchmark.dataset.config import (
    ALIASES, DEFAULT_SEED, get_profile, SIZE_ESTIMATES_GB, TIMESERIES_RATIO
)
from basetype_benchmark.dataset.export_graph import export_property_graph
from basetype_benchmark.dataset.export_pg import export_postgres
from basetype_benchmark.dataset.export_rdf import export_rdf
from basetype_benchmark.dataset.generator import (
    Dataset, Summary, generate_dataset, generate_graph_only,
    _get_sampling_frequency, _generate_values
)
from basetype_benchmark.dataset.model import TimeseriesChunk, Node, TIMESERIES_QUANTITIES


class DatasetManager:
    """Gestionnaire de datasets avec export direct sur disque."""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.export_dir = self.base_dir / "exports"
        self.export_dir.mkdir(exist_ok=True)

    def _estimate_size_gb(self, profile) -> float:
        """Estime la taille du dataset en GB."""
        estimates = {
            ("small", 2): 0.5, ("small", 7): 1, ("small", 30): 5, ("small", 180): 27, ("small", 365): 55,
            ("medium", 2): 1, ("medium", 7): 2, ("medium", 30): 10, ("medium", 180): 54, ("medium", 365): 110,
            ("large", 2): 5, ("large", 7): 11, ("large", 30): 45, ("large", 180): 270, ("large", 365): 550,
        }
        if profile.points <= 60000:
            scale = "small"
        elif profile.points <= 150000:
            scale = "medium"
        else:
            scale = "large"
        return estimates.get((scale, profile.duration_days), profile.points * profile.duration_days / 1e7)

    def generate_and_export(self, profile_name: str, seed: int = DEFAULT_SEED,
                            formats: list = None) -> Tuple[Path, Summary]:
        """Génère un dataset et l'exporte directement sur disque.

        Pour les gros datasets (>10 GB estimés), utilise le mode STREAMING:
        - Génère le graphe en RAM (quelques GB max)
        - Génère les timeseries par chunks et écrit immédiatement
        - Affiche une progression réelle

        Args:
            profile_name: Nom du profil (ex: 'small-1w', 'medium-1m')
            seed: Graine pour reproductibilité
            formats: Liste des formats d'export ['postgres', 'graph', 'rdf']
                    Par défaut: tous les formats

        Returns:
            Tuple (chemin_export, summary)
        """
        import time as time_module
        from random import Random

        if formats is None:
            formats = ['postgres', 'graph', 'rdf']

        # Résoudre l'alias
        resolved_profile = ALIASES.get(profile_name, profile_name)
        profile = get_profile(resolved_profile)
        estimated_size = self._estimate_size_gb(profile)

        # Créer le répertoire d'export
        export_subdir = self.export_dir / f"{resolved_profile}_seed{seed}"
        export_subdir.mkdir(exist_ok=True)

        print(f"[i] Generating dataset {profile_name}")
        print(f"    Scale: {profile.points:,} points, {profile.floors} floors, {profile.spaces} spaces")
        print(f"    Duration: {profile.duration_days} days of timeseries")
        print(f"    Estimated size: ~{estimated_size:.1f} GB")
        print(f"    Output: {export_subdir}")

        # Décider du mode: streaming si > 10 GB estimés
        use_streaming = estimated_size > 10
        if use_streaming:
            print(f"    Mode: STREAMING (dataset trop gros pour RAM)")
        else:
            print(f"    Mode: Standard (RAM)")
        print()

        start_time = time_module.time()

        if use_streaming:
            return self._generate_streaming(
                profile, seed, export_subdir, formats, estimated_size, start_time
            )
        else:
            return self._generate_standard(
                profile, seed, export_subdir, formats, start_time
            )

    def _generate_standard(self, profile, seed: int, export_subdir: Path,
                          formats: list, start_time: float) -> Tuple[Path, Summary]:
        """Génération standard: tout en RAM puis export."""
        import time as time_module

        # Phase 1: Générer le dataset en RAM
        print(f"    [1/2] Generating data...", end=" ", flush=True)
        dataset, summary = generate_dataset(profile, seed)
        gen_time = time_module.time() - start_time
        print(f"done ({gen_time:.1f}s)")

        print(f"          - Nodes: {summary.node_count:,}")
        print(f"          - Edges: {summary.edge_count:,}")
        print(f"          - Timeseries points: {len(dataset.timeseries):,}")
        print()

        # Phase 2: Exporter directement sur disque
        print(f"    [2/2] Exporting to disk...")

        if 'postgres' in formats:
            print(f"          - PostgreSQL CSV...", end=" ", flush=True)
            export_postgres(dataset, export_subdir)
            print("done")

        if 'graph' in formats:
            print(f"          - Property Graph JSON...", end=" ", flush=True)
            export_property_graph(dataset, export_subdir)
            print("done")

        if 'rdf' in formats:
            print(f"          - RDF JSON-LD...", end=" ", flush=True)
            export_rdf(dataset, export_subdir)
            print("done")

        total_time = time_module.time() - start_time
        total_size_mb = sum(f.stat().st_size for f in export_subdir.rglob('*') if f.is_file()) / (1024*1024)

        print()
        print(f"[OK] Dataset exported in {total_time:.1f}s ({total_size_mb:.1f} MB on disk)")
        print(f"     Location: {export_subdir}")

        return export_subdir, summary

    def _generate_streaming(self, profile, seed: int, export_subdir: Path,
                           formats: list, estimated_size: float,
                           start_time: float) -> Tuple[Path, Summary]:
        """Génération streaming: graphe en RAM, timeseries par chunks sur disque.

        Cette méthode permet de générer des datasets de plusieurs centaines de GB
        sans exploser la RAM.
        """
        import time as time_module
        from random import Random

        rng = Random(seed)

        # =====================================================================
        # PHASE 1: Générer le graphe (nodes + edges) - tient en RAM
        # =====================================================================
        print(f"    [1/4] Generating graph structure...")
        graph_start = time_module.time()

        graph_data, summary, ts_point_info = generate_graph_only(profile, seed)
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        measures = graph_data['measures']

        graph_time = time_module.time() - graph_start
        print(f"          Done in {graph_time:.1f}s")
        print(f"          - Nodes: {summary.node_count:,}")
        print(f"          - Edges: {summary.edge_count:,}")
        print(f"          - Points for timeseries: {len(ts_point_info):,}")
        print()

        # =====================================================================
        # PHASE 2: Exporter le graphe sur disque
        # =====================================================================
        print(f"    [2/4] Exporting graph to disk...")
        export_start = time_module.time()

        # Export nodes
        if 'postgres' in formats:
            self._export_nodes_csv(nodes, export_subdir)
            self._export_edges_csv(edges, measures, export_subdir)
            print(f"          - PostgreSQL CSV (nodes, edges): done")

        if 'graph' in formats:
            self._export_nodes_json(nodes, export_subdir)
            self._export_edges_json(edges, measures, export_subdir)
            print(f"          - Property Graph JSON (nodes, edges): done")

        if 'rdf' in formats:
            self._export_graph_rdf(nodes, edges, measures, export_subdir)
            print(f"          - RDF JSON-LD (graph): done")

        # Libérer la mémoire du graphe
        del nodes, edges, graph_data
        gc.collect()

        export_time = time_module.time() - export_start
        print(f"          Done in {export_time:.1f}s")
        print()

        # =====================================================================
        # PHASE 3: Générer et exporter les timeseries par CHUNKS
        # =====================================================================
        print(f"    [3/4] Generating timeseries (streaming)...")
        ts_start = time_module.time()

        # Calculer le nombre de points par chunk pour ~2GB de données
        # Environ 70 bytes par sample JSON, on veut ~2GB par chunk
        samples_per_point = (profile.duration_days * 24 * 60) // 15  # Moyenne 15min
        bytes_per_point = samples_per_point * 70
        chunk_target_bytes = 2 * 1024 * 1024 * 1024  # 2 GB
        points_per_chunk = max(100, chunk_target_bytes // max(1, bytes_per_point))

        total_points = len(ts_point_info)
        num_chunks = (total_points + points_per_chunk - 1) // points_per_chunk
        total_samples = 0

        print(f"          - {total_points:,} points in {num_chunks} chunks (~{points_per_chunk:,} points/chunk)")

        # Ouvrir les fichiers en mode append pour les timeseries
        ts_csv_path = export_subdir / "timeseries.csv"
        ts_chunks_path = export_subdir / "timeseries_chunks.json"

        # Écrire les headers
        with open(ts_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["time", "point_id", "value"])

        # Clear le fichier chunks
        ts_chunks_path.write_text("")

        for chunk_idx in range(num_chunks):
            chunk_start = chunk_idx * points_per_chunk
            chunk_end = min(chunk_start + points_per_chunk, total_points)
            chunk_points = ts_point_info[chunk_start:chunk_end]

            # Générer les timeseries pour ce chunk
            chunk_timeseries = self._generate_timeseries_chunk(
                chunk_points, profile, seed + chunk_idx, rng
            )

            # Écrire immédiatement sur disque
            chunk_samples = 0
            if 'postgres' in formats:
                chunk_samples = self._append_timeseries_csv(chunk_timeseries, ts_csv_path)

            if 'graph' in formats:
                self._append_timeseries_chunks_json(chunk_timeseries, ts_chunks_path)

            total_samples += chunk_samples

            # Libérer la mémoire
            del chunk_timeseries
            gc.collect()

            # Afficher la progression
            progress_pct = (chunk_idx + 1) / num_chunks * 100
            elapsed = time_module.time() - ts_start
            rate = total_samples / elapsed if elapsed > 0 else 0
            size_so_far = total_samples * 70 / (1024 * 1024 * 1024)  # GB estimé

            print(f"\r          - Chunk {chunk_idx + 1}/{num_chunks} "
                  f"({progress_pct:.0f}%) - {size_so_far:.1f}/{estimated_size:.0f} GB "
                  f"- {rate/1e6:.1f}M samples/s", end="", flush=True)

        ts_time = time_module.time() - ts_start
        print(f"\n          Done in {ts_time:.1f}s - {total_samples:,} samples total")
        print()

        # Mettre à jour le summary avec le nombre de samples
        summary.timeseries_samples = total_samples

        # =====================================================================
        # PHASE 4: Finalisation
        # =====================================================================
        print(f"    [4/4] Finalizing...")

        total_time = time_module.time() - start_time
        total_size_mb = sum(f.stat().st_size for f in export_subdir.rglob('*') if f.is_file()) / (1024*1024)

        print()
        print(f"[OK] Dataset exported in {total_time:.1f}s ({total_size_mb/1024:.1f} GB on disk)")
        print(f"     Location: {export_subdir}")

        return export_subdir, summary

    def _generate_timeseries_chunk(self, point_info: List[Tuple[Node, str]],
                                   profile, seed: int, rng) -> List[TimeseriesChunk]:
        """Génère les timeseries pour un chunk de points.

        Seuls les points avec mesures continues (fréquence > 0) sont générés.
        Les événements rares (alarmes, états, accès) sont ignorés.
        """
        from datetime import datetime, timedelta

        timeseries = []
        start_time = int((datetime.now() - timedelta(days=profile.duration_days)).timestamp())
        end_time = int(datetime.now().timestamp())

        for point, quantity in point_info:
            if not quantity:
                continue

            frequency_minutes = _get_sampling_frequency(quantity)

            # Skip event-based quantities (frequency = 0)
            if frequency_minutes == 0:
                continue

            values = _generate_values(quantity, profile.duration_days, frequency_minutes, rng)

            chunk = TimeseriesChunk(
                point_id=point.id,
                start_time=start_time,
                end_time=end_time,
                frequency_seconds=frequency_minutes * 60,
                values=values
            )
            timeseries.append(chunk)

        return timeseries

    def _export_nodes_csv(self, nodes: List[Node], out_dir: Path) -> None:
        """Export nodes en CSV PostgreSQL."""
        nodes_path = out_dir / "nodes.csv"
        with nodes_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "type", "name", "building_id", "data"])
            for node in nodes:
                building_id = node.properties.get("building_id", 0)
                data = json.dumps(node.properties)
                writer.writerow([node.id, node.type.value, node.name, building_id, data])

    def _export_edges_csv(self, edges, measures, out_dir: Path) -> None:
        """Export edges en CSV PostgreSQL."""
        edges_path = out_dir / "edges.csv"
        with edges_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["src_id", "dst_id", "rel_type"])
            for edge in edges:
                writer.writerow([edge.src, edge.dst, edge.rel.value])
            for measure in measures:
                writer.writerow([measure.src, measure.quantity, "MEASURES"])

    def _export_nodes_json(self, nodes: List[Node], out_dir: Path) -> None:
        """Export nodes en JSON lines."""
        nodes_path = out_dir / "nodes.json"
        with nodes_path.open("w", encoding="utf-8") as f:
            for node in nodes:
                json.dump({
                    "id": node.id,
                    "type": node.type.value,
                    "name": node.name,
                    "building_id": node.properties.get("building_id", 0),
                    "properties": node.properties
                }, f)
                f.write("\n")

    def _export_edges_json(self, edges, measures, out_dir: Path) -> None:
        """Export edges en JSON lines."""
        edges_path = out_dir / "edges.json"
        with edges_path.open("w", encoding="utf-8") as f:
            for edge in edges:
                json.dump({"src": edge.src, "dst": edge.dst, "rel": edge.rel.value}, f)
                f.write("\n")
            for measure in measures:
                json.dump({"src": measure.src, "dst": measure.quantity, "rel": "MEASURES"}, f)
                f.write("\n")

    def _export_graph_rdf(self, nodes, edges, measures, out_dir: Path) -> None:
        """Export graphe en RDF JSON-LD (sans timeseries)."""
        from basetype_benchmark.dataset.model import RelationType

        predicate_map = {
            "CONTAINS": "contains", "LOCATED_IN": "locatedIn", "HAS_PART": "hasPart",
            "HAS_POINT": "hasPoint", "CONTROLS": "controls", "FEEDS": "feeds",
            "SERVES": "serves", "OCCUPIES": "occupies",
        }

        graph = {node.id: {"id": node.id, "type": node.type.value, "name": node.name} for node in nodes}

        for edge in edges:
            pred = predicate_map.get(edge.rel.value)
            if pred and edge.src in graph:
                graph[edge.src].setdefault(pred, []).append({"id": edge.dst})

        for measure in measures:
            if measure.src in graph:
                graph[measure.src].setdefault("measures", []).append({"@value": measure.quantity})

        context = {
            "@base": "http://example.org/id/",
            "id": "@id", "type": "@type",
            "name": "http://example.org/name",
            "contains": "http://example.org/CONTAINS",
            "locatedIn": "http://example.org/LOCATED_IN",
            "hasPart": "http://example.org/HAS_PART",
            "hasPoint": "http://example.org/HAS_POINT",
            "controls": "http://example.org/CONTROLS",
            "feeds": "http://example.org/FEEDS",
            "serves": "http://example.org/SERVES",
            "occupies": "http://example.org/OCCUPIES",
            "measures": "http://example.org/MEASURES",
        }

        data = {"@context": context, "@graph": list(graph.values())}
        out_path = out_dir / "graph.jsonld"
        out_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def _append_timeseries_csv(self, timeseries: List[TimeseriesChunk], csv_path: Path) -> int:
        """Append timeseries au fichier CSV (mode streaming)."""
        total_samples = 0
        with csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for chunk in timeseries:
                current_time = chunk.start_time
                for value in chunk.values:
                    ts = datetime.fromtimestamp(current_time, tz=timezone.utc).isoformat()
                    writer.writerow([ts, chunk.point_id, value])
                    current_time += chunk.frequency_seconds
                    total_samples += 1
        return total_samples

    def _append_timeseries_chunks_json(self, timeseries: List[TimeseriesChunk], json_path: Path) -> None:
        """Append timeseries chunks au fichier JSON (mode streaming)."""
        with json_path.open("a", encoding="utf-8") as f:
            for chunk in timeseries:
                chunk_node = {
                    "id": f"chunk_{chunk.point_id}_{chunk.start_time}",
                    "type": "TimeseriesChunk",
                    "point_id": chunk.point_id,
                    "start_time": chunk.start_time,
                    "end_time": chunk.end_time,
                    "frequency_seconds": chunk.frequency_seconds,
                    "values": chunk.values
                }
                json.dump(chunk_node, f)
                f.write("\n")

                chunk_edge = {
                    "src": chunk.point_id,
                    "dst": f"chunk_{chunk.point_id}_{chunk.start_time}",
                    "rel": "HAS_CHUNK"
                }
                json.dump(chunk_edge, f)
                f.write("\n")

    def is_exported(self, profile_name: str, seed: int = DEFAULT_SEED) -> bool:
        """Vérifie si un dataset a déjà été exporté sur disque."""
        resolved_profile = ALIASES.get(profile_name, profile_name)
        export_subdir = self.export_dir / f"{resolved_profile}_seed{seed}"
        return export_subdir.exists() and any(export_subdir.glob("*.csv"))

    def get_export_path(self, profile_name: str, seed: int = DEFAULT_SEED) -> Path:
        """Retourne le chemin d'export pour un profil."""
        resolved_profile = ALIASES.get(profile_name, profile_name)
        return self.export_dir / f"{resolved_profile}_seed{seed}"

    def list_exported_datasets(self) -> list:
        """Liste les datasets exportés sur disque."""
        if not self.export_dir.exists():
            return []

        datasets = []
        for subdir in self.export_dir.iterdir():
            if subdir.is_dir() and any(subdir.glob("*.csv")):
                size_mb = sum(f.stat().st_size for f in subdir.rglob('*') if f.is_file()) / (1024*1024)
                datasets.append({
                    'name': subdir.name,
                    'path': subdir,
                    'size_mb': size_mb,
                })

        return sorted(datasets, key=lambda x: x['name'])

    def delete_export(self, profile_name: str, seed: int = DEFAULT_SEED) -> bool:
        """Supprime un dataset exporté."""
        export_path = self.get_export_path(profile_name, seed)
        if export_path.exists():
            shutil.rmtree(export_path)
            return True
        return False

    def get_export_info(self, profile_name: str, seed: int = DEFAULT_SEED) -> Optional[dict]:
        """Informations sur un dataset exporté."""
        if not self.is_exported(profile_name, seed):
            return None

        export_path = self.get_export_path(profile_name, seed)
        resolved_profile = ALIASES.get(profile_name, profile_name)
        profile = get_profile(resolved_profile)

        size_mb = sum(f.stat().st_size for f in export_path.rglob('*') if f.is_file()) / (1024*1024)

        return {
            'profile': resolved_profile,
            'export_path': export_path,
            'size_mb': size_mb,
            'points': profile.points,
            'duration_days': profile.duration_days,
            'seed': seed
        }


def main():
    """Interface en ligne de commande."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python dataset_manager.py <command> [args...]")
        print()
        print("Commands:")
        print("  generate <profile> [seed]         - Génère et exporte un dataset")
        print("  list                              - Liste les datasets exportés")
        print("  info <profile> [seed]             - Infos sur un dataset")
        print("  delete <profile> [seed]           - Supprime un dataset")
        print()
        print("Profiles disponibles: small-1w, small-1m, ..., large-1y")
        print("Alias: laptop, desktop, server, cluster")
        return

    manager = DatasetManager()
    command = sys.argv[1]

    if command == 'generate':
        profile = sys.argv[2]
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_SEED
        export_path, summary = manager.generate_and_export(profile, seed)
        print(f"[OK] Dataset: {summary.node_count} nodes, {summary.edge_count} edges")

    elif command == 'list':
        datasets = manager.list_exported_datasets()
        if not datasets:
            print("No datasets exported")
        else:
            print(f"Exported datasets ({len(datasets)}):")
            for ds in datasets:
                print(f"  {ds['name']}: {ds['size_mb']:.1f} MB")

    elif command == 'info':
        profile = sys.argv[2]
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_SEED
        info = manager.get_export_info(profile, seed)
        if info:
            print(f"Profile: {info['profile']}")
            print(f"Points: {info['points']:,}")
            print(f"Duration: {info['duration_days']} days")
            print(f"Seed: {info['seed']}")
            print(f"Size: {info['size_mb']:.1f} MB")
            print(f"Path: {info['export_path']}")
        else:
            print(f"Dataset {profile} not found")

    elif command == 'delete':
        profile = sys.argv[2]
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_SEED
        if manager.delete_export(profile, seed):
            print(f"[OK] Deleted {profile}")
        else:
            print(f"Dataset {profile} not found")


if __name__ == "__main__":
    main()
