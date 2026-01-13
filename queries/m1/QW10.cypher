// QW10 - Tenant Move-Out
// Supprimer relation OCCUPIES (METERS_TENANT reste pour historique)
MATCH (t:Tenant {id: $tenant_id})-[r:OCCUPIES]->(s:Space {id: $space_id})
DELETE r
RETURN t.id AS tenant_id, s.id AS space_id, 1 AS relations_deleted
