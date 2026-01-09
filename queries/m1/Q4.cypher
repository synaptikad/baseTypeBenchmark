// Q4: Floor Temperature Inventory
// Parametre: $floor_id
// Intention: Pour un etage, lister les points temperature.
// Memgraph: EXISTS { MATCH } non supporté, utilise OPTIONAL MATCH + filtrage

MATCH (eq:Equipment)-[:HAS_POINT]->(p:Point)
WHERE p.quantity = 'temperature'
OPTIONAL MATCH (eq)-[:LOCATED_IN|SERVES]->(sp:Space)
WHERE sp.floor_id = $floor_id
WITH eq, p, sp
WHERE eq.floor_id = $floor_id OR sp IS NOT NULL
RETURN
    $floor_id AS floor_id,
    p.id AS point_id,
    p.name AS point_name,
    eq.id AS equipment_id,
    eq.name AS equipment_name
ORDER BY equipment_id, point_id;
