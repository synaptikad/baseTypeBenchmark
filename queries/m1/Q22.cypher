// Q22: Equipment Siblings
// Status: NATIVE pour M1/M2 (pattern matching)
// Paramètre: $equipment_id

MATCH (target:Equipment {id: $equipment_id})<-[:FEEDS]-(parent:Equipment)-[:FEEDS]->(sibling:Equipment)
WHERE sibling.id <> $equipment_id
RETURN
    sibling.id AS sibling_id,
    sibling.name AS sibling_name,
    sibling.equipment_type AS sibling_type,
    parent.id AS parent_id,
    parent.name AS parent_name
ORDER BY parent_id, sibling_id;
