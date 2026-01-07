// M2: Memgraph + TimescaleDB
// Query graph-only - identique a M1
// Pour Q6+, voir aussi ts/Q0X.sql

// Q1: Energy Chain
// Parametre: $meter_id
// Intention: Depuis un compteur (meter_id), suivre FEEDS jusqu'a profondeur 10.

MATCH path = (source:Equipment {id: $meter_id})-[:FEEDS*1..10]->(target:Equipment)
WITH target, length(path) AS depth
RETURN
    target.id AS id,
    target.equipment_type AS type,
    target.name AS name,
    depth
ORDER BY depth, id;
