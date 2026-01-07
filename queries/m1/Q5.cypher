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
