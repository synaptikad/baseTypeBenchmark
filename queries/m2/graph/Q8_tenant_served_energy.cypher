// Q8: Tenant Energy Consumption (via METERS_TENANT)
// For M2 hybrid: This returns point IDs, aggregation done in TimescaleDB
// Parameters: $TENANT_ID - tenant to analyze, $DATE_START/$DATE_END (for TS query)
// Pattern: Tenant <- METERS_TENANT <- SubMeter -> HAS_POINT -> Point(energy)
// Complexity: 2 hops (vs 5 hops in previous version)

MATCH (t:Node {id: '$TENANT_ID', type: 'Tenant'})
      <-[:METERS_TENANT]-(m:Node {type: 'Equipment'})
      -[:HAS_POINT]->(p:Node {type: 'Point'})
WHERE p.quantity = 'energy'
RETURN t.id AS tenant_id,
       t.name AS tenant_name,
       collect(DISTINCT p.id) AS point_ids;
