// Q8: Tenant Energy - Extraction point_ids energie du tenant
// Parametre: $tenant_id

MATCH (t:Tenant {id: $tenant_id})<-[:METERS_TENANT]-(eq:Equipment)-[:HAS_POINT]->(p:Point {quantity: 'energy'})
RETURN collect(DISTINCT p.id) AS point_ids, count(DISTINCT eq.id) AS meter_count;
