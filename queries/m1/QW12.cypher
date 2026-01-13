// QW12 - Tenant Merge
// Transfer all relationships from source tenant to target tenant
MATCH (tgt:Tenant {id: $target_tenant_id})

// Transfer OCCUPIES relationships
OPTIONAL MATCH (src:Tenant {id: $source_tenant_id})-[r:OCCUPIES]->(s:Space)
WITH tgt, collect(r) AS rels_to_delete, collect(s) AS spaces
FOREACH (r IN rels_to_delete | DELETE r)
WITH tgt, spaces
UNWIND CASE WHEN size(spaces) > 0 THEN spaces ELSE [null] END AS space
WITH tgt, space WHERE space IS NOT NULL
MERGE (tgt)-[:OCCUPIES]->(space)
WITH tgt, count(space) AS spaces_transferred

// Transfer METERS_TENANT relationships
OPTIONAL MATCH (m:Equipment)-[r:METERS_TENANT]->(src:Tenant {id: $source_tenant_id})
WITH tgt, spaces_transferred, collect(r) AS meter_rels, collect(m) AS meters
FOREACH (r IN meter_rels | DELETE r)
WITH tgt, spaces_transferred, meters
UNWIND CASE WHEN size(meters) > 0 THEN meters ELSE [null] END AS meter
WITH tgt, spaces_transferred, meter WHERE meter IS NOT NULL
MERGE (meter)-[:METERS_TENANT]->(tgt)

RETURN $source_tenant_id AS source_tenant_id,
       $target_tenant_id AS target_tenant_id,
       spaces_transferred,
       count(meter) AS meters_transferred
