// Q41: Verify Tenant Consolidation
// Après un merge, vérifier le nombre total de relations du tenant target
// Paramètres: $tenant_id
// Validates: QW12 (Tenant Merge)

MATCH (t:Tenant {id: $tenant_id})
OPTIONAL MATCH (t)-[o:OCCUPIES]->(:Space)
OPTIONAL MATCH (:Equipment)-[m:METERS_TENANT]->(t)
RETURN t.id AS tenant_id,
       count(DISTINCT o) AS occupied_spaces,
       count(DISTINCT m) AS associated_meters
