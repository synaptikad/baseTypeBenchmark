// M2: Memgraph + TimescaleDB
// Query graph-only - identique a M1
// Pour Q6+, voir aussi ts/Q0X.sql

// Q2: Functional Impact
// Parametre: $equipment_id
// Intention: Depuis un equipement, remonter via FEEDS|SERVES|CONTAINS.

MATCH path = (source {id: $equipment_id})<-[r:FEEDS|SERVES|CONTAINS*1..10]-(parent)
WITH parent, r, length(path) AS depth
UNWIND r AS rel
WITH parent, type(rel) AS relation_type, depth
RETURN DISTINCT
    parent.id AS id,
    labels(parent)[0] AS type,
    parent.name AS name,
    relation_type,
    depth
ORDER BY depth, id;
