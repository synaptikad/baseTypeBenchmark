// Q8: Tenant Energy - Structure query (points identification)
// For M2 hybrid: This returns point IDs, aggregation done in TimescaleDB
// Parameters: $TENANT_ID - tenant to analyze, $DATE_START/$DATE_END (for TS query)

MATCH (t:Node {id: '$TENANT_ID'})-[:OCCUPIES]->(sp:Node {type: 'Space'})
      -[:SERVES|CONTAINS]-(eq:Node {type: 'Equipment'})
      -[:HAS_POINT]->(p:Node {type: 'Point'})
WHERE p.quantity = 'power'
RETURN t.id AS tenant_id,
       t.name AS tenant_name,
       collect(DISTINCT p.id) AS point_ids;
