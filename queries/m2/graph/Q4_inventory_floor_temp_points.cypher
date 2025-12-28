// Q4: Inventory - Temperature points for a specific floor
// Benchmark: Multi-hop pattern matching with filter
// Parameter: $FLOOR_ID - floor to inventory temperature points
// Note: Equipment can be CONTAINED by Space OR SERVES the Space (reverse direction)

MATCH (f:Node {id: '$FLOOR_ID'})-[:CONTAINS]->(sp:Node {type: 'Space'})
MATCH (eq:Node {type: 'Equipment'})-[:HAS_POINT]->(p:Node {type: 'Point'})
WHERE ((sp)-[:CONTAINS]->(eq) OR (eq)-[:SERVES]->(sp))
  AND p.quantity = 'Temperature'
RETURN f.id AS floor_id,
       f.name AS floor_name,
       f.building_id AS building_id,
       p.id AS point_id,
       p.name AS point_name,
       eq.id AS equipment_id,
       eq.name AS equipment_name
ORDER BY p.name;
