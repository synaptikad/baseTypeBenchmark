// Q5: Orphans
// Pas de parametre
// Intention: Equipements sans aucune relation.
// Memgraph: utilise OPTIONAL MATCH + IS NULL pour éviter pattern NOT

MATCH (eq:Equipment)
OPTIONAL MATCH (eq)-[r]-()
WITH eq, r
WHERE r IS NULL
RETURN
    eq.id AS id,
    eq.equipment_type AS type,
    eq.name AS name
ORDER BY type, id;
