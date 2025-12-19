"""Gestionnaire de datasets avec export direct sur disque.

Le workflow pour les benchmarks est:
1. generate_and_export() -> génère via generator_v2 et exporte via exporter_v2
2. Les benchmarks chargent depuis ces fichiers (I/O disque réaliste)

Version 2.0 - Utilise le nouveau générateur basé sur docs/Exploration
et produit les 6 formats de sortie (P1, P2, M1, M2, O1, O2).
"""
from __future__ import annotations

import gc
import json
import shutil
import time as time_module
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from .config import ALIASES, DEFAULT_SEED
from .generator_v2 import DatasetGeneratorV2, Dataset, generate_timeseries
from . import exporter_v2


# =============================================================================
# CONFIGURATION
# =============================================================================

# Répertoire de configuration
CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "config"

# Répertoire Exploration pour les définitions d'équipements
EXPLORATION_DIR = Path(__file__).parent.parent.parent.parent / "docs" / "Exploration"

# Durées disponibles
DURATIONS = {
    "2d": 2,
    "1w": 7,
    "1m": 30,
    "6m": 180,
    "1y": 365,
}

# Estimations de taille (GB) pour scale+duration
SIZE_ESTIMATES_GB = {
    ("small", 2): 0.5, ("small", 7): 1, ("small", 30): 5, ("small", 180): 27, ("small", 365): 55,
    ("medium", 2): 1, ("medium", 7): 2, ("medium", 30): 10, ("medium", 180): 54, ("medium", 365): 110,
    ("large", 2): 5, ("large", 7): 11, ("large", 30): 45, ("large", 180): 270, ("large", 365): 550,
}

# Seuil pour mode streaming (GB)
STREAMING_THRESHOLD_GB = 5


class DatasetManager:
    """Gestionnaire de datasets avec export direct sur disque."""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.export_dir = self.base_dir / "exports"
        self.export_dir.mkdir(exist_ok=True)

    def _parse_profile(self, profile_name: str) -> Tuple[str, int]:
        """Parse le nom de profil pour extraire scale et duration_days.

        Args:
            profile_name: Nom du profil (ex: 'small-1w', 'medium-1m')

        Returns:
            Tuple (scale, duration_days)
        """
        resolved = ALIASES.get(profile_name, profile_name)
        parts = resolved.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid profile name: {profile_name}. Expected format: scale-duration (e.g., small-1w)")

        scale = parts[0]
        duration_key = parts[1]

        if scale not in ("small", "medium", "large"):
            raise ValueError(f"Invalid scale: {scale}. Expected: small, medium, large")

        if duration_key not in DURATIONS:
            raise ValueError(f"Invalid duration: {duration_key}. Expected: {list(DURATIONS.keys())}")

        return scale, DURATIONS[duration_key]

    def _estimate_size_gb(self, scale: str, duration_days: int) -> float:
        """Estime la taille du dataset en GB."""
        return SIZE_ESTIMATES_GB.get((scale, duration_days), 10.0)

    def generate_and_export(
        self,
        profile_name: str,
        seed: int = DEFAULT_SEED,
        formats: list = None
    ) -> Tuple[Path, Dict[str, Any], Dict[str, Any]]:
        """Génère un dataset et l'exporte directement sur disque.

        Workflow V2:
        1. Génère le graphe avec generator_v2 (depuis Exploration + YAML)
        2. Exporte vers Parquet (format pivot)
        3. Exporte vers les 6 formats cibles (P1, P2, M1, M2, O1, O2)
        4. Calcule le fingerprint pour validation

        Pour les gros datasets (>5 GB), utilise le mode streaming.

        Args:
            profile_name: Nom du profil (ex: 'small-1w', 'medium-1m')
            seed: Graine pour reproductibilité
            formats: Liste des formats d'export (None = tous)
                    Options: 'parquet', 'postgresql', 'postgresql_jsonb',
                             'memgraph', 'memgraph_m1', 'oxigraph', 'oxigraph_o1'

        Returns:
            Tuple (chemin_export, summary_dict, fingerprint_dict)
        """
        if formats is None:
            formats = ['parquet', 'postgresql', 'postgresql_jsonb',
                      'memgraph', 'memgraph_m1', 'oxigraph', 'oxigraph_o1']

        # Parser le profil
        scale, duration_days = self._parse_profile(profile_name)
        resolved_profile = ALIASES.get(profile_name, profile_name)
        estimated_size = self._estimate_size_gb(scale, duration_days)

        # Créer le répertoire d'export
        export_subdir = self.export_dir / f"{resolved_profile}_seed{seed}"
        if export_subdir.exists():
            shutil.rmtree(export_subdir)
        export_subdir.mkdir(parents=True)

        print(f"[i] Generating dataset {profile_name} (v2)")
        print(f"    Scale: {scale}")
        print(f"    Duration: {duration_days} days")
        print(f"    Estimated size: ~{estimated_size:.1f} GB")
        print(f"    Output: {export_subdir}")

        # Mode streaming pour gros datasets
        use_streaming = estimated_size >= STREAMING_THRESHOLD_GB
        if use_streaming:
            print(f"    Mode: STREAMING (dataset > {STREAMING_THRESHOLD_GB} GB)")
        else:
            print(f"    Mode: Standard (RAM)")
        print()

        start_time = time_module.time()

        # =====================================================================
        # PHASE 1: Générer le graphe avec generator_v2
        # =====================================================================
        print(f"    [1/3] Generating graph structure...")
        graph_start = time_module.time()

        generator = DatasetGeneratorV2(
            profile_name=scale,
            config_path=CONFIG_DIR,
            exploration_path=EXPLORATION_DIR if EXPLORATION_DIR.exists() else None,
            seed=seed
        )
        dataset = generator.generate()

        graph_time = time_module.time() - graph_start
        print(f"          Done in {graph_time:.1f}s")
        print(f"          - Nodes: {len(dataset.nodes):,}")
        print(f"          - Edges: {len(dataset.edges):,}")
        print(f"          - Points: {len(dataset.points):,}")
        print()

        # =====================================================================
        # PHASE 2: Exporter vers Parquet (format pivot)
        # =====================================================================
        print(f"    [2/3] Exporting to Parquet pivot...")
        parquet_start = time_module.time()

        parquet_dir = export_subdir / "parquet"

        if use_streaming:
            exporter_v2.export_parquet_streaming(
                dataset, parquet_dir, duration_days=duration_days
            )
        else:
            exporter_v2.export_parquet(
                dataset, parquet_dir, duration_days=duration_days
            )

        parquet_time = time_module.time() - parquet_start
        print(f"          Done in {parquet_time:.1f}s")
        print()

        # =====================================================================
        # PHASE 3: Exporter vers les formats cibles
        # =====================================================================
        print(f"    [3/3] Exporting to target formats...")
        export_start = time_module.time()

        target_mapping = {
            'postgresql': ('postgresql', 'P1'),
            'postgresql_jsonb': ('postgresql_jsonb', 'P2'),
            'memgraph': ('memgraph', 'M2'),
            'memgraph_m1': ('memgraph_m1', 'M1'),
            'oxigraph': ('oxigraph', 'O2'),
            'oxigraph_o1': ('oxigraph_o1', 'O1'),
        }

        for fmt in formats:
            if fmt == 'parquet':
                continue  # Already done

            if fmt not in target_mapping:
                print(f"          - {fmt}: skipped (unknown)")
                continue

            target, scenario = target_mapping[fmt]
            output_dir = export_subdir / scenario.lower()

            try:
                print(f"          - {scenario} ({target})...", end=" ", flush=True)
                exporter_v2.export_for_target(parquet_dir, target, output_dir)
                print("done")
            except Exception as e:
                print(f"failed: {e}")

        export_time = time_module.time() - export_start
        print(f"          Done in {export_time:.1f}s")
        print()

        # =====================================================================
        # FINALISATION
        # =====================================================================

        # Libérer la mémoire
        del dataset
        gc.collect()

        # Calculer le fingerprint
        fingerprint = exporter_v2.compute_fingerprint(parquet_dir)
        fingerprint["profile"] = resolved_profile
        fingerprint["seed"] = seed
        fingerprint["duration_days"] = duration_days
        exporter_v2.save_fingerprint(fingerprint, export_subdir)

        total_time = time_module.time() - start_time
        total_size_mb = sum(
            f.stat().st_size for f in export_subdir.rglob('*') if f.is_file()
        ) / (1024 * 1024)

        # Summary
        summary = {
            "profile": resolved_profile,
            "scale": scale,
            "duration_days": duration_days,
            "seed": seed,
            "node_count": fingerprint["counts"]["nodes"],
            "edge_count": fingerprint["counts"]["edges"],
            "timeseries_count": fingerprint["counts"].get("timeseries", 0),
            "node_types": fingerprint["counts"]["node_types"],
            "edge_types": fingerprint["counts"]["edge_types"],
            "generation_time_s": total_time,
            "size_mb": total_size_mb,
        }

        print(f"[OK] Dataset exported in {total_time:.1f}s ({total_size_mb:.1f} MB on disk)")
        print(f"     Location: {export_subdir}")
        print(f"     Fingerprint: {fingerprint['struct_hash'][:8]}...{fingerprint.get('ts_hash', 'N/A')[:8] if fingerprint.get('ts_hash') else 'N/A'}")

        return export_subdir, summary, fingerprint

    def is_exported(self, profile_name: str, seed: int = DEFAULT_SEED) -> bool:
        """Vérifie si un dataset a déjà été exporté sur disque."""
        resolved_profile = ALIASES.get(profile_name, profile_name)
        export_subdir = self.export_dir / f"{resolved_profile}_seed{seed}"
        # Vérifie la présence du fingerprint comme indicateur de complétion
        return (export_subdir / "fingerprint.json").exists()

    def get_export_path(self, profile_name: str, seed: int = DEFAULT_SEED) -> Path:
        """Retourne le chemin d'export pour un profil."""
        resolved_profile = ALIASES.get(profile_name, profile_name)
        return self.export_dir / f"{resolved_profile}_seed{seed}"

    def get_scenario_path(
        self,
        profile_name: str,
        scenario: str,
        seed: int = DEFAULT_SEED
    ) -> Path:
        """Retourne le chemin d'export pour un scénario spécifique.

        Args:
            profile_name: Nom du profil (ex: 'small-1w')
            scenario: Code scénario (P1, P2, M1, M2, O1, O2)
            seed: Graine

        Returns:
            Path vers le répertoire du scénario
        """
        export_path = self.get_export_path(profile_name, seed)
        return export_path / scenario.lower()

    def list_exported_datasets(self) -> list:
        """Liste les datasets exportés sur disque."""
        if not self.export_dir.exists():
            return []

        datasets = []
        for subdir in self.export_dir.iterdir():
            if subdir.is_dir():
                fingerprint_path = subdir / "fingerprint.json"
                if fingerprint_path.exists():
                    with open(fingerprint_path) as f:
                        fp = json.load(f)

                    size_mb = sum(
                        f.stat().st_size for f in subdir.rglob('*') if f.is_file()
                    ) / (1024 * 1024)

                    datasets.append({
                        'name': subdir.name,
                        'path': subdir,
                        'size_mb': size_mb,
                        'profile': fp.get('profile', subdir.name),
                        'seed': fp.get('seed', 42),
                        'nodes': fp['counts']['nodes'],
                        'edges': fp['counts']['edges'],
                        'timeseries': fp['counts'].get('timeseries', 0),
                        'fingerprint': fp['struct_hash'][:8],
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
        fingerprint_path = export_path / "fingerprint.json"

        with open(fingerprint_path) as f:
            fp = json.load(f)

        size_mb = sum(
            f.stat().st_size for f in export_path.rglob('*') if f.is_file()
        ) / (1024 * 1024)

        # Lister les scénarios disponibles
        scenarios = []
        for scenario in ['p1', 'p2', 'm1', 'm2', 'o1', 'o2']:
            if (export_path / scenario).exists():
                scenarios.append(scenario.upper())

        return {
            'profile': fp.get('profile', profile_name),
            'export_path': export_path,
            'size_mb': size_mb,
            'nodes': fp['counts']['nodes'],
            'edges': fp['counts']['edges'],
            'timeseries': fp['counts'].get('timeseries', 0),
            'duration_days': fp.get('duration_days'),
            'seed': fp.get('seed', seed),
            'fingerprint': fp['struct_hash'],
            'scenarios': scenarios,
        }

    def verify_export(self, profile_name: str, seed: int = DEFAULT_SEED) -> bool:
        """Vérifie l'intégrité d'un export via fingerprint.

        Args:
            profile_name: Nom du profil
            seed: Graine

        Returns:
            True si l'export est valide
        """
        export_path = self.get_export_path(profile_name, seed)
        parquet_dir = export_path / "parquet"
        fingerprint_path = export_path / "fingerprint.json"

        if not fingerprint_path.exists() or not parquet_dir.exists():
            return False

        with open(fingerprint_path) as f:
            stored_fp = json.load(f)

        current_fp = exporter_v2.compute_fingerprint(parquet_dir)

        return (
            stored_fp['struct_hash'] == current_fp['struct_hash'] and
            stored_fp.get('ts_hash') == current_fp.get('ts_hash')
        )


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
        print("  verify <profile> [seed]           - Vérifie l'intégrité")
        print()
        print("Profiles: small-2d, small-1w, small-1m, small-6m, small-1y")
        print("          medium-2d, ..., large-1y")
        return

    manager = DatasetManager()
    command = sys.argv[1]

    if command == 'generate':
        profile = sys.argv[2]
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_SEED
        export_path, summary, fingerprint = manager.generate_and_export(profile, seed)
        print(f"\n[OK] Dataset: {summary['node_count']} nodes, {summary['edge_count']} edges")

    elif command == 'list':
        datasets = manager.list_exported_datasets()
        if not datasets:
            print("No datasets exported")
        else:
            print(f"Exported datasets ({len(datasets)}):")
            for ds in datasets:
                print(f"  {ds['name']}: {ds['size_mb']:.1f} MB")
                print(f"    Nodes: {ds['nodes']:,}, Edges: {ds['edges']:,}, TS: {ds['timeseries']:,}")
                print(f"    Fingerprint: {ds['fingerprint']}")

    elif command == 'info':
        profile = sys.argv[2]
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_SEED
        info = manager.get_export_info(profile, seed)
        if info:
            print(f"Profile: {info['profile']}")
            print(f"Nodes: {info['nodes']:,}")
            print(f"Edges: {info['edges']:,}")
            print(f"Timeseries: {info['timeseries']:,}")
            print(f"Duration: {info['duration_days']} days")
            print(f"Seed: {info['seed']}")
            print(f"Size: {info['size_mb']:.1f} MB")
            print(f"Scenarios: {', '.join(info['scenarios'])}")
            print(f"Fingerprint: {info['fingerprint']}")
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

    elif command == 'verify':
        profile = sys.argv[2]
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_SEED
        if manager.verify_export(profile, seed):
            print(f"[OK] Dataset {profile} is valid")
        else:
            print(f"[ERR] Dataset {profile} is invalid or missing")


if __name__ == "__main__":
    main()
