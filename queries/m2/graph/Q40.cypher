// Q40: Verify Tenant Meters
// Lister tous les compteurs associés à un locataire (via METERS_TENANT)
// Paramètres: $q40_tenant_id
// Note: Uses q40_tenant_id (different from QW10's tenant) to persist across runs

MATCH (m:Equipment)-[:METERS_TENANT]->(t:Tenant {id: $q40_tenant_id})
RETURN m.id AS meter_id, m.name AS meter_name, labels(m)[0] AS meter_type
ORDER BY meter_id
