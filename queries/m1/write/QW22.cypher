// QW22: Cancel Move-Out (Cleanup for QW10)
// Restaure la relation OCCUPIES supprimee par move-out
// Parametres: $tenant_id, $space_id
//
// Use case: Annuler un demenagement (cleanup QW10)
// Recree OCCUPIES entre tenant et space

MATCH (t:Tenant {id: $tenant_id})
MATCH (s:Space {id: $space_id})
MERGE (t)-[r:OCCUPIES]->(s)
RETURN
    t.id AS tenant_id,
    s.id AS space_id,
    1 AS relations_restored;
