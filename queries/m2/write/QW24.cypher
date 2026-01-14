// QW24: Revert Tenant Merge (Cleanup for QW12)
// Annule une fusion de tenants: transfere les relations du target vers le source
// Parametres: $source_tenant_id, $target_tenant_id, $space_ids (liste), $meter_ids (liste)
//
// Use case: Annuler une fusion de tenants (cleanup QW12)
// Restaure les OCCUPIES et METERS_TENANT vers le tenant source original
// Note: Necessite les listes des espaces et meters qui ont ete transferes

MATCH (src:Tenant {id: $source_tenant_id})
MATCH (tgt:Tenant {id: $target_tenant_id})

// Restaurer les OCCUPIES: supprimer de target, creer vers source
WITH src, tgt
OPTIONAL MATCH (tgt)-[r:OCCUPIES]->(s:Space)
WHERE s.id IN $space_ids
WITH src, tgt, collect(r) AS rels_to_delete, collect(s) AS spaces
FOREACH (r IN rels_to_delete | DELETE r)
WITH src, tgt, spaces
UNWIND CASE WHEN size(spaces) > 0 THEN spaces ELSE [null] END AS space
WITH src, tgt, space WHERE space IS NOT NULL
MERGE (src)-[:OCCUPIES]->(space)
WITH src, tgt, count(space) AS spaces_restored

// Restaurer les METERS_TENANT: supprimer vers target, creer vers source
OPTIONAL MATCH (m:Equipment)-[r:METERS_TENANT]->(tgt)
WHERE m.id IN $meter_ids
WITH src, tgt, spaces_restored, collect(r) AS meter_rels, collect(m) AS meters
FOREACH (r IN meter_rels | DELETE r)
WITH src, tgt, spaces_restored, meters
UNWIND CASE WHEN size(meters) > 0 THEN meters ELSE [null] END AS meter
WITH src, tgt, spaces_restored, meter WHERE meter IS NOT NULL
MERGE (meter)-[:METERS_TENANT]->(src)

RETURN
    $source_tenant_id AS source_tenant_id,
    $target_tenant_id AS target_tenant_id,
    spaces_restored,
    count(meter) AS meters_restored;
