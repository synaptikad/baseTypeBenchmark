"""
O2 Extractor - Oxigraph (RDF/SPARQL) + TimescaleDB
Benchmark BaseType V3
"""

from pathlib import Path
from typing import List, Dict, Any
import csv
from datetime import datetime

from .base import (
    BaseExtractor, ExportResult,
    write_csv
)


# Préfixes RDF
BTB = "http://basetype.benchmark/ontology#"
BTB_DATA = "http://basetype.benchmark/data#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
XSD = "http://www.w3.org/2001/XMLSchema#"


def escape_ntriples(value: str) -> str:
    """Escape une valeur pour N-Triples"""
    if value is None:
        return ""
    return (str(value)
            .replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '\\r')
            .replace('\t', '\\t'))


def make_uri(local_id: str) -> str:
    """Crée une URI à partir d'un ID local"""
    return f"<{BTB_DATA}{local_id}>"


def make_literal(value: Any, datatype: str = None) -> str:
    """Crée un literal RDF"""
    if value is None:
        return None

    escaped = escape_ntriples(str(value))

    if datatype:
        return f'"{escaped}"^^<{datatype}>'
    elif isinstance(value, bool):
        return f'"{str(value).lower()}"^^<{XSD}boolean>'
    elif isinstance(value, int):
        return f'"{value}"^^<{XSD}integer>'
    elif isinstance(value, float):
        return f'"{value}"^^<{XSD}double>'
    else:
        return f'"{escaped}"'


class O2Extractor(BaseExtractor):
    """
    Extracteur pour O2 (Oxigraph RDF).

    Produit:
    - data.nt : N-Triples pour bulk loading
    - ontology.ttl : Ontologie en Turtle
    - timeseries.csv : Pour TimescaleDB
    - load_oxigraph.sh : Script de chargement
    """

    @property
    def paradigm_name(self) -> str:
        return "o2"

    def _node_to_triples(self, node) -> List[str]:
        """Convertit un nœud en triples N-Triples"""
        triples = []
        subject = make_uri(node.id)

        # Type RDF
        triples.append(f'{subject} <{RDF}type> <{BTB}{node.type}> .')

        # Propriétés de base
        triples.append(f'{subject} <{BTB}id> {make_literal(node.id)} .')
        triples.append(f'{subject} <{BTB}name> {make_literal(node.name)} .')

        # Propriétés du dict properties
        property_mapping = {
            'equipment_type': 'equipmentType',
            'domain': 'domain',
            'building_id': 'buildingId',
            'floor_id': 'floorId',
            'space_id': 'spaceId',
            'site_id': 'siteId',
            'quantity': 'quantity',
            'unit': 'unit',
            'equipment_id': 'equipmentId',
            'space_type': 'spaceType',
            'floor_type': 'floorType',
            'level_index': 'levelIndex',
            'area_m2': 'areaM2',
            'capacity': 'capacity',
            'zone_type': 'zoneType',
            'contract_type': 'contractType',
            'contract_start': 'contractStart',
            'contract_end': 'contractEnd',
            'start_date': 'startDate',
            'end_date': 'endDate',
            'provider': 'provider',
            'frequency': 'frequency',
            'address': 'address',
            'gross_area_m2': 'grossAreaM2',
        }

        for py_key, rdf_key in property_mapping.items():
            value = node.properties.get(py_key)
            if value is not None and not isinstance(value, dict):
                literal = make_literal(value)
                if literal:
                    triples.append(f'{subject} <{BTB}{rdf_key}> {literal} .')

        # Capabilities (multi-valued)
        for cap in node.capabilities:
            triples.append(f'{subject} <{BTB}capability> {make_literal(cap)} .')

        # Tags (multi-valued)
        for tag in node.tags:
            triples.append(f'{subject} <{BTB}tag> {make_literal(tag)} .')

        # Metadata (aplati)
        for key, value in node.metadata.items():
            rdf_key = 'metadata' + key.replace('_', ' ').title().replace(' ', '')
            if value is not None:
                # Dates: check for 'date' or date-like patterns (warranty_end, _start, _end)
                if 'date' in key.lower() or key.endswith('_end') or key.endswith('_start'):
                    literal = make_literal(value, f"{XSD}date")
                else:
                    literal = make_literal(value)
                triples.append(f'{subject} <{BTB}{rdf_key}> {literal} .')

        # Protocol (aplati)
        for key, value in node.protocol.items():
            rdf_key = 'protocol' + key.replace('_', ' ').title().replace(' ', '')
            if value is not None:
                if isinstance(value, int):
                    literal = make_literal(value)
                else:
                    literal = make_literal(value)
                triples.append(f'{subject} <{BTB}{rdf_key}> {literal} .')

        # Calibration (aplati)
        for key, value in node.calibration.items():
            rdf_key = 'calibration' + key.replace('_', ' ').title().replace(' ', '')
            if value is not None:
                if 'date' in key.lower():
                    literal = make_literal(value, f"{XSD}date")
                else:
                    literal = make_literal(value)
                triples.append(f'{subject} <{BTB}{rdf_key}> {literal} .')

        # Range (aplati)
        for key, value in node.range_info.items():
            rdf_key = 'range' + key.replace('_', ' ').title().replace(' ', '')
            if value is not None:
                triples.append(f'{subject} <{BTB}{rdf_key}> {make_literal(value)} .')

        return triples

    def _edge_to_triple(self, edge) -> str:
        """Convertit une relation en triple"""
        subject = make_uri(edge.source_id)
        obj = make_uri(edge.target_id)

        # Mapping des types de relation vers predicats RDF
        rel_mapping = {
            'CONTAINS': 'contains',
            'FEEDS': 'feeds',
            'SERVES': 'serves',
            'HAS_POINT': 'hasPoint',
            'LOCATED_IN': 'locatedIn',
            'MONITORS': 'monitors',
            'ADJACENT_TO': 'adjacentTo',
            'METERS_TENANT': 'metersTenant',
            'METERS_ZONE': 'metersZone',
            'OCCUPIES': 'occupies',
            'MEMBER_OF': 'memberOf',
            'COVERED_BY': 'coveredBy',
            'SECURES': 'secures',
            'GRANTS_ACCESS': 'grantsAccess',
            'NETWORK_LINK': 'networkLink',
            'CONTROLS': 'controls',
            'HAS_PART': 'hasPart',
            'HOSTS': 'hosts',
            'HAS_TICKET': 'hasTicket',
            'LEASED_TO': 'leasedTo',
            'MANAGES': 'manages',
        }

        predicate = rel_mapping.get(edge.rel_type, edge.rel_type.lower().replace('_', ''))
        return f'{subject} <{BTB}{predicate}> {obj} .'

    def extract_nodes(self) -> List[Path]:
        """Extrait les nœuds vers N-Triples"""
        all_triples = []

        for node in self.dataset.nodes:
            triples = self._node_to_triples(node)
            all_triples.extend(triples)

        filepath = self.output_dir / "nodes.nt"
        with open(filepath, 'w', encoding='utf-8') as f:
            for triple in all_triples:
                f.write(triple + '\n')

        print(f"  Created {filepath} ({len(all_triples)} triples)")
        return [filepath]

    def extract_edges(self) -> List[Path]:
        """Extrait les relations vers N-Triples"""
        triples = []

        for edge in self.dataset.edges:
            triple = self._edge_to_triple(edge)
            triples.append(triple)

        filepath = self.output_dir / "edges.nt"
        with open(filepath, 'w', encoding='utf-8') as f:
            for triple in triples:
                f.write(triple + '\n')

        print(f"  Created {filepath} ({len(triples)} triples)")
        return [filepath]

    def extract_timeseries(self) -> List[Path]:
        """Extrait les timeseries vers CSV (pour TimescaleDB)"""
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
        """Retourne les commandes de création du schema (ontologie)"""
        return [
            "# L'ontologie est définie dans ontology.ttl",
            "# Charger avec: oxigraph load --file ontology.ttl"
        ]

    def get_load_commands(self) -> List[str]:
        """Retourne les commandes de chargement bulk"""
        return [
            f"# Charger les données RDF dans Oxigraph",
            f"oxigraph load --location ./oxigraph_data --file {self.output_dir}/data.nt",
            f"",
            f"# Ou via HTTP API",
            f"curl -X POST -H 'Content-Type: application/n-triples' \\",
            f"     --data-binary @{self.output_dir}/data.nt \\",
            f"     http://localhost:7878/store",
        ]

    def export_combined_ntriples(self) -> Path:
        """Combine tous les triples en un seul fichier"""
        filepath = self.output_dir / "data.nt"

        with open(filepath, 'w', encoding='utf-8') as out:
            # Nodes
            for node in self.dataset.nodes:
                for triple in self._node_to_triples(node):
                    out.write(triple + '\n')

            # Edges
            for edge in self.dataset.edges:
                out.write(self._edge_to_triple(edge) + '\n')

        print(f"  Created {filepath} (combined)")
        return filepath

    def export_ontology(self) -> Path:
        """Exporte l'ontologie en Turtle"""
        ontology = '''@prefix btb: <http://basetype.benchmark/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# ============================================================
# Ontologie BaseType Benchmark V3
# ============================================================

<http://basetype.benchmark/ontology#> a owl:Ontology ;
    rdfs:label "BaseType Benchmark Ontology" ;
    rdfs:comment "Ontologie pour le benchmark de systèmes d'information bâtimentaires" .

# ------------------------------------------------------------
# Classes
# ------------------------------------------------------------

btb:Site a rdfs:Class ;
    rdfs:label "Site" ;
    rdfs:comment "Campus ou site géographique" .

btb:Building a rdfs:Class ;
    rdfs:label "Building" ;
    rdfs:comment "Bâtiment physique" .

btb:Floor a rdfs:Class ;
    rdfs:label "Floor" ;
    rdfs:comment "Étage d'un bâtiment" .

btb:Space a rdfs:Class ;
    rdfs:label "Space" ;
    rdfs:comment "Espace ou pièce" .

btb:Equipment a rdfs:Class ;
    rdfs:label "Equipment" ;
    rdfs:comment "Équipement technique" .

btb:Point a rdfs:Class ;
    rdfs:label "Point" ;
    rdfs:comment "Point de mesure ou commande" .

btb:Tenant a rdfs:Class ;
    rdfs:label "Tenant" ;
    rdfs:comment "Locataire ou occupant" .

btb:Zone a rdfs:Class ;
    rdfs:label "Zone" ;
    rdfs:comment "Zone logique" .

btb:Contract a rdfs:Class ;
    rdfs:label "Contract" ;
    rdfs:comment "Contrat de maintenance" .

# ------------------------------------------------------------
# Object Properties (Relations)
# ------------------------------------------------------------

btb:contains a rdf:Property ;
    rdfs:label "contains" ;
    rdfs:domain btb:Site, btb:Building, btb:Floor ;
    rdfs:range btb:Building, btb:Floor, btb:Space .

btb:feeds a rdf:Property ;
    rdfs:label "feeds" ;
    rdfs:domain btb:Equipment ;
    rdfs:range btb:Equipment .

btb:serves a rdf:Property ;
    rdfs:label "serves" ;
    rdfs:domain btb:Equipment ;
    rdfs:range btb:Space, btb:Building .

btb:hasPoint a rdf:Property ;
    rdfs:label "hasPoint" ;
    rdfs:domain btb:Equipment ;
    rdfs:range btb:Point .

btb:locatedIn a rdf:Property ;
    rdfs:label "locatedIn" ;
    rdfs:domain btb:Equipment ;
    rdfs:range btb:Space .

btb:monitors a rdf:Property ;
    rdfs:label "monitors" ;
    rdfs:domain btb:Equipment ;
    rdfs:range btb:Space, btb:Equipment .

btb:adjacentTo a rdf:Property ;
    rdfs:label "adjacentTo" ;
    rdfs:domain btb:Space ;
    rdfs:range btb:Space ;
    a owl:SymmetricProperty .

btb:metersTenant a rdf:Property ;
    rdfs:label "metersTenant" ;
    rdfs:domain btb:Equipment ;
    rdfs:range btb:Tenant .

# ------------------------------------------------------------
# Datatype Properties
# ------------------------------------------------------------

btb:id a rdf:Property ;
    rdfs:label "id" ;
    rdfs:range xsd:string .

btb:name a rdf:Property ;
    rdfs:label "name" ;
    rdfs:range xsd:string .

btb:equipmentType a rdf:Property ;
    rdfs:label "equipmentType" ;
    rdfs:domain btb:Equipment ;
    rdfs:range xsd:string .

btb:domain a rdf:Property ;
    rdfs:label "domain" ;
    rdfs:range xsd:string .

btb:quantity a rdf:Property ;
    rdfs:label "quantity" ;
    rdfs:domain btb:Point ;
    rdfs:range xsd:string .

# JSONB properties
btb:capability a rdf:Property ;
    rdfs:label "capability" ;
    rdfs:domain btb:Equipment ;
    rdfs:range xsd:string .

btb:tag a rdf:Property ;
    rdfs:label "tag" ;
    rdfs:domain btb:Equipment, btb:Point ;
    rdfs:range xsd:string .

btb:protocolType a rdf:Property ;
    rdfs:label "protocolType" ;
    rdfs:range xsd:string .

btb:protocolDeviceId a rdf:Property ;
    rdfs:label "protocolDeviceId" ;
    rdfs:range xsd:integer .

btb:metadataWarrantyEnd a rdf:Property ;
    rdfs:label "metadataWarrantyEnd" ;
    rdfs:range xsd:date .

btb:calibrationNextDate a rdf:Property ;
    rdfs:label "calibrationNextDate" ;
    rdfs:range xsd:date .
'''
        filepath = self.output_dir / "ontology.ttl"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(ontology)
        return filepath

    def export_load_script(self) -> Path:
        """Exporte le script de chargement"""
        script = f'''#!/bin/bash
# Script de chargement O2 (Oxigraph)
# Benchmark BaseType V3

DATA_DIR="{self.output_dir.absolute()}"
OXIGRAPH_DATA="./oxigraph_data"

echo "=== Chargement O2 ==="

# Créer le répertoire de données Oxigraph
mkdir -p $OXIGRAPH_DATA

# Charger l'ontologie
echo "Chargement ontologie..."
oxigraph load --location $OXIGRAPH_DATA --file $DATA_DIR/ontology.ttl

# Charger les données (N-Triples = plus rapide)
echo "Chargement données..."
oxigraph load --location $OXIGRAPH_DATA --file $DATA_DIR/data.nt

# Démarrer le serveur (optionnel)
echo "Pour démarrer le serveur:"
echo "  oxigraph serve --location $OXIGRAPH_DATA"

# Charger timeseries dans TimescaleDB
echo ""
echo "=== Chargement TimescaleDB ==="
echo "psql -d benchmark -f $DATA_DIR/load_timeseries_o2.sql"
'''
        filepath = self.output_dir / "load_oxigraph.sh"
        with open(filepath, 'w') as f:
            f.write(script)
        return filepath

    def export_timeseries_sql(self) -> Path:
        """Exporte le script SQL pour TimescaleDB"""
        sql = f'''-- Chargement timeseries pour O2 (TimescaleDB)
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
        filepath = self.output_dir / "load_timeseries_o2.sql"
        with open(filepath, 'w') as f:
            f.write(sql)
        return filepath

    def export_sample_queries(self) -> Path:
        """Exporte des exemples de queries SPARQL"""
        queries = '''# Exemples de queries SPARQL O2
# Benchmark BaseType V3

PREFIX btb: <http://basetype.benchmark/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# Q14: Protocol Query (BACnet device_id = 1234)
SELECT ?point_id ?point_name ?equipment_id ?object_type ?object_instance
WHERE {
    ?point a btb:Point ;
           btb:id ?point_id ;
           btb:name ?point_name ;
           btb:equipmentId ?equipment_id ;
           btb:protocolType "BACnet" ;
           btb:protocolDeviceId 1234 .
    OPTIONAL { ?point btb:protocolObjectType ?object_type }
    OPTIONAL { ?point btb:protocolObjectInstance ?object_instance }
}
ORDER BY ?equipment_id ?point_id

# Q16: Semantic Tag Search (brick:*)
SELECT ?equipment_id ?name (GROUP_CONCAT(?tag; separator=",") AS ?matching_tags)
WHERE {
    ?eq a btb:Equipment ;
        btb:id ?equipment_id ;
        btb:name ?name ;
        btb:tag ?tag .
    FILTER(STRSTARTS(?tag, "brick:"))
}
GROUP BY ?equipment_id ?name
ORDER BY ?equipment_id

# Q17: Capability Filter (humidity_control)
SELECT ?equipment_id ?name ?equipment_type
WHERE {
    ?eq a btb:Equipment ;
        btb:id ?equipment_id ;
        btb:name ?name ;
        btb:equipmentType ?equipment_type ;
        btb:domain "HVAC" ;
        btb:capability "humidity_control" .
}
ORDER BY ?equipment_type ?equipment_id
'''
        filepath = self.output_dir / "sample_queries_o2.sparql"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(queries)
        return filepath


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='O2 Extractor - Oxigraph/SPARQL')
    parser.add_argument('--input', type=str, required=True, help='Input directory with Parquet files')
    parser.add_argument('--output', type=str, required=True, help='Output directory for N-Triples files')
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    print(f"O2 Extractor - {input_dir} → {output_dir}")

    extractor = O2Extractor(output_dir, input_dir)
    extractor.load_dataset()

    # Export données
    result = extractor.export_all()

    print(f"\n=== RÉSULTAT O2 ===")
    print(f"Nodes: {result.total_nodes}")
    print(f"Edges: {result.total_edges}")
    print(f"Timeseries: {result.total_timeseries}")
    print(f"Files: {len(result.files_created)}")

    # Export fichiers additionnels
    combined = extractor.export_combined_ntriples()
    print(f"Combined N-Triples: {combined}")

    ontology = extractor.export_ontology()
    print(f"Ontology: {ontology}")

    load_script = extractor.export_load_script()
    print(f"Load script: {load_script}")

    ts_sql = extractor.export_timeseries_sql()
    print(f"Timeseries SQL: {ts_sql}")

    samples = extractor.export_sample_queries()
    print(f"Sample queries: {samples}")

    # Afficher un sample
    print("\n=== SAMPLE TRIPLES (AHU_1) ===")
    with open(output_dir / "nodes.nt") as f:
        for line in f:
            if 'ahu_1>' in line:
                print(line.strip())

    print("\nO2 extraction complete.")
