// M2: Memgraph + TimescaleDB
// Query graph-only - identique a M1
// Pour Q6+, voir aussi ts/Q0X.sql

// Q3: Space Services
// Parametre: $space_id
// Intention: Pour un espace, lister les equipements connectes.

MATCH (eq:Equipment)-[r:SERVES|LOCATED_IN|MONITORS|SECURES|GRANTS_ACCESS]->(sp:Space {id: $space_id})
RETURN
    eq.id AS equipment_id,
    eq.name AS equipment_name,
    eq.equipment_type AS equipment_type,
    type(r) AS relation_type
ORDER BY relation_type, equipment_id;
