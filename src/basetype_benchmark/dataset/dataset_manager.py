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
        formats: list = None,
        n_workers: int = None,
        mode: str = "vectorized",
        export_targets: bool = False,
    ) -> Tuple[Path, Dict[str, Any], Dict[str, Any]]:
        """Génère un dataset et l'exporte directement sur disque.

        Workflow V2 (disk-efficient default):
        1. Génère le graphe avec generator_v2 (depuis Exploration + YAML)
        2. Exporte vers Parquet (format pivot)
        3. (Optionnel) Exporte vers les formats cibles (P1, P2, M1, M2, O1, O2)
        4. Calcule le fingerprint pour validation

        Pour les gros datasets (>5 GB), utilise le mode streaming.

        Args:
            profile_name: Nom du profil (ex: 'small-1w', 'medium-1m')
            seed: Graine pour reproductibilité
            formats: Liste des formats d'export (None = tous)
                    Options: 'parquet', 'postgresql', 'postgresql_jsonb',
                             'memgraph', 'memgraph_m1', 'oxigraph', 'oxigraph_o1'
            n_workers: Number of worker processes (for mode='parallel' only)
            mode: Simulation mode:
                - "vectorized": NumPy vectorized (100-500x faster, RECOMMENDED)
                - "sequential": Original Python step-by-step
                - "parallel": Multiprocessing (deprecated; usually slower than vectorized)

        Returns:
            Tuple (chemin_export, summary_dict, fingerprint_dict)
        """
        if formats is None:
            formats = ['parquet']

        # Backward-compat: if caller explicitly requested non-parquet formats,
        # enable target exports.
        if any(fmt != 'parquet' for fmt in formats):
            export_targets = True

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
        total_steps = 3 if export_targets else 2
        print(f"    [1/{total_steps}] Generating graph structure...")
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
        print(f"    [2/{total_steps}] Exporting to Parquet pivot...")
        parquet_start = time_module.time()

        parquet_dir = export_subdir / "parquet"

        effective_mode = mode

        # Always use streaming export for vectorized mode (uses direct Parquet write)
        # For other modes, use streaming only for large datasets
        if effective_mode == "vectorized" or use_streaming:
            exporter_v2.export_parquet_streaming(
                dataset, parquet_dir, duration_days=duration_days,
                mode=effective_mode, n_workers=n_workers
            )
        else:
            exporter_v2.export_parquet(
                dataset, parquet_dir, duration_days=duration_days
            )

        parquet_time = time_module.time() - parquet_start
        print(f"          Done in {parquet_time:.1f}s")
        print()

        if export_targets:
            # =====================================================================
            # PHASE 3: Exporter vers les formats cibles (optional)
            # =====================================================================
            print(f"    [3/{total_steps}] Exporting to target formats...")
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

    def prune_scenario(
        self,
        profile_name: str,
        scenario: str,
        seed: int = DEFAULT_SEED,
        keep_shared_timeseries: bool = True
    ) -> bool:
        """Supprime les fichiers d'un scénario spécifique pour libérer le disque.

        Args:
            profile_name: Nom du profil
            scenario: Code scénario (P1, P2, M1, M2, O1, O2)
            seed: Graine
            keep_shared_timeseries: Si True, garde timeseries.csv (partagé P1/P2/M2/O2)

        Returns:
            True si des fichiers ont été supprimés
        """
        scenario_path = self.get_scenario_path(profile_name, scenario, seed)
        if not scenario_path.exists():
            return False

        # Fichiers à conserver si keep_shared_timeseries
        shared_files = {"timeseries.csv", "pg_timeseries.csv"} if keep_shared_timeseries else set()

        deleted_count = 0
        for f in scenario_path.iterdir():
            if f.is_file() and f.name not in shared_files:
                f.unlink()
                deleted_count += 1

        # Supprimer le dossier s'il est vide (ou ne contient que shared)
        remaining = list(scenario_path.iterdir())
        if not remaining:
            scenario_path.rmdir()

        print(f"[PRUNE] {scenario}: deleted {deleted_count} files")
        return deleted_count > 0

    def export_scenario_only(
        self,
        profile_name: str,
        scenario: str,
        seed: int = DEFAULT_SEED,
        skip_timeseries: bool = False,
    ) -> Path:
        """Exporte uniquement un scénario spécifique depuis le Parquet pivot.

        Workflow optimisé pour gros datasets:
        1. Parquet doit déjà exister (via generate_parquet_only)
        2. Exporte uniquement le format nécessaire pour ce scénario
        3. Après le run, appeler prune_scenario pour libérer l'espace

        Args:
            profile_name: Nom du profil
            scenario: Code scénario (P1, P2, M1, M2, O1, O2)
            seed: Graine
            skip_timeseries: If True, don't export timeseries (use shared version)

        Returns:
            Path vers le répertoire du scénario
        """
        export_path = self.get_export_path(profile_name, seed)
        parquet_dir = export_path / "parquet"

        if not parquet_dir.exists():
            raise RuntimeError(
                f"Parquet pivot not found at {parquet_dir}. "
                "Call generate_parquet_only() first."
            )

        scenario_upper = scenario.upper()
        scenario_lower = scenario.lower()
        output_dir = export_path / scenario_lower

        # Mapping scénario -> target exporter
        target_mapping = {
            'P1': 'postgresql',
            'P2': 'postgresql_jsonb',
            'M1': 'memgraph_m1',
            'M2': 'memgraph',
            'O1': 'oxigraph_o1',
            'O2': 'oxigraph',
        }

        if scenario_upper not in target_mapping:
            raise ValueError(f"Unknown scenario: {scenario}. Valid: {list(target_mapping.keys())}")

        target = target_mapping[scenario_upper]

        # P1/P2: ALWAYS skip timeseries CSV export - engine loads directly from Parquet
        # M2/O2: Need shared timeseries.csv for TimescaleDB
        # M1/O1: Have their own chunked format, no timeseries CSV needed
        shared_ts_path = export_path / "timeseries.csv"
        
        if scenario_upper in ('P1', 'P2', 'M1', 'O1'):
            # These scenarios can load directly from Parquet or use their own format
            use_skip_ts = True
        else:
            # M2/O2 need shared timeseries.csv for external TimescaleDB
            use_skip_ts = skip_timeseries or shared_ts_path.exists()

        print(f"[EXPORT] {scenario_upper} ({target})...")
        exporter_v2.export_for_target(parquet_dir, target, output_dir, skip_timeseries=use_skip_ts)
        print(f"[EXPORT] {scenario_upper} done -> {output_dir}")

        return output_dir

    def generate_parquet_only(
        self,
        profile_name: str,
        seed: int = DEFAULT_SEED,
        n_workers: int = None,
        mode: str = "vectorized",
    ) -> Tuple[Path, Dict[str, Any]]:
        """Génère uniquement le Parquet pivot (sans les exports scénarios).

        Workflow optimisé pour gros datasets:
        1. Cette méthode génère le Parquet pivot
        2. Appeler export_scenario_only() pour chaque scénario avant son run
        3. Appeler prune_scenario() après chaque run

        Args:
            profile_name: Nom du profil
            seed: Graine
            n_workers: Number of worker processes (for mode='parallel' only)
            mode: Simulation mode:
                - "vectorized": NumPy vectorized (100-500x faster, RECOMMENDED)
                - "sequential": Original Python step-by-step
                - "parallel": Multiprocessing (deprecated; usually slower than vectorized)

        Returns:
            Tuple (parquet_dir, fingerprint)
        """
        # Parser le profil
        scale, duration_days = self._parse_profile(profile_name)
        resolved_profile = ALIASES.get(profile_name, profile_name)
        estimated_size = self._estimate_size_gb(scale, duration_days)

        # Créer le répertoire d'export
        export_subdir = self.export_dir / f"{resolved_profile}_seed{seed}"
        parquet_dir = export_subdir / "parquet"

        # Si Parquet existe déjà, skip
        if (parquet_dir / "timeseries.parquet").exists():
            print(f"[i] Parquet pivot already exists: {parquet_dir}")
            fingerprint = exporter_v2.compute_fingerprint(parquet_dir)
            fingerprint["profile"] = resolved_profile
            fingerprint["seed"] = seed
            fingerprint["duration_days"] = duration_days
            exporter_v2.save_fingerprint(fingerprint, export_subdir)
            return parquet_dir, fingerprint

        if export_subdir.exists():
            shutil.rmtree(export_subdir)
        export_subdir.mkdir(parents=True)

        print(f"[i] Generating Parquet pivot for {profile_name}")
        print(f"    Scale: {scale}, Duration: {duration_days} days")
        print(f"    Estimated size: ~{estimated_size:.1f} GB")

        use_streaming = estimated_size >= STREAMING_THRESHOLD_GB
        if use_streaming:
            print(f"    Mode: STREAMING")

        start_time = time_module.time()

        # Phase 1: Générer le graphe
        print(f"    [1/2] Generating graph structure...")
        generator = DatasetGeneratorV2(
            profile_name=scale,
            config_path=CONFIG_DIR,
            exploration_path=EXPLORATION_DIR if EXPLORATION_DIR.exists() else None,
            seed=seed
        )
        dataset = generator.generate()
        print(f"          Nodes: {len(dataset.nodes):,}, Edges: {len(dataset.edges):,}, Points: {len(dataset.points):,}")

        # Phase 2: Export Parquet
        print(f"    [2/2] Exporting to Parquet pivot...")

        effective_mode = mode

        # Always use streaming export for vectorized mode (uses direct Parquet write)
        # For other modes, use streaming only for large datasets
        if effective_mode == "vectorized" or use_streaming:
            exporter_v2.export_parquet_streaming(
                dataset, parquet_dir, duration_days=duration_days,
                mode=effective_mode, n_workers=n_workers
            )
        else:
            exporter_v2.export_parquet(dataset, parquet_dir, duration_days=duration_days)

        # Cleanup
        del dataset
        gc.collect()

        # Fingerprint
        fingerprint = exporter_v2.compute_fingerprint(parquet_dir)
        fingerprint["profile"] = resolved_profile
        fingerprint["seed"] = seed
        fingerprint["duration_days"] = duration_days
        exporter_v2.save_fingerprint(fingerprint, export_subdir)

        total_time = time_module.time() - start_time
        print(f"[OK] Parquet pivot generated in {total_time:.1f}s")

        return parquet_dir, fingerprint

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

        stored_ts_mode = stored_fp.get("ts_hash_mode", "row" if stored_fp.get("ts_hash") else "none")
        if stored_ts_mode == "none":
            current_fp = exporter_v2.compute_fingerprint(parquet_dir, include_timeseries_hash=False)
            return stored_fp["struct_hash"] == current_fp["struct_hash"]

        current_fp = exporter_v2.compute_fingerprint(
            parquet_dir,
            include_timeseries_hash=True,
            ts_hash_mode=stored_ts_mode,
        )

        return (
            stored_fp["struct_hash"] == current_fp["struct_hash"]
            and stored_fp.get("ts_hash") == current_fp.get("ts_hash")
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
        parquet_dir, fingerprint = manager.generate_parquet_only(profile, seed)
        export_path = parquet_dir.parent
        print(f"\n[OK] Parquet pivot ready at: {export_path}")
        print(f"     Nodes: {fingerprint['counts']['nodes']:,}, Edges: {fingerprint['counts']['edges']:,}")

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
