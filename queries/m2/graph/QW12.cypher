// QW12 - Tenant Merge
// Transférer toutes les relations du source vers le target
MATCH (tgt:Tenant {id: $target_tenant_id})

// Transférer OCCUPIES
OPTIONAL MATCH (src:Tenant {id: $source_tenant_id})-[r:OCCUPIES]->(s:Space)
WITH tgt, collect({rel: r, space: s}) AS occupies_rels
UNWIND CASE WHEN size(occupies_rels) > 0 AND occupies_rels[0].rel IS NOT NULL THEN occupies_rels ELSE [] END AS occ
MERGE (tgt)-[:OCCUPIES]->(occ.space)
DELETE occ.rel
WITH tgt, count(occ) AS spaces_transferred

// Transférer METERS_TENANT
OPTIONAL MATCH (m:Equipment)-[r:METERS_TENANT]->(src:Tenant {id: $source_tenant_id})
WITH tgt, spaces_transferred, collect({rel: r, meter: m}) AS meter_rels
UNWIND CASE WHEN size(meter_rels) > 0 AND meter_rels[0].rel IS NOT NULL THEN meter_rels ELSE [] END AS met
MERGE (met.meter)-[:METERS_TENANT]->(tgt)
DELETE met.rel

RETURN $source_tenant_id AS source_tenant_id, $target_tenant_id AS target_tenant_id,
       spaces_transferred, count(met) AS meters_transferred
