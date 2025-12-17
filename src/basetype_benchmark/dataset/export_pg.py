"""Export vers PostgreSQL/TimescaleDB (fichiers CSV pour COPY).

Supporte deux modes de schéma :
- P1 (relational): colonnes id, type, name, building_id
- P2 (JSONB): colonnes id, type, name, building_id + data JSONB

L'export unifié produit les colonnes nécessaires pour les deux schémas.
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from basetype_benchmark.dataset.generator import Dataset


def export_postgres(dataset: Dataset, out_dir: Path) -> None:
    """Export PostgreSQL compatible P1 et P2.

    Format nodes.csv : id, type, name, building_id, data (JSONB)
    Format edges.csv : src_id, dst_id, rel_type
    Format timeseries.csv : time, point_id, value
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    nodes_path = out_dir / "nodes.csv"
    edges_path = out_dir / "edges.csv"

    # Export nodes avec building_id et data JSONB
    with nodes_path.open("w", newline="", encoding="utf-8") as f_nodes:
        writer = csv.writer(f_nodes)
        writer.writerow(["id", "type", "name", "building_id", "data"])
        for node in dataset.nodes:
            building_id = node.properties.get("building_id", 0)
            # data JSONB contient toutes les propriétés sauf building_id (déjà extrait)
            data = json.dumps(node.properties)
            writer.writerow([node.id, node.type.value, node.name, building_id, data])

    # Export edges
    with edges_path.open("w", newline="", encoding="utf-8") as f_edges:
        writer = csv.writer(f_edges)
        writer.writerow(["src_id", "dst_id", "rel_type"])
        for edge in dataset.edges:
            writer.writerow([edge.src, edge.dst, edge.rel.value])
        for measure in dataset.measures:
            writer.writerow([measure.src, measure.quantity, "MEASURES"])

    # Export séries temporelles avec format ISO timestamp
    timeseries_path = out_dir / "timeseries.csv"
    with timeseries_path.open("w", newline="", encoding="utf-8") as f_ts:
        writer = csv.writer(f_ts)
        writer.writerow(["time", "point_id", "value"])
        for chunk in dataset.timeseries:
            current_time = chunk.start_time
            for value in chunk.values:
                # Format ISO pour PostgreSQL TIMESTAMPTZ
                ts = datetime.fromtimestamp(current_time, tz=timezone.utc).isoformat()
                writer.writerow([ts, chunk.point_id, value])
                current_time += chunk.frequency_seconds
