"""Export neutre au format JSON pour un property graph."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from basetype_benchmark.dataset.generator import Dataset


def export_property_graph(dataset: Dataset, out_dir: Path) -> None:
    """Exporte le dataset en format property graph avec timeseries chunkées.

    Format conforme aux pratiques industrielles BOS/Digital Twin:
    - Structure: nodes et edges classiques
    - Timeseries: nœuds TimeseriesChunk avec arrays de valeurs
    - Évite le pattern naïf "1 mesure = 1 nœud"
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    nodes_path = out_dir / "nodes.json"
    edges_path = out_dir / "edges.json"
    chunks_path = out_dir / "timeseries_chunks.json"

    # Export des nœuds de structure avec building_id
    with nodes_path.open("w", encoding="utf-8") as f_nodes:
        for node in dataset.nodes:
            json.dump({
                "id": node.id,
                "type": node.type.value,
                "name": node.name,
                "building_id": node.properties.get("building_id", 0),
                "properties": node.properties
            }, f_nodes)
            f_nodes.write("\n")

    # Export des edges de structure
    with edges_path.open("w", encoding="utf-8") as f_edges:
        for edge in dataset.edges:
            json.dump({"src": edge.src, "dst": edge.dst, "rel": edge.rel.value}, f_edges)
            f_edges.write("\n")
        for measure in dataset.measures:
            json.dump({"src": measure.src, "dst": measure.quantity, "rel": "MEASURES"}, f_edges)
            f_edges.write("\n")

    # Export des timeseries chunks
    with chunks_path.open("w", encoding="utf-8") as f_chunks:
        for chunk in dataset.timeseries:
            # Nœud chunk
            chunk_node = {
                "id": f"chunk_{chunk.point_id}_{chunk.start_time}",
                "type": "TimeseriesChunk",
                "point_id": chunk.point_id,
                "start_time": chunk.start_time,
                "end_time": chunk.end_time,
                "frequency_seconds": chunk.frequency_seconds,
                "values": chunk.values
            }
            json.dump(chunk_node, f_chunks)
            f_chunks.write("\n")

            # Edge HAS_CHUNK
            chunk_edge = {
                "src": chunk.point_id,
                "dst": f"chunk_{chunk.point_id}_{chunk.start_time}",
                "rel": "HAS_CHUNK"
            }
            json.dump(chunk_edge, f_chunks)
            f_chunks.write("\n")
