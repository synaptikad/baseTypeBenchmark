// QW21: Cancel Move-In (Cleanup for QW9)
// Supprime les relations OCCUPIES et METERS_TENANT creees par move-in
// Parametres: $tenant_id, $space_id, $meter_id (optionnel)
//
// Use case: Annuler un emmenagement (cleanup QW9)
// Supprime OCCUPIES entre tenant et space
// Supprime METERS_TENANT entre meter et tenant si existe

MATCH (t:Tenant {id: $tenant_id})-[r:OCCUPIES]->(s:Space {id: $space_id})
DELETE r
WITH t, 1 AS occupies_deleted
OPTIONAL MATCH (m:Equipment {id: $meter_id})-[rm:METERS_TENANT]->(t)
WHERE $meter_id IS NOT NULL
DELETE rm
RETURN
    t.id AS tenant_id,
    $space_id AS space_id,
    occupies_deleted,
    CASE WHEN rm IS NOT NULL THEN 1 ELSE 0 END AS meters_deleted;
