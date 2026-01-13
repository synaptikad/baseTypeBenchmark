// QW11 - Space Reassignment
// Réaffecter un espace d'un tenant à un autre (atomique)
MATCH (old:Tenant {id: $old_tenant_id})-[r:OCCUPIES]->(s:Space {id: $space_id})
DELETE r
WITH s
MATCH (new:Tenant {id: $new_tenant_id})
MERGE (new)-[:OCCUPIES]->(s)
RETURN s.id AS space_id, $old_tenant_id AS old_tenant_id, $new_tenant_id AS new_tenant_id, true AS reassigned
