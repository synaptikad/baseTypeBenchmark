"""Export minimal en JSON-LD pour un graphe RDF/SPARQL."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from basetype_benchmark.dataset.generator import Dataset
from basetype_benchmark.dataset.model import NodeType, RelationType


_NODE_TYPE_IRIS = {node_type.value: f"http://example.org/type/{node_type.value}" for node_type in NodeType}

_CONTEXT = {
    "@base": "http://example.org/id/",
    "id": "@id",
    "type": "@type",
    "name": "http://example.org/name",
    "contains": "http://example.org/CONTAINS",
    "locatedIn": "http://example.org/LOCATED_IN",
    "hasPart": "http://example.org/HAS_PART",
    "hasPoint": "http://example.org/HAS_POINT",
    "measures": "http://example.org/MEASURES",
    "controls": "http://example.org/CONTROLS",
    "feeds": "http://example.org/FEEDS",
    "serves": "http://example.org/SERVES",
    "occupies": "http://example.org/OCCUPIES",
    **_NODE_TYPE_IRIS,
}


def export_rdf(dataset: Dataset, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    graph = _build_graph(dataset)
    data = {"@context": _CONTEXT, "@graph": list(graph.values())}
    out_path = out_dir / "graph.jsonld"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_graph(dataset: Dataset):
    graph = {node.id: {"id": node.id, "type": node.type.value, "name": node.name} for node in dataset.nodes}

    predicate_map = {
        RelationType.CONTAINS: "contains",
        RelationType.LOCATED_IN: "locatedIn",
        RelationType.HAS_PART: "hasPart",
        RelationType.HAS_POINT: "hasPoint",
        RelationType.CONTROLS: "controls",
        RelationType.FEEDS: "feeds",
        RelationType.SERVES: "serves",
        RelationType.OCCUPIES: "occupies",
    }

    for edge in dataset.edges:
        pred = predicate_map.get(edge.rel)
        if pred is None:
            continue
        subject = graph[edge.src]
        subject.setdefault(pred, []).append({"id": edge.dst})

    for measure in dataset.measures:
        subject = graph[measure.src]
        subject.setdefault("measures", []).append({"@value": measure.quantity})

    return graph
