"""
M1/M2 Extractor - Memgraph (Cypher) avec propriétés aplaties
Benchmark BaseType V3
"""

from pathlib import Path
from typing import List, Dict, Any
import csv
import json

from .base import (
    BaseExtractor, ExportResult,
    flatten_jsonb, write_csv
)


class M1M2Extractor(BaseExtractor):
    """
    Extracteur pour M1/M2 (Memgraph Cypher).

    Produit:
    - nodes.csv avec propriétés aplaties
    - edges.csv pour les relations
    - timeseries.csv pour M2 (ignoré par M1)
    - load_cypher.cql pour bulk loading
    - schema_memgraph.cql pour contraintes/index
    """

    @property
    def paradigm_name(self) -> str:
        return "m1m2"

    def extract_nodes(self) -> List[Path]:
        """Extrait les nœuds avec propriétés aplaties vers CSV"""

        # Collecter toutes les colonnes possibles
        all_columns = set(["id", "node_type", "name"])
        all_rows = []

        for node in self.dataset.nodes:
            flat = flatten_jsonb(node)
            all_rows.append(flat)
            all_columns.update(flat.keys())

        # Colonnes triées pour cohérence
        columns = ["id", "node_type", "name"] + sorted(
            [c for c in all_columns if c not in ["id", "node_type", "name"]]
        )

        # Convertir les listes en JSON strings pour CSV
        rows_for_csv = []
        for row in all_rows:
            csv_row = {}
            for col in columns:
                value = row.get(col)
                if isinstance(value, (list, dict)):
                    csv_row[col] = json.dumps(value, ensure_ascii=False)
                elif value is None:
                    csv_row[col] = ""
                else:
                    csv_row[col] = str(value)
            rows_for_csv.append(csv_row)

        filepath = self.output_dir / "nodes.csv"
        write_csv(filepath, rows_for_csv, columns)
        print(f"  Created {filepath} ({len(rows_for_csv)} rows, {len(columns)} columns)")

        # Sauvegarder la liste des colonnes pour le script Cypher
        self._node_columns = columns

        return [filepath]

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
        """Extrait les timeseries (pour M2 uniquement)"""
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
        print(f"  Note: timeseries.csv pour M2 (TimescaleDB), ignoré par M1")
        return [filepath]

    def get_schema_commands(self) -> List[str]:
        """Retourne les commandes Cypher de création de schema"""
        return [
            "// Contraintes d'unicité",
            "CREATE CONSTRAINT ON (n:Site) ASSERT n.id IS UNIQUE;",
            "CREATE CONSTRAINT ON (n:Building) ASSERT n.id IS UNIQUE;",
            "CREATE CONSTRAINT ON (n:Floor) ASSERT n.id IS UNIQUE;",
            "CREATE CONSTRAINT ON (n:Space) ASSERT n.id IS UNIQUE;",
            "CREATE CONSTRAINT ON (n:Equipment) ASSERT n.id IS UNIQUE;",
            "CREATE CONSTRAINT ON (n:Point) ASSERT n.id IS UNIQUE;",
            "CREATE CONSTRAINT ON (n:Tenant) ASSERT n.id IS UNIQUE;",
            "CREATE CONSTRAINT ON (n:Zone) ASSERT n.id IS UNIQUE;",
            "CREATE CONSTRAINT ON (n:Contract) ASSERT n.id IS UNIQUE;",
            "",
            "// Index pour queries fréquentes",
            "CREATE INDEX ON :Equipment(equipment_type);",
            "CREATE INDEX ON :Equipment(domain);",
            "CREATE INDEX ON :Equipment(building_id);",
            "CREATE INDEX ON :Point(quantity);",
            "CREATE INDEX ON :Point(equipment_id);",
            "CREATE INDEX ON :Space(space_type);",
            "CREATE INDEX ON :Space(building_id);",
            "",
            "// Index pour JSONB aplati",
            "CREATE INDEX ON :Equipment(protocol_device_id);",
            "CREATE INDEX ON :Equipment(metadata_warranty_end);",
            "CREATE INDEX ON :Point(protocol_device_id);",
            "CREATE INDEX ON :Point(calibration_next_date);",
        ]

    def get_load_commands(self) -> List[str]:
        """Retourne les commandes de chargement bulk"""
        csv_path = self.output_dir.absolute()

        return [
            f"// Bulk loading M1/M2 depuis {csv_path}",
            "",
            "// Charger les nœuds",
            f'LOAD CSV WITH HEADERS FROM "file:///{csv_path}/nodes.csv" AS row',
            "CALL {",
            "  WITH row",
            "  CALL apoc.create.node([row.node_type], {",
            "    id: row.id,",
            "    name: row.name,",
            "    // Propriétés de base",
            "    equipment_type: row.equipment_type,",
            "    domain: row.domain,",
            "    building_id: row.building_id,",
            "    floor_id: row.floor_id,",
            "    space_id: row.space_id,",
            "    quantity: row.quantity,",
            "    unit: row.unit,",
            "    equipment_id: row.equipment_id,",
            "    space_type: row.space_type,",
            "    // Propriétés aplaties",
            "    protocol_type: row.protocol_type,",
            "    protocol_device_id: toInteger(row.protocol_device_id),",
            "    metadata_warranty_end: row.metadata_warranty_end,",
            "    calibration_next_date: row.calibration_next_date,",
            "    // Listes (parsing JSON)",
            "    capabilities: apoc.convert.fromJsonList(row.capabilities),",
            "    tags: apoc.convert.fromJsonList(row.tags)",
            "  }) YIELD node",
            "  RETURN count(*)",
            "} IN TRANSACTIONS OF 1000 ROWS;",
            "",
            "// Charger les relations",
            f'LOAD CSV WITH HEADERS FROM "file:///{csv_path}/edges.csv" AS row',
            "CALL {",
            "  WITH row",
            "  MATCH (source {id: row.source_id})",
            "  MATCH (target {id: row.target_id})",
            "  CALL apoc.create.relationship(source, row.rel_type, {}, target) YIELD rel",
            "  RETURN count(*)",
            "} IN TRANSACTIONS OF 1000 ROWS;",
        ]

    def export_schema_file(self) -> Path:
        """Exporte le fichier schema Cypher"""
        commands = self.get_schema_commands()
        filepath = self.output_dir / "schema_memgraph.cql"
        with open(filepath, 'w') as f:
            f.write("// Schema Memgraph - Benchmark BaseType V3\n")
            f.write("// Exécuter: mgconsole < schema_memgraph.cql\n\n")
            for cmd in commands:
                f.write(cmd + "\n")
        return filepath

    def export_load_script_simple(self) -> Path:
        """
        Exporte un script de chargement simplifié (sans APOC).
        Plus compatible avec Memgraph standard.
        """
        csv_path = self.output_dir.absolute()

        # Grouper les nœuds par type
        nodes_by_type: Dict[str, List] = {}
        for node in self.dataset.nodes:
            node_type = node.type
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(node)

        lines = [
            "// Script de chargement Memgraph (sans APOC)",
            "// Benchmark BaseType V3",
            f"// CSV depuis: {csv_path}",
            "",
        ]

        # Créer les nœuds par type avec UNWIND
        for node_type, nodes in nodes_by_type.items():
            lines.append(f"// === {node_type} ({len(nodes)} nodes) ===")

            # Collecter les propriétés pour ce type
            sample = flatten_jsonb(nodes[0])
            props = [k for k in sample.keys() if k not in ['node_type']]

            # Générer les données en batch
            lines.append(f"UNWIND [")
            for i, node in enumerate(nodes):
                flat = flatten_jsonb(node)
                # Formater les valeurs
                props_str = []
                for k, v in flat.items():
                    if k == 'node_type':
                        continue
                    if v is None or v == "":
                        continue
                    if isinstance(v, str):
                        # Escape quotes
                        v_escaped = v.replace('\\', '\\\\').replace('"', '\\"')
                        props_str.append(f'{k}: "{v_escaped}"')
                    elif isinstance(v, list):
                        props_str.append(f'{k}: {json.dumps(v)}')
                    elif isinstance(v, bool):
                        props_str.append(f'{k}: {str(v).lower()}')
                    else:
                        props_str.append(f'{k}: {v}')

                comma = "," if i < len(nodes) - 1 else ""
                lines.append(f"  {{{', '.join(props_str)}}}{comma}")

            lines.append(f"] AS props")
            lines.append(f"CREATE (n:{node_type})")
            lines.append(f"SET n = props;")
            lines.append("")

        # Créer les relations
        lines.append("// === Relations ===")
        for edge in self.dataset.edges:
            lines.append(
                f'MATCH (a {{id: "{edge.source_id}"}}), (b {{id: "{edge.target_id}"}}) '
                f'CREATE (a)-[:{edge.rel_type}]->(b);'
            )

        filepath = self.output_dir / "load_memgraph_simple.cql"
        with open(filepath, 'w') as f:
            f.write("\n".join(lines))
        return filepath

    def export_load_script_csv(self) -> Path:
        """
        Exporte un script de chargement via LOAD CSV.
        Nécessite que les CSV soient accessibles par Memgraph.
        """
        csv_path = str(self.output_dir.absolute()).replace('\\', '/')

        lines = [
            "// Script de chargement Memgraph via LOAD CSV",
            "// Benchmark BaseType V3",
            f"// CSV path: {csv_path}",
            "",
            "// Note: Les fichiers CSV doivent être dans un répertoire",
            "// accessible par Memgraph (--data-directory ou volume Docker)",
            "",
        ]

        # Charger les nœuds par type
        node_types = set(n.type for n in self.dataset.nodes)

        for node_type in sorted(node_types):
            lines.append(f"// Charger {node_type}")
            lines.append(f'LOAD CSV WITH HEADERS FROM "file:///{csv_path}/nodes.csv" AS row')
            lines.append(f'WITH row WHERE row.node_type = "{node_type}"')
            lines.append(f"CREATE (n:{node_type} {{")
            lines.append(f"  id: row.id,")
            lines.append(f"  name: row.name,")
            lines.append(f"  equipment_type: row.equipment_type,")
            lines.append(f"  domain: row.domain,")
            lines.append(f"  building_id: row.building_id,")
            lines.append(f"  protocol_device_id: CASE WHEN row.protocol_device_id <> '' THEN toInteger(row.protocol_device_id) ELSE null END,")
            lines.append(f"  metadata_warranty_end: row.metadata_warranty_end,")
            lines.append(f"  calibration_next_date: row.calibration_next_date")
            lines.append(f"}});")
            lines.append("")

        # Charger les relations
        lines.append("// Charger les relations")
        lines.append(f'LOAD CSV WITH HEADERS FROM "file:///{csv_path}/edges.csv" AS row')
        lines.append("MATCH (a {id: row.source_id})")
        lines.append("MATCH (b {id: row.target_id})")
        lines.append("CALL {")
        lines.append("  WITH a, b, row")
        lines.append("  WITH a, b, row")
        lines.append("  WHERE row.rel_type = 'FEEDS' CREATE (a)-[:FEEDS]->(b)")
        lines.append("  UNION")
        lines.append("  WITH a, b, row")
        lines.append("  WHERE row.rel_type = 'SERVES' CREATE (a)-[:SERVES]->(b)")
        lines.append("  // ... autres types de relations")
        lines.append("};")

        filepath = self.output_dir / "load_memgraph_csv.cql"
        with open(filepath, 'w') as f:
            f.write("\n".join(lines))
        return filepath

    def export_timeseries_sql(self) -> Path:
        """Exporte le script SQL pour charger les timeseries dans TimescaleDB (M2)"""
        sql = f'''-- Chargement timeseries pour M2 (TimescaleDB)
-- Benchmark BaseType V3

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS timeseries (
    time TIMESTAMPTZ NOT NULL,
    point_id VARCHAR(64) NOT NULL,
    value DOUBLE PRECISION NOT NULL
);
SELECT create_hypertable('timeseries', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_timeseries_point ON timeseries(point_id, time DESC);

\\COPY timeseries FROM '{self.output_dir.absolute()}/timeseries.csv' WITH (FORMAT csv, HEADER true);
'''
        filepath = self.output_dir / "load_timeseries_m2.sql"
        with open(filepath, 'w') as f:
            f.write(sql)
        return filepath


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    from pathlib import Path

    output_dir = Path("data/export/m1m2")
    print(f"M1/M2 Extractor - Export vers {output_dir}")

    extractor = M1M2Extractor(output_dir)
    extractor.load_dataset()

    # Export données
    result = extractor.export_all()

    print(f"\n=== RÉSULTAT M1/M2 ===")
    print(f"Nodes: {result.total_nodes}")
    print(f"Edges: {result.total_edges}")
    print(f"Timeseries: {result.total_timeseries} (M2 only)")
    print(f"Files: {len(result.files_created)}")

    # Export scripts
    schema_file = extractor.export_schema_file()
    print(f"Schema: {schema_file}")

    simple_file = extractor.export_load_script_simple()
    print(f"Load script (simple): {simple_file}")

    csv_file = extractor.export_load_script_csv()
    print(f"Load script (CSV): {csv_file}")

    ts_file = extractor.export_timeseries_sql()
    print(f"Timeseries SQL (M2): {ts_file}")

    # Afficher un sample
    print("\n=== SAMPLE NODE APLATI ===")
    import json
    with open(output_dir / "nodes.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['id'] == 'ahu_1':
                print(f"AHU_1 (colonnes avec valeurs):")
                for k, v in row.items():
                    if v:
                        print(f"  {k}: {v}")
                break

    print("\nM1/M2 extraction complete.")
