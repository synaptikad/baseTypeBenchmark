// Q4: Inventory - Temperature points per floor
// Benchmark: Multi-hop pattern matching with filter

MATCH (f:Node {type: 'Floor'})-[:CONTAINS]->(sp:Node {type: 'Space'})
      -[:CONTAINS|SERVES]->(eq:Node {type: 'Equipment'})
      -[:HAS_POINT]->(p:Node {type: 'Point'})
WHERE p.quantity = 'Temperature'
RETURN f.id AS floor_id,
       f.name AS floor_name,
       f.building_id AS building_id,
       count(DISTINCT p) AS temp_point_count
ORDER BY temp_point_count DESC;
