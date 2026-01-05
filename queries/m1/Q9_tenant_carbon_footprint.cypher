// Q9: Tenant Carbon Footprint (via METERS_TENANT)
// For M1: Graph traversal for structure
// Parameters: $TENANT_ID - tenant to analyze, $DATE_START/$DATE_END (for TS query)
// Pattern: Tenant <- METERS_TENANT <- SubMeter -> HAS_POINT -> Point(energy)
// Complexity: 2 hops + carbon calculation

MATCH (t:Node {id: '$TENANT_ID', type: 'Tenant'})
      <-[:METERS_TENANT]-(m:Node {type: 'Equipment'})
      -[:HAS_POINT]->(p:Node {type: 'Point'})
WHERE p.quantity = 'energy'
RETURN t.id AS tenant_id,
       t.name AS tenant_name,
       t.building_id AS building_id,
       count(DISTINCT m) AS meter_count,
       collect(DISTINCT p.id) AS energy_point_ids;
