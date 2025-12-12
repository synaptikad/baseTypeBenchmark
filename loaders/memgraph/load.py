"""Charge les données du dataset synthétique dans Memgraph via Bolt.

Le loader s'appuie sur le driver officiel Neo4j, compatible avec Memgraph, et
exploite les exports JSON ligne par ligne produits par `dataset_gen`. Les
relations MEASURES sont traduites en propriété `quantity` sur les points afin
que les requêtes structurelles puissent filtrer les points de température ou de
puissance sans introduire de noeuds supplémentaires.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Iterable, List

from neo4j import GraphDatabase


def iter_json_lines(path: Path) -> Iterable[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_constraints(session) -> None:
    session.run("CREATE CONSTRAINT ON (n:Node) ASSERT n.id IS UNIQUE;")
    session.run("CREATE INDEX ON :Node(type);")


def load_nodes(session, nodes_path: Path, batch_size: int) -> int:
    batch: List[Dict[str, str]] = []
    total = 0
    t0 = time.perf_counter()

    for node in iter_json_lines(nodes_path):
        batch.append(node)
        if len(batch) >= batch_size:
            session.run(
                "UNWIND $batch AS row "
                "MERGE (n:Node {id: row.id}) "
                "SET n.type = row.type, n.name = row.name",
                batch=batch,
            )
            total += len(batch)
            batch.clear()

    if batch:
        session.run(
            "UNWIND $batch AS row "
            "MERGE (n:Node {id: row.id}) "
            "SET n.type = row.type, n.name = row.name",
            batch=batch,
        )
        total += len(batch)

    elapsed = time.perf_counter() - t0
    print(f"Noeuds insérés: {total} en {elapsed:.2f}s")
    return total


def flush_edges(session, rel_type: str, batch: List[Dict[str, str]]) -> None:
    if not batch:
        return
    query = (
        "UNWIND $batch AS row "
        "MATCH (s:Node {id: row.src}) "
        "MATCH (d:Node {id: row.dst}) "
        f"CREATE (s)-[:{rel_type} {{source: 'synthetic'}}]->(d)"
    )
    session.run(query, batch=batch)


def flush_quantities(session, batch: List[Dict[str, str]]) -> None:
    if not batch:
        return
    session.run(
        "UNWIND $batch AS row "
        "MATCH (p:Node {id: row.src}) "
        "SET p.quantity = row.dst",
        batch=batch,
    )


def load_edges(session, edges_path: Path, batch_size: int) -> Dict[str, int]:
    batches: Dict[str, List[Dict[str, str]]] = {}
    measure_batch: List[Dict[str, str]] = []
    counters: Dict[str, int] = {"relationships": 0, "measurements": 0}
    t0 = time.perf_counter()

    for edge in iter_json_lines(edges_path):
        rel = edge["rel"]
        if rel == "MEASURES":
            measure_batch.append(edge)
            if len(measure_batch) >= batch_size:
                flush_quantities(session, measure_batch)
                counters["measurements"] += len(measure_batch)
                measure_batch.clear()
            continue

        batch = batches.setdefault(rel, [])
        batch.append(edge)
        if len(batch) >= batch_size:
            flush_edges(session, rel, batch)
            counters["relationships"] += len(batch)
            batch.clear()

    for rel, batch in batches.items():
        if batch:
            flush_edges(session, rel, batch)
            counters["relationships"] += len(batch)
    if measure_batch:
        flush_quantities(session, measure_batch)
        counters["measurements"] += len(measure_batch)

    elapsed = time.perf_counter() - t0
    print(
        "Relations créées: {relationships}, propriétés MEASURES appliquées: {measurements} "
        "en {elapsed:.2f}s".format(elapsed=elapsed, **counters)
    )
    return counters


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Loader Memgraph pour Base Type Benchmark")
    parser.add_argument(
        "--uri",
        default="bolt://localhost:7688",
        help="URI Bolt Memgraph (par défaut bolt://localhost:7688)",
    )
    parser.add_argument("--user", default=None, help="Utilisateur Memgraph si l'authentification est activée")
    parser.add_argument("--password", default=None, help="Mot de passe Memgraph si l'authentification est activée")
    parser.add_argument(
        "--nodes-file",
        type=Path,
        default=Path("dataset_gen/out/nodes.json"),
        help="Chemin vers nodes.json généré",
    )
    parser.add_argument(
        "--edges-file",
        type=Path,
        default=Path("dataset_gen/out/edges.json"),
        help="Chemin vers edges.json généré",
    )
    parser.add_argument("--batch-size", type=int, default=1000, help="Taille des batchs d'insertion")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    auth = None
    if args.user is not None and args.password is not None:
        auth = (args.user, args.password)

    driver = GraphDatabase.driver(args.uri, auth=auth)
    with driver.session() as session:
        load_constraints(session)
        load_nodes(session, args.nodes_file, args.batch_size)
        load_edges(session, args.edges_file, args.batch_size)
    driver.close()


if __name__ == "__main__":
    main()
