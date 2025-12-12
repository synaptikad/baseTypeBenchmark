"""Export neutre au format JSON pour un property graph."""
from __future__ import annotations

import json
from pathlib import Path

from .generator import Dataset


def export_property_graph(dataset: Dataset, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    nodes_path = out_dir / "nodes.json"
    edges_path = out_dir / "edges.json"

    with nodes_path.open("w", encoding="utf-8") as f_nodes:
        for node in dataset.nodes:
            json.dump({"id": node.id, "type": node.type.value, "name": node.name}, f_nodes)
            f_nodes.write("\n")

    with edges_path.open("w", encoding="utf-8") as f_edges:
        for edge in dataset.edges:
            json.dump({"src": edge.src, "dst": edge.dst, "rel": edge.rel.value}, f_edges)
            f_edges.write("\n")
        for measure in dataset.measures:
            json.dump({"src": measure.src, "dst": measure.quantity, "rel": "MEASURES"}, f_edges)
            f_edges.write("\n")
