"""Point d'entrée pour générer et exporter le dataset."""
from __future__ import annotations

import os
from pathlib import Path

from dataset_gen.config import ALIASES, DEFAULT_SEED, get_profile
from dataset_gen.export_graph import export_property_graph
from dataset_gen.export_pg import export_postgres
from dataset_gen.export_rdf import export_rdf
from dataset_gen.generator import generate_dataset


def main() -> None:
    mode = os.environ.get("SCALE_MODE", "small")
    seed = int(os.environ.get("SEED", DEFAULT_SEED))

    profile = get_profile(mode)
    normalized_mode = ALIASES.get(mode.lower(), mode.lower())
    dataset, summary = generate_dataset(profile, seed)

    out_dir = Path(__file__).parent / "out"
    export_postgres(dataset, out_dir)
    export_property_graph(dataset, out_dir)
    export_rdf(dataset, out_dir)

    print("Dataset généré avec succès")
    print(
        "Profil de volumétrie: "
        f"{normalized_mode} (SCALE_MODE={mode}, alias acceptés: {', '.join(ALIASES)})"
    )
    print(f"Seed: {seed}")
    print(f"Nœuds: {summary.node_count}")
    for rel, count in sorted(summary.relation_counts.items(), key=lambda x: x[0].value):
        print(f"{rel.value}: {count}")
    print(f"Profondeur globale max: {summary.max_depth}")
    print(f"Profondeur FEEDS max: {summary.max_feeds_depth}")
    print(f"Profondeur fonctionnelle max: {summary.max_functional_depth}")


if __name__ == "__main__":
    main()
