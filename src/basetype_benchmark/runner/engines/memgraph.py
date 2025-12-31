"""Memgraph engine for M1 (standalone) and M2 (hybrid) scenarios."""

import csv
import time
from pathlib import Path
from typing import Callable, List, Tuple

from neo4j import GraphDatabase


class MemgraphEngine:
    """Memgraph engine for M1/M2 benchmarks."""

    def __init__(self, scenario: str = "M1"):
        """Initialize engine.

        Args:
            scenario: M1 (standalone) or M2 (hybrid with TimescaleDB)
        """
        self.scenario = scenario.upper()
        self.driver = None

    def connect(self, uri: str = "bolt://localhost:7688") -> None:
        """Establish database connection."""
        self.driver = GraphDatabase.driver(uri, auth=None)

    def close(self) -> None:
        """Close database connection."""
        if self.driver:
            self.driver.close()
            self.driver = None

    def clear(self) -> None:
        """Clear all data."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            # Drop indexes
            try:
                session.run("DROP INDEX ON :Node(id)")
            except:
                pass
            try:
                session.run("DROP INDEX ON :Node(building_id)")
            except:
                pass

    def load_nodes(self, nodes_file: Path, batch_size: int = 1000) -> int:
        """Load nodes from CSV."""
        total = 0
        t0 = time.time()

        # Create indexes FIRST for fast lookups during edge loading and query filtering
        with self.driver.session() as session:
            session.run("CREATE INDEX ON :Node(id)")
            session.run("CREATE INDEX ON :Node(building_id)")  # For query filtering

        with open(nodes_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            batch = []

            for row in reader:
                batch.append({
                    "id": row["id"],
                    "type": row["type"],
                    "name": row.get("name", ""),
                    "equipment_type": row.get("equipment_type", ""),
                    "building_id": row.get("building_id", ""),
                })

                if len(batch) >= batch_size:
                    with self.driver.session() as session:
                        session.run(
                            "UNWIND $batch AS row "
                            "CREATE (n:Node {id: row.id, type: row.type, "
                            "name: row.name, equipment_type: row.equipment_type, "
                            "building_id: row.building_id})",
                            batch=batch
                        )
                    total += len(batch)
                    batch.clear()
                    elapsed = time.time() - t0
                    print(f"\r  [LOAD] Nodes: {total:,} ({total/elapsed:.0f}/s)", end="", flush=True)

            if batch:
                with self.driver.session() as session:
                    session.run(
                        "UNWIND $batch AS row "
                        "CREATE (n:Node {id: row.id, type: row.type, "
                        "name: row.name, equipment_type: row.equipment_type, "
                        "building_id: row.building_id})",
                        batch=batch
                    )
                total += len(batch)

        print(f"\r  [LOAD] Nodes: {total:,} in {time.time() - t0:.1f}s          ")
        return total

    def load_edges(self, edges_file: Path, batch_size: int = 1000) -> int:
        """Load edges from CSV."""
        total = 0
        t0 = time.time()

        # Group edges by relationship type for efficient loading
        edges_by_type = {}
        with open(edges_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rel_type = row["rel_type"]
                if rel_type not in edges_by_type:
                    edges_by_type[rel_type] = []
                edges_by_type[rel_type].append({
                    "src": row["src_id"],
                    "dst": row["dst_id"]
                })

        for rel_type, edges in edges_by_type.items():
            for i in range(0, len(edges), batch_size):
                batch = edges[i:i + batch_size]
                with self.driver.session() as session:
                    session.run(
                        f"UNWIND $batch AS row "
                        f"MATCH (s:Node {{id: row.src}}) "
                        f"MATCH (d:Node {{id: row.dst}}) "
                        f"CREATE (s)-[:{rel_type}]->(d)",
                        batch=batch
                    )
                total += len(batch)

        print(f"  [LOAD] Edges: {total:,} in {time.time() - t0:.1f}s")
        return total

    def load_chunks(self, chunks_file: Path, batch_size: int = 500) -> int:
        """Load timeseries chunks for M1 scenario.

        Expected CSV format:
            point_id,date_day,timestamps,values
            point_123,2024-01-01,"[1704067200,...]","[1.2,1.3,...]"

        Creates ArchiveDay nodes linked to Point nodes via HAS_TIMESERIES.
        """
        import json

        total = 0
        t0 = time.time()

        with open(chunks_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            batch = []

            for row in reader:
                # Parse timestamps and values arrays from JSON string
                timestamps_str = row.get("timestamps", "[]")
                values_str = row.get("values", "[]")
                try:
                    timestamps = json.loads(timestamps_str) if timestamps_str else []
                    values = json.loads(values_str) if values_str else []
                except json.JSONDecodeError:
                    timestamps = []
                    values = []

                batch.append({
                    "point_id": row["point_id"],
                    "day": row["date_day"],
                    "timestamps": timestamps,
                    "values": values,
                })

                if len(batch) >= batch_size:
                    with self.driver.session() as session:
                        session.run(
                            "UNWIND $batch AS row "
                            "MATCH (p:Node {id: row.point_id}) "
                            "CREATE (a:ArchiveDay {point_id: row.point_id, day: row.day, timestamps: row.timestamps, values: row.values}) "
                            "CREATE (p)-[:HAS_TIMESERIES]->(a)",
                            batch=batch
                        )
                    total += len(batch)
                    batch.clear()
                    elapsed = time.time() - t0
                    print(f"\r  [LOAD] Chunks: {total:,} ({total/elapsed:.0f}/s)", end="", flush=True)

            if batch:
                with self.driver.session() as session:
                    session.run(
                        "UNWIND $batch AS row "
                        "MATCH (p:Node {id: row.point_id}) "
                        "CREATE (a:ArchiveDay {point_id: row.point_id, day: row.day, timestamps: row.timestamps, values: row.values}) "
                        "CREATE (p)-[:HAS_TIMESERIES]->(a)",
                        batch=batch
                    )
                total += len(batch)

        print(f"\r  [LOAD] Chunks: {total:,} in {time.time() - t0:.1f}s          ")
        return total

    def execute_query(self, query: str) -> Tuple[int, float]:
        """Execute a Cypher query and return (row_count, latency_ms)."""
        t0 = time.perf_counter()
        with self.driver.session() as session:
            result = list(session.run(query))
            latency_ms = (time.perf_counter() - t0) * 1000
            return len(result), latency_ms

    def get_executor(self) -> Callable[[str], Tuple[int, float]]:
        """Return query executor function."""
        return self.execute_query
