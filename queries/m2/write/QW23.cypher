// QW23: Revert Space Reassignment (Cleanup for QW11)
// Annule une reaffectation d'espace: supprime nouveau + insere ancien
// Parametres: $space_id, $old_tenant_id, $new_tenant_id
//
// Use case: Annuler une reaffectation (cleanup QW11)
// Supprime OCCUPIES du nouveau tenant, restaure pour l'ancien

MATCH (new:Tenant {id: $new_tenant_id})-[r:OCCUPIES]->(s:Space {id: $space_id})
DELETE r
WITH s
MATCH (old:Tenant {id: $old_tenant_id})
MERGE (old)-[:OCCUPIES]->(s)
RETURN
    s.id AS space_id,
    $old_tenant_id AS restored_tenant_id,
    $new_tenant_id AS removed_tenant_id,
    true AS reverted;
