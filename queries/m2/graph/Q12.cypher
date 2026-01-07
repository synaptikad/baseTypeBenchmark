// Q12: Full Building Analytics - Extraction points par quantity
// Parametre: $building_id

MATCH (p:Point {building_id: $building_id})
WHERE p.quantity IN ['energy', 'temperature', 'occupancy']
RETURN p.quantity AS quantity, collect(p.id) AS point_ids;
