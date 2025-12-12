"""Export neutre vers un format PostgreSQL/TimescaleDB (fichiers COPY)."""
from __future__ import annotations

import csv
from pathlib import Path

from .generator import Dataset


def export_postgres(dataset: Dataset, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    nodes_path = out_dir / "nodes.csv"
    edges_path = out_dir / "edges.csv"

    with nodes_path.open("w", newline="", encoding="utf-8") as f_nodes:
        writer = csv.writer(f_nodes)
        writer.writerow(["id", "type", "name"])
        for node in dataset.nodes:
            writer.writerow([node.id, node.type.value, node.name])

    with edges_path.open("w", newline="", encoding="utf-8") as f_edges:
        writer = csv.writer(f_edges)
        writer.writerow(["src_id", "dst_id", "rel_type"])
        for edge in dataset.edges:
            writer.writerow([edge.src, edge.dst, edge.rel.value])
        for measure in dataset.measures:
            writer.writerow([measure.src, measure.quantity, "MEASURES"])
