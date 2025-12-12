// Création des contraintes et index de base
CREATE CONSTRAINT ON (n:Node) ASSERT n.id IS UNIQUE;
CREATE INDEX ON :Node(type);

// Chargement depuis des CSV placés dans /import (monter dataset_gen/out dans le container)
LOAD CSV FROM "/import/nodes.csv" WITH HEADER AS row
MERGE (n:Node {id: row.id})
SET n.type = row.type, n.name = row.name;

// Les quantités sont appliquées comme propriété sur les points pour rester comparables aux autres moteurs
LOAD CSV FROM "/import/edges.csv" WITH HEADER AS row
WITH row WHERE row.rel_type = "MEASURES"
MATCH (p:Node {id: row.src_id})
SET p.quantity = row.dst_id;

LOAD CSV FROM "/import/edges.csv" WITH HEADER AS row
WITH row WHERE row.rel_type <> "MEASURES"
MATCH (s:Node {id: row.src_id})
MATCH (d:Node {id: row.dst_id})
CALL {
  WITH row, s, d
  FOREACH (_ IN CASE WHEN row.rel_type = "CONTAINS" THEN [1] ELSE [] END |
    CREATE (s)-[:CONTAINS {source: "synthetic"}]->(d))
  FOREACH (_ IN CASE WHEN row.rel_type = "LOCATED_IN" THEN [1] ELSE [] END |
    CREATE (s)-[:LOCATED_IN {source: "synthetic"}]->(d))
  FOREACH (_ IN CASE WHEN row.rel_type = "HAS_PART" THEN [1] ELSE [] END |
    CREATE (s)-[:HAS_PART {source: "synthetic"}]->(d))
  FOREACH (_ IN CASE WHEN row.rel_type = "HAS_POINT" THEN [1] ELSE [] END |
    CREATE (s)-[:HAS_POINT {source: "synthetic"}]->(d))
  FOREACH (_ IN CASE WHEN row.rel_type = "CONTROLS" THEN [1] ELSE [] END |
    CREATE (s)-[:CONTROLS {source: "synthetic"}]->(d))
  FOREACH (_ IN CASE WHEN row.rel_type = "FEEDS" THEN [1] ELSE [] END |
    CREATE (s)-[:FEEDS {source: "synthetic"}]->(d))
  FOREACH (_ IN CASE WHEN row.rel_type = "SERVES" THEN [1] ELSE [] END |
    CREATE (s)-[:SERVES {source: "synthetic"}]->(d))
  FOREACH (_ IN CASE WHEN row.rel_type = "OCCUPIES" THEN [1] ELSE [] END |
    CREATE (s)-[:OCCUPIES {source: "synthetic"}]->(d))
}
