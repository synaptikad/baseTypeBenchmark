// Q40: Verify Tenant Meters
// Lister tous les compteurs associés à un locataire (via METERS_TENANT)
// Paramètres: $tenant_id
// Validates: QW9 (Move-In with meter)

MATCH (m:Equipment)-[:METERS_TENANT]->(t:Tenant {id: $tenant_id})
RETURN m.id AS meter_id, m.name AS meter_name, labels(m)[0] AS meter_type
ORDER BY meter_id
