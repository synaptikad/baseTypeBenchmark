"""Exporter v2.0 - Export dataset to multiple formats.

Exports the generated dataset to:
- Parquet (pivot format)
- CSV for PostgreSQL
- CSV for PostgreSQL JSONB
- CSV for Memgraph
- N-Triples for Oxigraph
- Timeseries CSV for TimescaleDB
"""

import hashlib
import json
import tempfile
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

import pandas as pd

from .generator_v2 import (
    Dataset, Node, Edge, Point, TSChunk, DailyAggregate,
    generate_timeseries, generate_chunks, generate_daily_aggregates,
    CHUNK_SIZE
)


# =============================================================================
# PARQUET EXPORT (PIVOT FORMAT)
# =============================================================================

def export_parquet(
    dataset: Dataset,
    output_dir: Path,
    duration_days: int = 30,
    include_timeseries: bool = True
) -> None:
    """Export dataset to Parquet pivot format.

    Args:
        dataset: Generated dataset
        output_dir: Output directory
        duration_days: Duration for timeseries generation
        include_timeseries: Whether to generate timeseries
    """
    import random

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export nodes
    nodes_data = []
    for node in dataset.nodes:
        nodes_data.append({
            "id": node.id,
            "type": node.type,
            "name": node.properties.get("name", ""),
            "properties": json.dumps(node.properties)
        })

    nodes_df = pd.DataFrame(nodes_data)
    nodes_df.to_parquet(output_dir / "nodes.parquet", index=False)

    # Export edges
    edges_data = []
    for edge in dataset.edges:
        edges_data.append({
            "src_id": edge.src_id,
            "dst_id": edge.dst_id,
            "rel_type": edge.rel_type,
            "properties": json.dumps(edge.properties)
        })

    edges_df = pd.DataFrame(edges_data)
    edges_df.to_parquet(output_dir / "edges.parquet", index=False)

    # Export timeseries
    if include_timeseries and dataset.points:
        rng = random.Random(dataset.seed)
        ts_data = []

        for point_id, timestamp, value in generate_timeseries(
            dataset.points, duration_days, rng
        ):
            ts_data.append({
                "point_id": point_id,
                "timestamp": timestamp,
                "value": value
            })

        ts_df = pd.DataFrame(ts_data)
        ts_df.to_parquet(output_dir / "timeseries.parquet", index=False)

    # Compute and save fingerprint
    fingerprint = compute_fingerprint(output_dir)
    save_fingerprint(fingerprint, output_dir)

    print(f"Exported to Parquet: {output_dir}")
    print(f"  Nodes: {len(nodes_df)}")
    print(f"  Edges: {len(edges_df)}")
    if include_timeseries:
        print(f"  Timeseries: {len(ts_df)}")


def export_parquet_streaming(
    dataset: Dataset,
    output_dir: Path,
    duration_days: int = 30,
    batch_size: int = 100000
) -> None:
    """Export dataset to Parquet with streaming for large datasets.

    Args:
        dataset: Generated dataset
        output_dir: Output directory
        duration_days: Duration for timeseries generation
        batch_size: Number of timeseries rows per batch
    """
    import random
    import pyarrow as pa
    import pyarrow.parquet as pq

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export nodes and edges (same as regular export)
    nodes_data = [
        {"id": n.id, "type": n.type, "name": n.properties.get("name", ""),
         "properties": json.dumps(n.properties)}
        for n in dataset.nodes
    ]
    pd.DataFrame(nodes_data).to_parquet(output_dir / "nodes.parquet", index=False)

    edges_data = [
        {"src_id": e.src_id, "dst_id": e.dst_id, "rel_type": e.rel_type,
         "properties": json.dumps(e.properties)}
        for e in dataset.edges
    ]
    pd.DataFrame(edges_data).to_parquet(output_dir / "edges.parquet", index=False)

    # Stream timeseries
    rng = random.Random(dataset.seed)
    ts_path = output_dir / "timeseries.parquet"

    schema = pa.schema([
        ("point_id", pa.string()),
        ("timestamp", pa.timestamp("us")),
        ("value", pa.float64())
    ])

    writer = pq.ParquetWriter(ts_path, schema)
    batch = []
    total_rows = 0

    for point_id, timestamp, value in generate_timeseries(
        dataset.points, duration_days, rng
    ):
        batch.append({"point_id": point_id, "timestamp": timestamp, "value": value})

        if len(batch) >= batch_size:
            table = pa.Table.from_pydict({
                "point_id": [r["point_id"] for r in batch],
                "timestamp": [r["timestamp"] for r in batch],
                "value": [r["value"] for r in batch]
            }, schema=schema)
            writer.write_table(table)
            total_rows += len(batch)
            batch = []
            print(f"  Written {total_rows:,} timeseries rows...", end="\r")

    # Write remaining batch
    if batch:
        table = pa.Table.from_pydict({
            "point_id": [r["point_id"] for r in batch],
            "timestamp": [r["timestamp"] for r in batch],
            "value": [r["value"] for r in batch]
        }, schema=schema)
        writer.write_table(table)
        total_rows += len(batch)

    writer.close()

    print(f"\nExported to Parquet (streaming): {output_dir}")
    print(f"  Nodes: {len(nodes_data)}")
    print(f"  Edges: {len(edges_data)}")
    print(f"  Timeseries: {total_rows:,}")


# =============================================================================
# POSTGRESQL CSV EXPORT
# =============================================================================

def export_postgresql_csv(parquet_dir: Path, output_dir: Path) -> None:
    """Export Parquet to PostgreSQL CSV format.

    Args:
        parquet_dir: Directory containing Parquet files
        output_dir: Output directory for CSV files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read Parquet
    nodes_df = pd.read_parquet(parquet_dir / "nodes.parquet")
    edges_df = pd.read_parquet(parquet_dir / "edges.parquet")

    # Expand node properties to columns
    nodes_expanded = []
    for _, row in nodes_df.iterrows():
        props = json.loads(row["properties"]) if row["properties"] else {}
        node_row = {
            "id": row["id"],
            "type": row["type"],
            "name": row.get("name", props.get("name", "")),
            "domain": props.get("domain", ""),
            "equipment_type": props.get("equipment_type", ""),
            "space_type": props.get("space_type", ""),
            "building_id": props.get("building_id", ""),
            "floor_id": props.get("floor_id", ""),
            "space_id": props.get("space_id", ""),
            "data": row["properties"]  # Keep JSON for flexibility
        }
        nodes_expanded.append(node_row)

    pd.DataFrame(nodes_expanded).to_csv(
        output_dir / "pg_nodes.csv", index=False
    )

    # Edges
    edges_df[["src_id", "dst_id", "rel_type"]].to_csv(
        output_dir / "pg_edges.csv", index=False
    )

    # Timeseries
    if (parquet_dir / "timeseries.parquet").exists():
        ts_df = pd.read_parquet(parquet_dir / "timeseries.parquet")
        ts_df.rename(columns={"timestamp": "time"}).to_csv(
            output_dir / "pg_timeseries.csv", index=False
        )

    print(f"Exported PostgreSQL CSV: {output_dir}")


def export_postgresql_jsonb_csv(parquet_dir: Path, output_dir: Path) -> None:
    """Export Parquet to PostgreSQL JSONB CSV format.

    Args:
        parquet_dir: Directory containing Parquet files
        output_dir: Output directory for CSV files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read Parquet
    nodes_df = pd.read_parquet(parquet_dir / "nodes.parquet")
    edges_df = pd.read_parquet(parquet_dir / "edges.parquet")

    # Nodes with JSONB properties
    nodes_df[["id", "type", "name", "properties"]].to_csv(
        output_dir / "pg_jsonb_nodes.csv", index=False
    )

    # Edges with JSONB properties
    edges_df.to_csv(output_dir / "pg_jsonb_edges.csv", index=False)

    # Timeseries (same format)
    if (parquet_dir / "timeseries.parquet").exists():
        ts_df = pd.read_parquet(parquet_dir / "timeseries.parquet")
        ts_df.rename(columns={"timestamp": "time"}).to_csv(
            output_dir / "pg_timeseries.csv", index=False
        )

    print(f"Exported PostgreSQL JSONB CSV: {output_dir}")


# =============================================================================
# MEMGRAPH CSV EXPORT
# =============================================================================

def export_memgraph_csv(parquet_dir: Path, output_dir: Path) -> None:
    """Export Parquet to Memgraph CSV format.

    Args:
        parquet_dir: Directory containing Parquet files
        output_dir: Output directory for CSV files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read Parquet
    nodes_df = pd.read_parquet(parquet_dir / "nodes.parquet")
    edges_df = pd.read_parquet(parquet_dir / "edges.parquet")

    # Nodes for Memgraph
    nodes_mg = []
    for _, row in nodes_df.iterrows():
        props = json.loads(row["properties"]) if row["properties"] else {}
        node_row = {
            "id": row["id"],
            "type": row["type"],
            "name": row.get("name", props.get("name", "")),
            "equipment_type": props.get("equipment_type", ""),
            "space_type": props.get("space_type", ""),
            "domain": props.get("domain", ""),
            "building_id": props.get("building_id", ""),
            "floor_id": props.get("floor_id", ""),
            "space_id": props.get("space_id", ""),
        }
        nodes_mg.append(node_row)

    pd.DataFrame(nodes_mg).to_csv(output_dir / "mg_nodes.csv", index=False)

    # Edges
    edges_df[["src_id", "dst_id", "rel_type"]].to_csv(
        output_dir / "mg_edges.csv", index=False
    )

    # Timeseries for TimescaleDB
    if (parquet_dir / "timeseries.parquet").exists():
        ts_df = pd.read_parquet(parquet_dir / "timeseries.parquet")
        ts_df.rename(columns={"timestamp": "time"}).to_csv(
            output_dir / "timeseries.csv", index=False
        )

    print(f"Exported Memgraph CSV: {output_dir}")


def export_memgraph_chunks_csv(
    parquet_dir: Path,
    output_dir: Path,
    chunk_size: int = CHUNK_SIZE
) -> None:
    """Export timeseries as chunks for M1 (in-memory chunks).

    Args:
        parquet_dir: Directory containing Parquet files
        output_dir: Output directory for CSV files
        chunk_size: Number of values per chunk
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ts_df = pd.read_parquet(parquet_dir / "timeseries.parquet")

    chunks_data = []

    # Group by point_id
    for point_id, group in ts_df.groupby("point_id"):
        samples = list(zip(group["timestamp"], group["value"]))
        samples.sort(key=lambda x: x[0])

        for chunk in generate_chunks(point_id, samples):
            chunks_data.append({
                "point_id": chunk.point_id,
                "chunk_idx": chunk.chunk_idx,
                "start_ts": chunk.start_ts,
                "freq_sec": chunk.freq_sec,
                "values": json.dumps(chunk.values)
            })

    pd.DataFrame(chunks_data).to_csv(
        output_dir / "mg_chunks.csv", index=False
    )

    print(f"Exported Memgraph chunks: {len(chunks_data)} chunks")


# =============================================================================
# OXIGRAPH N-TRIPLES EXPORT
# =============================================================================

def export_ntriples(parquet_dir: Path, output_dir: Path) -> None:
    """Export Parquet to N-Triples format for Oxigraph.

    Args:
        parquet_dir: Directory containing Parquet files
        output_dir: Output directory for N-Triples file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes_df = pd.read_parquet(parquet_dir / "nodes.parquet")
    edges_df = pd.read_parquet(parquet_dir / "edges.parquet")

    # Prefixes
    prefixes = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "brick": "https://brickschema.org/schema/Brick#",
        "btb": "http://basetype-benchmark.org/",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
    }

    # Type mappings
    type_mapping = {
        "Site": "brick:Site",
        "Building": "brick:Building",
        "Floor": "brick:Floor",
        "Space": "brick:Space",
        "Equipment": "brick:Equipment",
        "Point": "brick:Point",
        "Tenant": "btb:Tenant",
    }

    # Relation mappings
    rel_mapping = {
        "CONTAINS": "brick:hasPart",
        "LOCATED_IN": "brick:isLocationOf",
        "HAS_POINT": "brick:hasPoint",
        "FEEDS": "brick:feeds",
        "SERVES": "btb:serves",
        "HAS_PART": "brick:hasPart",
        "OCCUPIES": "btb:occupies",
    }

    triples = []

    def uri(id_str: str) -> str:
        return f"<urn:{id_str}>"

    def literal(value: str, datatype: str = None) -> str:
        escaped = value.replace('"', '\\"').replace('\n', '\\n')
        if datatype:
            return f'"{escaped}"^^<{prefixes["xsd"]}{datatype}>'
        return f'"{escaped}"'

    # Export nodes
    for _, row in nodes_df.iterrows():
        node_uri = uri(row["id"])
        node_type = type_mapping.get(row["type"], f"btb:{row['type']}")

        # Type triple
        triples.append(f'{node_uri} <{prefixes["rdf"]}type> <{node_type.replace("brick:", prefixes["brick"]).replace("btb:", prefixes["btb"])}> .')

        # Label
        name = row.get("name", "")
        if name:
            triples.append(f'{node_uri} <{prefixes["rdfs"]}label> {literal(name)} .')

        # Properties
        props = json.loads(row["properties"]) if row["properties"] else {}
        for key, value in props.items():
            if key in ("name",):
                continue
            if isinstance(value, str) and value:
                triples.append(f'{node_uri} <{prefixes["btb"]}{key}> {literal(value)} .')

    # Export edges
    for _, row in edges_df.iterrows():
        src_uri = uri(row["src_id"])
        dst_uri = uri(row["dst_id"])
        rel = rel_mapping.get(row["rel_type"], f"btb:{row['rel_type'].lower()}")
        rel_uri = rel.replace("brick:", prefixes["brick"]).replace("btb:", prefixes["btb"])
        triples.append(f'{src_uri} <{rel_uri}> {dst_uri} .')

    # Write to file
    with open(output_dir / "graph.nt", "w", encoding="utf-8") as f:
        f.write("\n".join(triples))

    print(f"Exported N-Triples: {len(triples)} triples")


def export_oxigraph_chunks_ntriples(
    parquet_dir: Path,
    output_dir: Path,
    chunk_size: int = CHUNK_SIZE
) -> None:
    """Export timeseries chunks as N-Triples for O1.

    Args:
        parquet_dir: Directory containing Parquet files
        output_dir: Output directory
        chunk_size: Number of values per chunk
    """
    output_dir = Path(output_dir)

    ts_df = pd.read_parquet(parquet_dir / "timeseries.parquet")

    prefixes = {
        "ts": "http://example.org/ts/",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
    }

    triples = []

    def uri(id_str: str) -> str:
        return f"<urn:{id_str}>"

    def literal(value, datatype: str) -> str:
        return f'"{value}"^^<{prefixes["xsd"]}{datatype}>'

    # Generate chunks
    for point_id, group in ts_df.groupby("point_id"):
        samples = list(zip(group["timestamp"], group["value"]))
        samples.sort(key=lambda x: x[0])

        point_uri = uri(point_id)

        for chunk in generate_chunks(point_id, samples):
            chunk_uri = uri(f"chunk_{point_id}_{chunk.chunk_idx}")

            triples.append(f'{point_uri} <{prefixes["ts"]}hasChunk> {chunk_uri} .')
            triples.append(f'{chunk_uri} <{prefixes["ts"]}chunkIdx> {literal(chunk.chunk_idx, "integer")} .')
            triples.append(f'{chunk_uri} <{prefixes["ts"]}startTs> {literal(chunk.start_ts, "integer")} .')
            triples.append(f'{chunk_uri} <{prefixes["ts"]}freqSec> {literal(chunk.freq_sec, "integer")} .')
            triples.append(f'{chunk_uri} <{prefixes["ts"]}values> {literal(json.dumps(chunk.values), "string")} .')

    # Write to file
    with open(output_dir / "chunks.nt", "w", encoding="utf-8") as f:
        f.write("\n".join(triples))

    print(f"Exported O1 chunks N-Triples: {len(triples)} triples")


def export_oxigraph_aggregates_ntriples(
    parquet_dir: Path,
    output_dir: Path
) -> None:
    """Export daily aggregates as N-Triples for O1.

    Args:
        parquet_dir: Directory containing Parquet files
        output_dir: Output directory
    """
    output_dir = Path(output_dir)

    ts_df = pd.read_parquet(parquet_dir / "timeseries.parquet")

    prefixes = {
        "ts": "http://example.org/ts/",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
    }

    triples = []

    def uri(id_str: str) -> str:
        return f"<urn:{id_str}>"

    def literal(value, datatype: str) -> str:
        return f'"{value}"^^<{prefixes["xsd"]}{datatype}>'

    # Generate daily aggregates
    for point_id, group in ts_df.groupby("point_id"):
        samples = list(zip(group["timestamp"], group["value"]))

        point_uri = uri(point_id)

        for agg in generate_daily_aggregates(point_id, samples):
            agg_uri = uri(f"agg_{point_id}_{agg.date.replace('-', '')}")

            triples.append(f'{point_uri} <{prefixes["ts"]}hasDailyAgg> {agg_uri} .')
            triples.append(f'{agg_uri} <{prefixes["ts"]}date> {literal(agg.date, "date")} .')
            triples.append(f'{agg_uri} <{prefixes["ts"]}avg> {literal(agg.avg, "float")} .')
            triples.append(f'{agg_uri} <{prefixes["ts"]}min> {literal(agg.min_val, "float")} .')
            triples.append(f'{agg_uri} <{prefixes["ts"]}max> {literal(agg.max_val, "float")} .')
            triples.append(f'{agg_uri} <{prefixes["ts"]}count> {literal(agg.count, "integer")} .')

    # Write to file
    with open(output_dir / "aggregates.nt", "w", encoding="utf-8") as f:
        f.write("\n".join(triples))

    print(f"Exported O1 aggregates N-Triples: {len(triples)} triples")


# =============================================================================
# FINGERPRINT
# =============================================================================

def compute_fingerprint(parquet_dir: Path) -> dict:
    """Compute a deterministic fingerprint of the dataset.

    Args:
        parquet_dir: Directory containing Parquet files

    Returns:
        Fingerprint dictionary
    """
    parquet_dir = Path(parquet_dir)

    nodes_df = pd.read_parquet(parquet_dir / "nodes.parquet")
    edges_df = pd.read_parquet(parquet_dir / "edges.parquet")

    # Counts
    counts = {
        "nodes": len(nodes_df),
        "edges": len(edges_df),
        "node_types": dict(sorted(nodes_df["type"].value_counts().items())),
        "edge_types": dict(sorted(edges_df["rel_type"].value_counts().items())),
    }

    # Timeseries counts
    ts_path = parquet_dir / "timeseries.parquet"
    if ts_path.exists():
        ts_df = pd.read_parquet(ts_path)
        counts["timeseries"] = len(ts_df)

    # Structural hash
    node_ids = "\n".join(sorted(nodes_df["id"].tolist()))
    edge_keys = "\n".join(sorted(
        f"{row['src_id']}|{row['rel_type']}|{row['dst_id']}"
        for _, row in edges_df.iterrows()
    ))

    struct_hash = hashlib.sha256(
        (node_ids + edge_keys).encode("utf-8")
    ).hexdigest()[:16]

    # Timeseries hash
    ts_hash = None
    if ts_path.exists():
        ts_df = pd.read_parquet(ts_path)
        ts_sorted = ts_df.sort_values(["point_id", "timestamp"])
        ts_values = ts_sorted["value"].round(6).astype(str).str.cat(sep="\n")
        ts_hash = hashlib.sha256(ts_values.encode("utf-8")).hexdigest()[:16]

    return {
        "version": "2.0",
        "seed": 42,
        "counts": counts,
        "struct_hash": struct_hash,
        "ts_hash": ts_hash,
    }


def save_fingerprint(fingerprint: dict, output_dir: Path) -> None:
    """Save fingerprint to JSON file.

    Args:
        fingerprint: Fingerprint dictionary
        output_dir: Output directory
    """
    with open(output_dir / "fingerprint.json", "w", encoding="utf-8") as f:
        json.dump(fingerprint, f, indent=2, sort_keys=True)


# =============================================================================
# UNIFIED EXPORT
# =============================================================================

def export_for_target(
    parquet_dir: Path,
    target: str,
    output_dir: Path
) -> None:
    """Export Parquet to a specific target format.

    Args:
        parquet_dir: Directory containing Parquet files
        target: Target format (postgresql, postgresql_jsonb, memgraph, oxigraph)
        output_dir: Output directory
    """
    parquet_dir = Path(parquet_dir)
    output_dir = Path(output_dir)

    if target == "postgresql":
        export_postgresql_csv(parquet_dir, output_dir)

    elif target == "postgresql_jsonb":
        export_postgresql_jsonb_csv(parquet_dir, output_dir)

    elif target == "memgraph":
        export_memgraph_csv(parquet_dir, output_dir)

    elif target == "memgraph_m1":
        export_memgraph_csv(parquet_dir, output_dir)
        export_memgraph_chunks_csv(parquet_dir, output_dir)

    elif target == "oxigraph":
        export_ntriples(parquet_dir, output_dir)

    elif target == "oxigraph_o1":
        export_ntriples(parquet_dir, output_dir)
        export_oxigraph_chunks_ntriples(parquet_dir, output_dir)
        export_oxigraph_aggregates_ntriples(parquet_dir, output_dir)

    else:
        raise ValueError(f"Unknown target: {target}")


def export_all_targets(parquet_dir: Path, base_output_dir: Path) -> None:
    """Export Parquet to all target formats.

    Args:
        parquet_dir: Directory containing Parquet files
        base_output_dir: Base output directory
    """
    targets = [
        "postgresql",
        "postgresql_jsonb",
        "memgraph",
        "memgraph_m1",
        "oxigraph",
        "oxigraph_o1",
    ]

    for target in targets:
        output_dir = base_output_dir / target
        print(f"\n=== Exporting to {target} ===")
        export_for_target(parquet_dir, target, output_dir)


# =============================================================================
# CLI
# =============================================================================

def main():
    """Command-line interface for the exporter."""
    import argparse

    parser = argparse.ArgumentParser(description="Export dataset to various formats")
    parser.add_argument("parquet_dir", type=Path, help="Directory containing Parquet files")
    parser.add_argument("--target", choices=[
        "postgresql", "postgresql_jsonb", "memgraph", "memgraph_m1",
        "oxigraph", "oxigraph_o1", "all"
    ], default="all", help="Target format")
    parser.add_argument("--output", type=Path, default=Path("output"),
                        help="Output directory")

    args = parser.parse_args()

    if args.target == "all":
        export_all_targets(args.parquet_dir, args.output)
    else:
        export_for_target(args.parquet_dir, args.target, args.output)


if __name__ == "__main__":
    main()
