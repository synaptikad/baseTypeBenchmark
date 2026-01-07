"""
P2 Extractor - PostgreSQL JSONB + TimescaleDB
Benchmark BaseType V3
"""

from pathlib import Path
from typing import List, Dict, Any
import csv
import json

from .base import (
    BaseExtractor, ExportResult,
    merge_to_jsonb, write_csv
)


class P2Extractor(BaseExtractor):
    """
    Extracteur pour P2 (PostgreSQL JSONB).

    Produit:
    - nodes.csv avec colonne data en JSON string
    - edges.csv pour les relations
    - timeseries.csv pour les données temporelles
    - schema_p2.sql pour la création des tables
    - load_p2.sql pour les commandes COPY
    """

    @property
    def paradigm_name(self) -> str:
        return "p2"

    def extract_nodes(self) -> List[Path]:
        """Extrait tous les nœuds vers nodes.csv avec JSONB"""
        rows = []

        for node in self.dataset.nodes:
            # Fusionner tout en JSONB
            data = merge_to_jsonb(node)

            rows.append({
                "id": node.id,
                "node_type": node.type,
                "name": node.name,
                "data": json.dumps(data, ensure_ascii=False, default=str)
            })

        filepath = self.output_dir / "nodes.csv"
        write_csv(filepath, rows, ["id", "node_type", "name", "data"])
        print(f"  Created {filepath} ({len(rows)} rows)")
        return [filepath]

    def extract_edges(self) -> List[Path]:
        """Extrait les relations vers edges.csv"""
        rows = []
        for edge in self.dataset.edges:
            rows.append({
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "rel_type": edge.rel_type,
                "properties": json.dumps(edge.properties, ensure_ascii=False) if edge.properties else "{}"
            })

        filepath = self.output_dir / "edges.csv"
        write_csv(filepath, rows, ["source_id", "target_id", "rel_type", "properties"])
        print(f"  Created {filepath} ({len(rows)} rows)")
        return [filepath]

    def extract_timeseries(self) -> List[Path]:
        """Extrait les timeseries vers timeseries.csv"""
        rows = []
        for ts in self.dataset.timeseries:
            rows.append({
                "time": ts.timestamp.isoformat(),
                "point_id": ts.point_id,
                "value": ts.value
            })

        filepath = self.output_dir / "timeseries.csv"
        write_csv(filepath, rows, ["time", "point_id", "value"])
        print(f"  Created {filepath} ({len(rows)} rows)")
        return [filepath]

    def get_schema_commands(self) -> List[str]:
        """Retourne le SQL de création du schema"""
        return [
            "-- Voir fichier schema_p2.sql",
            "\\i schema_p2.sql"
        ]

    def get_load_commands(self) -> List[str]:
        """Retourne les commandes COPY pour bulk loading"""
        return [
            "-- Bulk loading P2",
            f"\\COPY nodes FROM '{self.output_dir.absolute()}/nodes.csv' WITH (FORMAT csv, HEADER true);",
            f"\\COPY edges(source_id, target_id, rel_type, properties) FROM '{self.output_dir.absolute()}/edges.csv' WITH (FORMAT csv, HEADER true);",
            f"\\COPY timeseries FROM '{self.output_dir.absolute()}/timeseries.csv' WITH (FORMAT csv, HEADER true);",
        ]

    def export_schema_file(self) -> Path:
        """Exporte le fichier schema SQL"""
        schema_sql = '''-- Schema P2 : PostgreSQL JSONB + TimescaleDB
-- Benchmark BaseType V3
-- Généré par P2Extractor

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Table nodes (tous les types en une seule table)
CREATE TABLE IF NOT EXISTS nodes (
    id VARCHAR(64) PRIMARY KEY,
    node_type VARCHAR(32) NOT NULL,
    name VARCHAR(255) NOT NULL,
    data JSONB NOT NULL DEFAULT '{}'
);

-- Index de base
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_data_gin ON nodes USING GIN (data);

-- Index pour queries fréquentes (Q1-Q5)
CREATE INDEX IF NOT EXISTS idx_nodes_equipment_type ON nodes((data->>'equipment_type')) WHERE node_type = 'Equipment';
CREATE INDEX IF NOT EXISTS idx_nodes_building_id ON nodes((data->>'building_id'));
CREATE INDEX IF NOT EXISTS idx_nodes_domain ON nodes((data->>'domain')) WHERE node_type = 'Equipment';
CREATE INDEX IF NOT EXISTS idx_nodes_quantity ON nodes((data->>'quantity')) WHERE node_type = 'Point';
CREATE INDEX IF NOT EXISTS idx_nodes_space_type ON nodes((data->>'space_type')) WHERE node_type = 'Space';
CREATE INDEX IF NOT EXISTS idx_nodes_floor_id ON nodes((data->>'floor_id'));
CREATE INDEX IF NOT EXISTS idx_nodes_equipment_id ON nodes((data->>'equipment_id')) WHERE node_type = 'Point';
CREATE INDEX IF NOT EXISTS idx_nodes_space_id ON nodes((data->>'space_id')) WHERE node_type = 'Equipment';

-- Index pour JSONB arrays (Q16, Q17)
CREATE INDEX IF NOT EXISTS idx_nodes_tags ON nodes USING GIN ((data->'tags'));
CREATE INDEX IF NOT EXISTS idx_nodes_capabilities ON nodes USING GIN ((data->'capabilities'));

-- Index pour nested JSONB (Q14, Q15, Q18)
CREATE INDEX IF NOT EXISTS idx_nodes_protocol_type ON nodes((data->'protocol'->>'type')) WHERE data->'protocol' IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nodes_protocol_device ON nodes((data->'protocol'->>'device_id')) WHERE data->'protocol' IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nodes_warranty ON nodes((data->'metadata'->>'warranty_end')) WHERE data->'metadata' IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nodes_calibration_next ON nodes((data->'calibration'->>'next_date')) WHERE data->'calibration' IS NOT NULL;

-- Table edges
CREATE TABLE IF NOT EXISTS edges (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(64) NOT NULL,
    target_id VARCHAR(64) NOT NULL,
    rel_type VARCHAR(32) NOT NULL,
    properties JSONB DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_rel_type ON edges(rel_type);
CREATE INDEX IF NOT EXISTS idx_edges_source_rel ON edges(source_id, rel_type);
CREATE INDEX IF NOT EXISTS idx_edges_target_rel ON edges(target_id, rel_type);

-- FK constraints (after data load for performance)
-- ALTER TABLE edges ADD CONSTRAINT fk_edges_source FOREIGN KEY (source_id) REFERENCES nodes(id);
-- ALTER TABLE edges ADD CONSTRAINT fk_edges_target FOREIGN KEY (target_id) REFERENCES nodes(id);

-- Table timeseries (hypertable)
CREATE TABLE IF NOT EXISTS timeseries (
    time TIMESTAMPTZ NOT NULL,
    point_id VARCHAR(64) NOT NULL,
    value DOUBLE PRECISION NOT NULL
);
SELECT create_hypertable('timeseries', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_timeseries_point ON timeseries(point_id, time DESC);
'''
        filepath = self.output_dir / "schema_p2.sql"
        with open(filepath, 'w') as f:
            f.write(schema_sql)
        return filepath

    def export_load_script(self) -> Path:
        """Exporte le script de chargement"""
        commands = self.get_load_commands()
        filepath = self.output_dir / "load_p2.sql"
        with open(filepath, 'w') as f:
            f.write("-- Script de chargement P2\n")
            f.write("-- Exécuter: psql -d benchmark -f load_p2.sql\n\n")
            for cmd in commands:
                f.write(cmd + "\n")
        return filepath

    def export_sample_queries(self) -> Path:
        """Exporte des exemples de queries JSONB pour validation"""
        queries = '''-- Exemples de queries JSONB P2
-- Pour validation du format de données

-- Q14: Protocol Query (BACnet device_id = 1234)
SELECT
    id AS point_id,
    name AS point_name,
    data->>'equipment_id' AS equipment_id,
    data->'protocol'->>'object_type' AS object_type,
    (data->'protocol'->>'object_instance')::integer AS object_instance
FROM nodes
WHERE node_type = 'Point'
  AND data->'protocol'->>'type' = 'BACnet'
  AND (data->'protocol'->>'device_id')::integer = 1234;

-- Q15: Warranty Expiry (90 jours)
SELECT
    id AS equipment_id,
    name,
    data->>'equipment_type' AS equipment_type,
    (data->'metadata'->>'warranty_end')::date AS warranty_end
FROM nodes
WHERE node_type = 'Equipment'
  AND data->'metadata'->>'warranty_end' IS NOT NULL
  AND (data->'metadata'->>'warranty_end')::date <= CURRENT_DATE + INTERVAL '90 days'
  AND (data->'metadata'->>'warranty_end')::date >= CURRENT_DATE;

-- Q16: Semantic Tag Search (brick:*)
SELECT
    id AS equipment_id,
    name,
    jsonb_array_elements_text(data->'tags') AS tag
FROM nodes
WHERE node_type = 'Equipment'
  AND data->'tags' IS NOT NULL
  AND EXISTS (
    SELECT 1 FROM jsonb_array_elements_text(data->'tags') t
    WHERE t LIKE 'brick:%'
  );

-- Q17: Capability Filter (humidity_control)
SELECT
    id AS equipment_id,
    name,
    data->>'equipment_type' AS equipment_type,
    data->'capabilities' AS all_capabilities
FROM nodes
WHERE node_type = 'Equipment'
  AND data->>'domain' = 'HVAC'
  AND data->'capabilities' @> '["humidity_control"]';
'''
        filepath = self.output_dir / "sample_queries_p2.sql"
        with open(filepath, 'w') as f:
            f.write(queries)
        return filepath


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='P2 Extractor - PostgreSQL JSONB')
    parser.add_argument('--input', type=str, required=True, help='Input directory with Parquet files')
    parser.add_argument('--output', type=str, required=True, help='Output directory for CSV files')
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    print(f"P2 Extractor - {input_dir} → {output_dir}")

    extractor = P2Extractor(output_dir, input_dir)
    extractor.load_dataset()

    # Export schema
    schema_file = extractor.export_schema_file()
    print(f"Schema: {schema_file}")

    # Export données
    result = extractor.export_all()

    print(f"\n=== RÉSULTAT P2 ===")
    print(f"Nodes: {result.total_nodes}")
    print(f"Edges: {result.total_edges}")
    print(f"Timeseries: {result.total_timeseries}")
    print(f"Files: {len(result.files_created)}")

    # Export scripts
    load_file = extractor.export_load_script()
    print(f"Load script: {load_file}")

    sample_file = extractor.export_sample_queries()
    print(f"Sample queries: {sample_file}")

    print("\n=== SAMPLE NODE DATA ===")
    import json
    with open(output_dir / "nodes.csv") as f:
        import csv
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if row['id'] == 'ahu_1':
                print(f"AHU_1 data:")
                print(json.dumps(json.loads(row['data']), indent=2))
                break

    print("\nP2 extraction complete.")
