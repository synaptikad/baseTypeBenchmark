// M2: Memgraph + TimescaleDB
// Query graph-only - identique a M1
// Pour Q6+, voir aussi ts/Q0X.sql

// Q5: Orphans
// Pas de parametre
// Intention: Equipements sans aucune relation.

MATCH (eq:Equipment)
WHERE NOT (eq)--()
RETURN
    eq.id AS id,
    eq.equipment_type AS type,
    eq.name AS name
ORDER BY type, id;
