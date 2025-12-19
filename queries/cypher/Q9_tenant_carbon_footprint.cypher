// Q9: Tenant Carbon Footprint - Structure traversal
// Parameters: $TENANT_ID - tenant to analyze, $DATE_START/$DATE_END (for TS query)
// Returns tenant → space → equipment → point relationships

MATCH (t:Node {id: '$TENANT_ID'})-[:OCCUPIES]->(sp:Node {type: 'Space'})
      -[:SERVES|CONTAINS]-(eq:Node {type: 'Equipment'})
      -[:HAS_POINT]->(p:Node {type: 'Point'})
WHERE p.quantity = 'Power'
RETURN t.id AS tenant_id,
       t.name AS tenant_name,
       t.building_id AS building_id,
       count(DISTINCT sp) AS space_count,
       count(DISTINCT eq) AS equipment_count,
       collect(DISTINCT p.id) AS power_point_ids;
