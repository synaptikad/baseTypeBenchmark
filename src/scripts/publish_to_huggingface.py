#!/usr/bin/env python3
"""
Publie le dataset de référence sur HuggingFace Hub.

Workflow:
1. Génère le dataset large-1y (profil maximal)
2. Exporte en format Parquet partitionné par mois
3. Publie sur HuggingFace Hub

Prérequis:
    pip install huggingface_hub pyarrow
    export HF_TOKEN=hf_xxxxx  # ou huggingface-cli login

Usage:
    python -m scripts.publish_to_huggingface --repo-id=synaptikad/basetype-benchmark
    python -m scripts.publish_to_huggingface --data-dir=./data/parquet --skip-generation
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from basetype_benchmark.dataset.config import PROFILES
from basetype_benchmark.dataset.generator import generate_dataset, extract_subset
from basetype_benchmark.dataset.huggingface import (
    export_to_parquet,
    publish_dataset,
    generate_dataset_card,
    check_dependencies,
    DEFAULT_REPO_ID,
)

DEFAULT_AUTHOR = "Antoine Debienne"
DEFAULT_ORCID = "0009-0002-6674-2691"


def main():
    parser = argparse.ArgumentParser(
        description="Publie le dataset BaseType Benchmark sur HuggingFace Hub"
    )
    parser.add_argument(
        "--repo-id",
        default=DEFAULT_REPO_ID,
        help=f"ID du repo HuggingFace (défaut: {DEFAULT_REPO_ID})"
    )
    parser.add_argument(
        "--profile",
        default="large-1y",
        help="Profil de génération (défaut: large-1y)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed pour la génération (défaut: 42)"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("./data/parquet"),
        help="Répertoire de sortie pour les fichiers Parquet"
    )
    parser.add_argument(
        "--skip-generation",
        action="store_true",
        help="Passe la génération et utilise les fichiers existants"
    )
    parser.add_argument(
        "--skip-publish",
        action="store_true",
        help="Génère sans publier sur HuggingFace"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Créer un dataset privé sur HuggingFace"
    )
    parser.add_argument(
        "--zenodo-doi",
        type=str,
        default=None,
        help="DOI Zenodo de l'article associé (pour la Dataset Card)"
    )
    parser.add_argument(
        "--author-name",
        type=str,
        default=DEFAULT_AUTHOR,
        help=f"Nom de l'auteur (défaut: {DEFAULT_AUTHOR})"
    )
    parser.add_argument(
        "--author-orcid",
        type=str,
        default=DEFAULT_ORCID,
        help=f"ORCID de l'auteur (défaut: {DEFAULT_ORCID})"
    )
    args = parser.parse_args()

    # Vérifier les dépendances
    deps = check_dependencies()
    if not args.skip_publish and not deps["huggingface_hub"]:
        print("Error: huggingface_hub is not installed. Run: pip install huggingface_hub")
        return 1
    if not deps["pyarrow"]:
        print("Error: pyarrow is not installed. Run: pip install pyarrow")
        return 1

    output_dir = args.data_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_generation:
        # Récupérer le profil
        profile = PROFILES.get(args.profile)
        if profile is None:
            print(f"Error: Profile '{args.profile}' not found. Available: {list(PROFILES.keys())}")
            return 1

        print(f"Generating dataset with profile '{args.profile}'...")
        print(f"  Points: {profile.points:,}")
        print(f"  Duration: {profile.duration_days} days")
        print(f"  Seed: {args.seed}")

        # Génération
        start_time = datetime.now()
        dataset, summary = generate_dataset(profile, args.seed)
        duration = datetime.now() - start_time

        print(f"Generation completed in {duration.total_seconds():.1f}s")
        print(f"  Nodes: {summary.node_count:,}")
        print(f"  Edges: {summary.edge_count:,}")
        print(f"  Buildings: {summary.buildings_count}")
        print(f"  Timeseries points: {summary.timeseries_points:,}")
        print(f"  Timeseries samples: {summary.timeseries_samples:,}")

        print("\nPer-building statistics:")
        for bld_id, stats in summary.building_stats.items():
            print(f"  Building {bld_id}: {stats['spaces']} spaces, {stats['equipments']} equips, {stats['points']} points")

        print(f"\nExporting to Parquet in {output_dir}...")

        # Convertir en dictionnaires pour export
        nodes_dicts = [n.to_dict() for n in dataset.nodes]
        edges_dicts = [e.to_dict() for e in dataset.edges]

        # Convertir les timeseries en format plat pour Parquet
        timeseries_dicts = []
        for ts in dataset.timeseries:
            # Trouver le building_id du point
            point_node = next((n for n in dataset.nodes if n.id == ts.point_id), None)
            building_id = point_node.properties.get("building_id", 0) if point_node else 0

            for i, value in enumerate(ts.values):
                timestamp = ts.start_time + i * ts.frequency_seconds
                ts_datetime = datetime.fromtimestamp(timestamp)
                timeseries_dicts.append({
                    "point_id": ts.point_id,
                    "timestamp": timestamp,
                    "value": value,
                    "building_id": building_id,
                    "year_month": ts_datetime.strftime("%Y-%m"),
                })

        export_to_parquet(
            nodes=nodes_dicts,
            edges=edges_dicts,
            timeseries=timeseries_dicts,
            output_dir=output_dir,
            partition_by_month=True,
        )

        # Générer la Dataset Card
        generate_dataset_card(
            output_path=output_dir / "README.md",
            repo_id=args.repo_id,
            zenodo_doi=args.zenodo_doi,
            author_name=args.author_name,
            author_orcid=args.author_orcid,
        )

        # Sauvegarder le summary
        summary_dict = {
            "profile": args.profile,
            "seed": args.seed,
            "generated_at": datetime.now().isoformat(),
            "node_count": summary.node_count,
            "edge_count": summary.edge_count,
            "buildings_count": summary.buildings_count,
            "timeseries_points": summary.timeseries_points,
            "timeseries_samples": summary.timeseries_samples,
            "node_types": summary.node_types,
            "relation_counts": summary.relation_counts,
            "building_stats": {str(k): v for k, v in summary.building_stats.items()},
        }
        (output_dir / "metadata.json").write_text(
            json.dumps(summary_dict, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        print("Export completed")

    if not args.skip_publish:
        print(f"\nPublishing to HuggingFace: {args.repo_id}...")

        try:
            url = publish_dataset(
                local_path=output_dir,
                repo_id=args.repo_id,
                private=args.private,
                commit_message=f"Update dataset ({args.profile}, seed={args.seed})",
            )
            print(f"Dataset published: {url}")
        except Exception as e:
            print(f"Error during publication: {e}")
            print("  Check that HF_TOKEN is set or run: huggingface-cli login")
            return 1

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
