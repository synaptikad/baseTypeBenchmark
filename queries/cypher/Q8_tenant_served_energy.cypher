// Q8: Tenant Energy - Structure query (points identification)
// For M2 hybrid: This returns point IDs, aggregation done in TimescaleDB

MATCH (t:Node {type: 'Tenant'})-[:OCCUPIES]->(sp:Node {type: 'Space'})
      -[:SERVES|CONTAINS]-(eq:Node {type: 'Equipment'})
      -[:HAS_POINT]->(p:Node {type: 'Point'})
WHERE p.quantity = 'Power'
RETURN t.id AS tenant_id,
       t.name AS tenant_name,
       collect(DISTINCT p.id) AS point_ids
ORDER BY tenant_id;
