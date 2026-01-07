// Q9: Tenant Carbon - Reutilise Q08
// Parametre: $tenant_id

MATCH (t:Tenant {id: $tenant_id})<-[:METERS_TENANT]-(eq:Equipment)-[:HAS_POINT]->(p:Point {quantity: 'energy'})
RETURN collect(DISTINCT p.id) AS point_ids;
