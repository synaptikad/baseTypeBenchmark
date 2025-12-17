"""Gestionnaire de datasets avec export direct sur disque.

Le workflow pour les benchmarks est:
1. generate_and_export() -> génère et écrit directement les CSV/JSON sur disque
2. Les benchmarks chargent depuis ces fichiers (I/O disque réaliste)

Pas de cache pickle - cela fausserait les benchmarks.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional, Tuple

from basetype_benchmark.dataset.config import ALIASES, DEFAULT_SEED, get_profile, SIZE_ESTIMATES_GB
from basetype_benchmark.dataset.export_graph import export_property_graph
from basetype_benchmark.dataset.export_pg import export_postgres
from basetype_benchmark.dataset.export_rdf import export_rdf
from basetype_benchmark.dataset.generator import Dataset, Summary, generate_dataset


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

        Args:
            profile_name: Nom du profil (ex: 'small-1w', 'medium-1m')
            seed: Graine pour reproductibilité
            formats: Liste des formats d'export ['postgres', 'graph', 'rdf']
                    Par défaut: ['postgres']

        Returns:
            Tuple (chemin_export, summary)
        """
        import time as time_module

        if formats is None:
            formats = ['postgres']

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
        print()

        start_time = time_module.time()

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
        export_start = time_module.time()

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

        # Calculer la taille sur disque
        total_size_mb = sum(f.stat().st_size for f in export_subdir.rglob('*') if f.is_file()) / (1024*1024)

        print()
        print(f"[OK] Dataset exported in {total_time:.1f}s ({total_size_mb:.1f} MB on disk)")
        print(f"     Location: {export_subdir}")

        return export_subdir, summary

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
