// QW10 - Tenant Move-Out
// Supprimer TOUTES les relations OCCUPIES et METERS_TENANT pour un tenant
// Note: OCCUPIES = (tenant)-[:OCCUPIES]->(space), METERS_TENANT = (meter)-[:METERS_TENANT]->(tenant)
MATCH (t:Tenant {id: $tenant_id})
OPTIONAL MATCH (t)-[r1:OCCUPIES]->()
OPTIONAL MATCH ()-[r2:METERS_TENANT]->(t)
WITH t, collect(r1) AS occupies_rels, collect(r2) AS meter_rels
FOREACH (r IN occupies_rels | DELETE r)
FOREACH (r IN meter_rels | DELETE r)
RETURN t.id AS tenant_id, size(occupies_rels) AS occupies_deleted, size(meter_rels) AS meters_deleted
