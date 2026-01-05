// Q8: Tenant Energy Consumption (via METERS_TENANT)
// For M1: Graph traversal + embedded timeseries
// Parameters: $TENANT_ID - tenant to analyze, $DATE_START/$DATE_END - time range
// Pattern: Tenant <- METERS_TENANT <- SubMeter -> HAS_POINT -> Point(energy)
// Complexity: 2 hops (vs 5 hops in previous version)

MATCH (t:Node {id: '$TENANT_ID', type: 'Tenant'})
      <-[:METERS_TENANT]-(m:Node {type: 'Equipment'})
      -[:HAS_POINT]->(p:Node {type: 'Point'})
WHERE p.quantity = 'energy'
RETURN t.id AS tenant_id,
       t.name AS tenant_name,
       m.id AS meter_id,
       m.name AS meter_name,
       collect(DISTINCT p.id) AS point_ids;
