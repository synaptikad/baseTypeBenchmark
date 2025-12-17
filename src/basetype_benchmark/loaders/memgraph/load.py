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
import threading
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Callable

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


class LoadingTimeout(Exception):
    """Exception raised when loading operation times out or stalls."""
    pass


class LoadingStalled(Exception):
    """Exception raised when loading progress stalls (possible memory pressure)."""
    pass


def run_with_timeout(func: Callable, timeout_seconds: float, description: str = "operation"):
    """Run a function with timeout, raising LoadingTimeout if exceeded.

    Args:
        func: Function to execute
        timeout_seconds: Maximum time allowed
        description: Description for error messages

    Returns:
        Result of func()

    Raises:
        LoadingTimeout: If operation exceeds timeout
    """
    result = [None]
    exception = [None]
    completed = threading.Event()

    def wrapper():
        try:
            result[0] = func()
        except Exception as e:
            exception[0] = e
        finally:
            completed.set()

    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()

    if not completed.wait(timeout=timeout_seconds):
        raise LoadingTimeout(f"{description} timed out after {timeout_seconds}s")

    if exception[0]:
        raise exception[0]

    return result[0]


def get_driver(
    uri: str = "bolt://localhost:7688",
    auth: Optional[tuple] = None,
    max_retries: int = 10,
    retry_delay: float = 3.0
):
    """Create a Memgraph driver with retry logic.

    Args:
        uri: Bolt URI (default uses port 7688 as mapped in docker-compose)
        auth: Optional (user, password) tuple
        max_retries: Maximum connection attempts
        retry_delay: Seconds to wait between retries

    Returns:
        Neo4j driver object

    Raises:
        ServiceUnavailable: If connection fails after all retries
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            driver = GraphDatabase.driver(uri, auth=auth)
            # Test connection
            with driver.session() as session:
                session.run("RETURN 1")
            return driver
        except (ServiceUnavailable, Exception) as e:
            last_error = e
            if attempt < max_retries - 1:
                print(f"[INFO] Memgraph not ready (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"[ERROR] Memgraph connection failed after {max_retries} attempts: {e}")
    raise last_error


def iter_json_lines(path: Path) -> Iterable[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_constraints(session) -> None:
    """Create indexes and constraints for efficient loading.

    CRITICAL: The index on Node.id is essential for edge loading performance.
    Without it, each MATCH in flush_edges is O(N) instead of O(1).
    """
    # Drop existing constraints/indexes first (idempotent)
    try:
        session.run("DROP INDEX ON :Node(id);")
    except Exception:
        pass
    try:
        session.run("DROP INDEX ON :Node(type);")
    except Exception:
        pass
    try:
        session.run("DROP INDEX ON :TimeseriesChunk(id);")
    except Exception:
        pass

    # Create indexes - CRITICAL for edge loading performance
    # Memgraph uses label property indexes
    print("  Creating indexes...", flush=True)

    # Primary index on Node.id - MUST exist for edge MATCH to be fast
    session.run("CREATE INDEX ON :Node(id);")
    print("    - Index on :Node(id) created", flush=True)

    # Secondary index on type for query filtering
    session.run("CREATE INDEX ON :Node(type);")
    print("    - Index on :Node(type) created", flush=True)

    # Index for TimeseriesChunk lookups
    session.run("CREATE INDEX ON :TimeseriesChunk(id);")
    print("    - Index on :TimeseriesChunk(id) created", flush=True)

    # Verify indexes exist
    result = session.run("SHOW INDEX INFO;")
    indexes = list(result)
    print(f"    - Total indexes: {len(indexes)}", flush=True)


def load_nodes(session, nodes_path: Path, batch_size: int) -> int:
    batch: List[Dict[str, str]] = []
    total = 0
    t0 = time.perf_counter()

    for node in iter_json_lines(nodes_path):
        batch.append(node)
        if len(batch) >= batch_size:
            session.run(
                "UNWIND $batch AS row "
                "CREATE (n:Node {id: row.id, type: row.type, name: row.name})",
                batch=batch,
            )
            total += len(batch)
            if total % 10000 == 0:
                print(f"  ... {total} nodes loaded", flush=True)
            batch.clear()

    if batch:
        session.run(
            "UNWIND $batch AS row "
            "CREATE (n:Node {id: row.id, type: row.type, name: row.name})",
            batch=batch,
        )
        total += len(batch)

    elapsed = time.perf_counter() - t0
    print(f"Noeuds insérés: {total} en {elapsed:.2f}s")
    return total


def flush_edges(session, rel_type: str, batch: List[Dict[str, str]], timeout_seconds: float = 60.0) -> None:
    """Flush edge batch with timeout protection.

    Args:
        session: Neo4j/Memgraph session
        rel_type: Relationship type
        batch: List of edge dicts with src/dst
        timeout_seconds: Max time for this batch (default 60s)

    Raises:
        LoadingTimeout: If batch takes too long (memory pressure indicator)
    """
    if not batch:
        return
    query = (
        "UNWIND $batch AS row "
        "MATCH (s:Node {id: row.src}) "
        "MATCH (d:Node {id: row.dst}) "
        f"CREATE (s)-[:{rel_type} {{source: 'synthetic'}}]->(d)"
    )

    def execute():
        session.run(query, batch=batch)

    run_with_timeout(execute, timeout_seconds, f"flush_edges({rel_type}, {len(batch)} edges)")


def flush_quantities(session, batch: List[Dict[str, str]], timeout_seconds: float = 60.0) -> None:
    """Flush quantity batch with timeout protection."""
    if not batch:
        return

    def execute():
        session.run(
            "UNWIND $batch AS row "
            "MATCH (p:Node {id: row.src}) "
            "SET p.quantity = row.dst",
            batch=batch,
        )

    run_with_timeout(execute, timeout_seconds, f"flush_quantities({len(batch)} items)")


def load_edges(
    session,
    edges_path: Path,
    batch_size: int,
    batch_timeout_seconds: float = 60.0,
    stall_threshold_multiplier: float = 5.0,
    min_batches_for_stall_detection: int = 5,
    adaptive_batch_size: bool = True,
    min_batch_size: int = 100,
    max_retries_on_stall: int = 3
) -> Dict[str, int]:
    """Load edges with timeout, stall detection, and adaptive batch sizing.

    Args:
        session: Memgraph session
        edges_path: Path to edges.json
        batch_size: Base batch size (will be capped at 1000 for edges)
        batch_timeout_seconds: Timeout per batch (default 60s)
        stall_threshold_multiplier: If batch takes > avg * this, consider stalled (default 5x)
        min_batches_for_stall_detection: Min batches before stall detection kicks in
        adaptive_batch_size: If True, reduce batch size on slowdown instead of failing
        min_batch_size: Minimum batch size before giving up
        max_retries_on_stall: Max consecutive stalls before giving up

    Returns:
        Dict with relationship and measurement counts

    Raises:
        LoadingTimeout: If a batch times out
        LoadingStalled: If loading continues to stall despite adaptations
    """
    # Use smaller batch for edges (double MATCH is expensive)
    edge_batch_size = min(batch_size, 1000)
    current_batch_size = edge_batch_size
    consecutive_stalls = 0

    batches: Dict[str, List[Dict[str, str]]] = {}
    measure_batch: List[Dict[str, str]] = []
    counters: Dict[str, int] = {"relationships": 0, "measurements": 0}
    t0 = time.perf_counter()
    total_edges = 0

    # Stall detection: track batch times (only keep recent ones)
    batch_times: List[float] = []
    max_batch_history = 20

    for edge in iter_json_lines(edges_path):
        rel = edge["rel"]
        if rel == "MEASURES":
            measure_batch.append(edge)
            if len(measure_batch) >= current_batch_size:
                flush_quantities(session, measure_batch, batch_timeout_seconds)
                counters["measurements"] += len(measure_batch)
                measure_batch.clear()
            continue

        batch = batches.setdefault(rel, [])
        batch.append(edge)
        if len(batch) >= current_batch_size:
            batch_start = time.perf_counter()

            flush_edges(session, rel, batch, batch_timeout_seconds)

            batch_elapsed = time.perf_counter() - batch_start
            batch_times.append(batch_elapsed)

            # Keep only recent history for accurate average
            if len(batch_times) > max_batch_history:
                batch_times = batch_times[-max_batch_history:]

            # Stall detection: check if this batch is anomalously slow
            is_stalled = False
            if len(batch_times) >= min_batches_for_stall_detection:
                avg_time = sum(batch_times[:-1]) / len(batch_times[:-1])
                if batch_elapsed > avg_time * stall_threshold_multiplier:
                    is_stalled = True
                    rate_now = current_batch_size / batch_elapsed if batch_elapsed > 0 else 0
                    rate_avg = current_batch_size / avg_time if avg_time > 0 else 0

                    if adaptive_batch_size and current_batch_size > min_batch_size:
                        # Reduce batch size instead of failing
                        new_batch_size = max(min_batch_size, current_batch_size // 2)
                        print(f"\n  [!] Slowdown detected ({batch_elapsed:.1f}s vs avg {avg_time:.1f}s). "
                              f"Reducing batch size: {current_batch_size} -> {new_batch_size}", flush=True)
                        current_batch_size = new_batch_size
                        consecutive_stalls += 1

                        # Clear batch times to recalibrate with new batch size
                        batch_times = []

                        if consecutive_stalls >= max_retries_on_stall:
                            raise LoadingStalled(
                                f"Loading stalled despite {max_retries_on_stall} batch size reductions. "
                                f"Current batch size: {current_batch_size}. "
                                f"Rate: {rate_now:.0f} edges/s. Likely severe memory pressure."
                            )
                    else:
                        raise LoadingStalled(
                            f"Loading stalled: batch took {batch_elapsed:.1f}s "
                            f"(avg: {avg_time:.1f}s, threshold: {avg_time * stall_threshold_multiplier:.1f}s). "
                            f"Rate dropped from {rate_avg:.0f} edges/s to {rate_now:.0f} edges/s. "
                            f"Likely memory pressure - consider increasing RAM."
                        )

            if not is_stalled:
                consecutive_stalls = 0  # Reset on successful batch

            counters["relationships"] += len(batch)
            total_edges += len(batch)

            if total_edges % 10000 == 0:
                elapsed_so_far = time.perf_counter() - t0
                rate = total_edges / elapsed_so_far if elapsed_so_far > 0 else 0
                batch_info = f" [batch={current_batch_size}]" if current_batch_size != edge_batch_size else ""
                print(f"  ... {total_edges} edges loaded ({rate:.0f} edges/s){batch_info}", flush=True)
            batch.clear()

    for rel, batch in batches.items():
        if batch:
            flush_edges(session, rel, batch, batch_timeout_seconds)
            counters["relationships"] += len(batch)
    if measure_batch:
        flush_quantities(session, measure_batch, batch_timeout_seconds)
        counters["measurements"] += len(measure_batch)

    elapsed = time.perf_counter() - t0
    rate = total_edges / elapsed if elapsed > 0 else 0
    print(
        f"Relations créées: {counters['relationships']}, "
        f"propriétés MEASURES appliquées: {counters['measurements']} "
        f"en {elapsed:.2f}s ({rate:.0f} edges/s)"
    )
    return counters


def load_timeseries_chunks(
    session,
    chunks_path: Path,
    batch_size: int,
    batch_timeout_seconds: float = 60.0
) -> Dict[str, int]:
    """Charge les chunks de séries temporelles dans Memgraph.

    Format conforme aux pratiques industrielles:
    - Nœuds TimeseriesChunk avec arrays de valeurs
    - Edges HAS_CHUNK reliant les Points aux chunks

    Args:
        session: Memgraph session
        chunks_path: Path to timeseries_chunks.json
        batch_size: Batch size for inserts
        batch_timeout_seconds: Timeout per batch operation

    Returns:
        Dict with chunk_nodes and chunk_edges counts

    Raises:
        LoadingTimeout: If a batch times out
    """
    chunk_nodes_batch: List[Dict] = []
    chunk_edges_batch: List[Dict] = []
    counters: Dict[str, int] = {"chunk_nodes": 0, "chunk_edges": 0}
    t0 = time.perf_counter()

    def flush_chunk_nodes(batch):
        session.run(
            "UNWIND $batch AS row "
            "CREATE (c:TimeseriesChunk {id: row.id}) "
            "SET c.point_id = row.point_id, "
            "    c.start_time = row.start_time, "
            "    c.end_time = row.end_time, "
            "    c.frequency_seconds = row.frequency_seconds, "
            "    c.values = row.values",
            batch=batch,
        )

    def flush_chunk_edges(batch):
        session.run(
            "UNWIND $batch AS row "
            "MATCH (p:Node {id: row.src}) "
            "MATCH (c:TimeseriesChunk {id: row.dst}) "
            "CREATE (p)-[:HAS_CHUNK]->(c)",
            batch=batch,
        )

    for line in iter_json_lines(chunks_path):
        if line.get("type") == "TimeseriesChunk":
            chunk_nodes_batch.append(line)
            if len(chunk_nodes_batch) >= batch_size:
                run_with_timeout(
                    lambda b=list(chunk_nodes_batch): flush_chunk_nodes(b),
                    batch_timeout_seconds,
                    f"flush_chunk_nodes({len(chunk_nodes_batch)} chunks)"
                )
                counters["chunk_nodes"] += len(chunk_nodes_batch)
                if counters["chunk_nodes"] % 10000 == 0:
                    print(f"  ... {counters['chunk_nodes']} chunk nodes loaded", flush=True)
                chunk_nodes_batch.clear()
        elif line.get("rel") == "HAS_CHUNK":
            chunk_edges_batch.append(line)
            if len(chunk_edges_batch) >= batch_size:
                run_with_timeout(
                    lambda b=list(chunk_edges_batch): flush_chunk_edges(b),
                    batch_timeout_seconds,
                    f"flush_chunk_edges({len(chunk_edges_batch)} edges)"
                )
                counters["chunk_edges"] += len(chunk_edges_batch)
                if counters["chunk_edges"] % 10000 == 0:
                    print(f"  ... {counters['chunk_edges']} chunk edges loaded", flush=True)
                chunk_edges_batch.clear()

    # Flush remaining batches
    if chunk_nodes_batch:
        run_with_timeout(
            lambda: flush_chunk_nodes(chunk_nodes_batch),
            batch_timeout_seconds,
            f"flush_chunk_nodes({len(chunk_nodes_batch)} chunks, final)"
        )
        counters["chunk_nodes"] += len(chunk_nodes_batch)

    if chunk_edges_batch:
        run_with_timeout(
            lambda: flush_chunk_edges(chunk_edges_batch),
            batch_timeout_seconds,
            f"flush_chunk_edges({len(chunk_edges_batch)} edges, final)"
        )
        counters["chunk_edges"] += len(chunk_edges_batch)

    elapsed = time.perf_counter() - t0
    print(
        f"Chunks créés: {counters['chunk_nodes']}, "
        f"Relations HAS_CHUNK: {counters['chunk_edges']} "
        f"en {elapsed:.2f}s"
    )
    return counters


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Loader Memgraph pour Base Type Benchmark")
    parser.add_argument(
        "--uri",
        default="bolt://localhost:7688",
        help="URI Bolt Memgraph (port 7688 mapped from container's 7687)",
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
    parser.add_argument(
        "--chunks-file",
        type=Path,
        default=Path("dataset_gen/out/timeseries_chunks.json"),
        help="Chemin vers timeseries_chunks.json généré",
    )
    parser.add_argument("--batch-size", type=int, default=1000, help="Taille des batchs d'insertion")
    parser.add_argument("--skip-chunks", action="store_true", help="Skip loading timeseries chunks (structure only)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    auth = None
    if args.user is not None and args.password is not None:
        auth = (args.user, args.password)

    driver = get_driver(args.uri, auth=auth)
    with driver.session() as session:
        load_constraints(session)
        load_nodes(session, args.nodes_file, args.batch_size)
        load_edges(session, args.edges_file, args.batch_size)

        if not args.skip_chunks and args.chunks_file.exists():
            print(f"\nLoading timeseries chunks from {args.chunks_file}")
            load_timeseries_chunks(session, args.chunks_file, args.batch_size)
        elif args.skip_chunks:
            print("\nTimeseries chunks skipped (--skip-chunks)")
        else:
            print(f"\nChunks file not found: {args.chunks_file}")

    driver.close()


if __name__ == "__main__":
    main()
