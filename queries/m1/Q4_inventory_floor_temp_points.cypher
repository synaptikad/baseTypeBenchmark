// Q4: Inventory - Temperature points for a specific floor
// Benchmark: Multi-hop pattern matching with filter
// Parameter: $FLOOR_ID - floor to inventory temperature points

MATCH (f:Node {id: '$FLOOR_ID'})-[:CONTAINS]->(sp:Node {type: 'Space'})
      -[:CONTAINS|SERVES]->(eq:Node {type: 'Equipment'})
      -[:HAS_POINT]->(p:Node {type: 'Point'})
WHERE p.quantity = 'Temperature'
RETURN f.id AS floor_id,
       f.name AS floor_name,
       f.building_id AS building_id,
       p.id AS point_id,
       p.name AS point_name,
       eq.id AS equipment_id,
       eq.name AS equipment_name
ORDER BY p.name;
