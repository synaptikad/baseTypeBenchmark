"""
P1 Extractor - PostgreSQL Relationnel + TimescaleDB
Benchmark BaseType V3

Produit:
- CSV par table (sites.csv, buildings.csv, equipment.csv, etc.)
- edges.csv pour les relations
- timeseries.csv pour les données temporelles
- schema_p1.sql pour la création des tables
- load_p1.sql pour les commandes COPY

IMPORTANT: JSONB ignoré → Q14-Q19 IMPOSSIBLE (cohérent avec le benchmark)
"""

from pathlib import Path
from typing import List, Dict, Any

from .base import (
    BaseExtractor, ExportResult,
    node_to_relational, write_csv
)


class P1Extractor(BaseExtractor):
    """
    Extracteur pour P1 (PostgreSQL relationnel).

    Produit:
    - CSV par table (sites, buildings, floors, spaces, equipment, points, etc.)
    - edges.csv pour les relations
    - timeseries.csv pour les données temporelles
    - schema_p1.sql pour la création des tables
    - load_p1.sql pour les commandes COPY
    """

    # Mapping type → nom table
    TYPE_TO_TABLE = {
        "site": "sites",
        "building": "buildings",
        "floor": "floors",
        "space": "spaces",
        "equipment": "equipment",
        "point": "points",
        "tenant": "tenants",
        "zone": "zones",
        "contract": "contracts",
        "ticket": "tickets",
    }

    # Colonnes par table (définit l'ordre et les colonnes exportées)
    TABLE_COLUMNS = {
        "sites": ["id", "name", "address"],
        "buildings": ["id", "name", "site_id", "address", "gross_area_m2"],
        "floors": ["id", "name", "building_id", "floor_type", "level_index"],
        "spaces": ["id", "name", "floor_id", "building_id", "space_type", "area_m2", "capacity"],
        "equipment": ["id", "name", "equipment_type", "domain", "building_id", "floor_id", "space_id"],
        "points": ["id", "name", "quantity", "unit", "equipment_id", "building_id", "frequency"],
        "tenants": ["id", "name", "contract_start", "contract_end"],
        "zones": ["id", "name", "zone_type", "description"],
        "contracts": ["id", "name", "contract_type", "start_date", "end_date", "provider"],
    }

    @property
    def paradigm_name(self) -> str:
        return "p1"

    def extract_nodes(self) -> List[Path]:
        """Extrait les noeuds vers des CSV par type"""
        files = []

        # Grouper les noeuds par type
        nodes_by_type: Dict[str, List] = {}
        for node in self.dataset.nodes:
            node_type = node.type.lower()
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(node)

        for node_type, nodes in nodes_by_type.items():
            table_name = self.TYPE_TO_TABLE.get(node_type, f"{node_type}s")
            columns = self.TABLE_COLUMNS.get(table_name)

            if columns is None:
                print(f"  WARN: No column mapping for {table_name}, skipping")
                continue

            rows = []
            for node in nodes:
                row = node_to_relational(node, node_type)
                rows.append(row)

            filepath = self.output_dir / f"{table_name}.csv"
            write_csv(filepath, rows, columns)
            files.append(filepath)
            print(f"  Created {filepath} ({len(rows)} rows)")

        return files

    def extract_edges(self) -> List[Path]:
        """Extrait les relations vers edges.csv"""
        rows = []
        for edge in self.dataset.edges:
            rows.append({
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "rel_type": edge.rel_type
            })

        filepath = self.output_dir / "edges.csv"
        write_csv(filepath, rows, ["source_id", "target_id", "rel_type"])
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
            "-- Voir fichier schema_p1.sql",
            "\\i schema_p1.sql"
        ]

    def get_load_commands(self) -> List[str]:
        """Retourne les commandes COPY pour bulk loading"""
        tables = [
            "sites", "buildings", "floors", "spaces",
            "equipment", "points", "tenants", "zones", "contracts"
        ]

        commands = ["-- Bulk loading P1"]
        for table in tables:
            csv_file = self.output_dir / f"{table}.csv"
            if csv_file.exists():
                commands.append(
                    f"\\COPY {table} FROM '{csv_file.absolute()}' WITH (FORMAT csv, HEADER true);"
                )

        # Edges
        commands.append(
            f"\\COPY edges(source_id, target_id, rel_type) FROM '{self.output_dir / 'edges.csv'}' WITH (FORMAT csv, HEADER true);"
        )

        # Timeseries
        commands.append(
            f"\\COPY timeseries FROM '{self.output_dir / 'timeseries.csv'}' WITH (FORMAT csv, HEADER true);"
        )

        return commands

    def export_schema_file(self) -> Path:
        """Exporte le fichier schema SQL"""
        schema_sql = '''-- Schema P1 : PostgreSQL Relationnel + TimescaleDB
-- Benchmark BaseType V3
-- Genere par P1Extractor

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Sites
CREATE TABLE IF NOT EXISTS sites (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(512)
);

-- Buildings
CREATE TABLE IF NOT EXISTS buildings (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    site_id VARCHAR(64) REFERENCES sites(id),
    address VARCHAR(512),
    gross_area_m2 FLOAT
);

-- Floors
CREATE TABLE IF NOT EXISTS floors (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    building_id VARCHAR(64) REFERENCES buildings(id),
    floor_type VARCHAR(32),
    level_index INTEGER
);

-- Spaces
CREATE TABLE IF NOT EXISTS spaces (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    floor_id VARCHAR(64) REFERENCES floors(id),
    building_id VARCHAR(64) REFERENCES buildings(id),
    space_type VARCHAR(64),
    area_m2 FLOAT,
    capacity INTEGER
);

-- Equipment
CREATE TABLE IF NOT EXISTS equipment (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    equipment_type VARCHAR(64) NOT NULL,
    domain VARCHAR(32) NOT NULL,
    building_id VARCHAR(64) REFERENCES buildings(id),
    floor_id VARCHAR(64) REFERENCES floors(id),
    space_id VARCHAR(64) REFERENCES spaces(id)
);

-- Points
CREATE TABLE IF NOT EXISTS points (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    quantity VARCHAR(32) NOT NULL,
    unit VARCHAR(32) NOT NULL,
    equipment_id VARCHAR(64) REFERENCES equipment(id),
    building_id VARCHAR(64) REFERENCES buildings(id),
    frequency VARCHAR(32)
);

-- Tenants
CREATE TABLE IF NOT EXISTS tenants (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contract_start DATE,
    contract_end DATE
);

-- Zones
CREATE TABLE IF NOT EXISTS zones (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    zone_type VARCHAR(32),
    description TEXT
);

-- Contracts
CREATE TABLE IF NOT EXISTS contracts (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contract_type VARCHAR(32),
    start_date DATE,
    end_date DATE,
    provider VARCHAR(255)
);

-- Edges (relations)
CREATE TABLE IF NOT EXISTS edges (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(64) NOT NULL,
    target_id VARCHAR(64) NOT NULL,
    rel_type VARCHAR(32) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_rel_type ON edges(rel_type);
CREATE INDEX IF NOT EXISTS idx_edges_source_rel ON edges(source_id, rel_type);
CREATE INDEX IF NOT EXISTS idx_edges_target_rel ON edges(target_id, rel_type);

-- Timeseries (hypertable)
CREATE TABLE IF NOT EXISTS timeseries (
    time TIMESTAMPTZ NOT NULL,
    point_id VARCHAR(64) NOT NULL,
    value DOUBLE PRECISION NOT NULL
);
SELECT create_hypertable('timeseries', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_timeseries_point ON timeseries(point_id, time DESC);
'''
        filepath = self.output_dir / "schema_p1.sql"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(schema_sql)
        print(f"  Created {filepath}")
        return filepath

    def export_load_script(self) -> Path:
        """Exporte le script de chargement"""
        commands = self.get_load_commands()
        filepath = self.output_dir / "load_p1.sql"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("-- Script de chargement P1\n")
            f.write("-- Executer: psql -d benchmark -f load_p1.sql\n\n")
            for cmd in commands:
                f.write(cmd + "\n")
        print(f"  Created {filepath}")
        return filepath


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    from pathlib import Path

    output_dir = Path("data/export/p1")
    print(f"P1 Extractor - Export vers {output_dir}")

    extractor = P1Extractor(output_dir)
    extractor.load_dataset()

    # Export schema
    print("\n=== SCHEMA ===")
    schema_file = extractor.export_schema_file()

    # Export donnees
    print("\n=== EXPORT DONNEES ===")
    result = extractor.export_all()

    print(f"\n=== RESULTAT P1 ===")
    print(f"Nodes: {result.total_nodes}")
    print(f"Edges: {result.total_edges}")
    print(f"Timeseries: {result.total_timeseries}")
    print(f"Files: {len(result.files_created)}")

    # Export script de chargement
    print("\n=== LOAD SCRIPT ===")
    load_file = extractor.export_load_script()

    print("\n=== COMMANDES DE CHARGEMENT ===")
    for cmd in result.load_commands:
        print(cmd)

    print("\nP1 extraction complete.")
    print("\nAGENT-EXTRACT-P1 TERMINE")
