// QW9 - Tenant Move-In
// Créer relation OCCUPIES et optionnellement METERS_TENANT
MATCH (t:Tenant {id: $tenant_id})
MATCH (s:Space {id: $space_id})
MERGE (t)-[:OCCUPIES]->(s)
WITH t
OPTIONAL MATCH (m:Equipment {id: $meter_id})
WHERE $meter_id IS NOT NULL
FOREACH (_ IN CASE WHEN m IS NOT NULL THEN [1] ELSE [] END |
    MERGE (m)-[:METERS_TENANT]->(t)
)
RETURN t.id AS tenant_id, 1 AS relations_created
