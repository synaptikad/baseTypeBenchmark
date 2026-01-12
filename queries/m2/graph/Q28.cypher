// Q28: Tenant Impact Chain
// Status: NATIVE pour M1/M2 (5-hop chain traversal)
// Semantic: If this submeter is cut, which tenants are impacted?
// Parametres: $meter_id

MATCH (meter:Equipment {id: $meter_id})
WHERE meter.equipment_type IN ['SubMeter', 'MainMeter']
MATCH (meter)-[:FEEDS*1..3]->(equip:Equipment)-[:SERVES]->(space:Space)<-[:OCCUPIES]-(tenant:Tenant)
WITH tenant,
     collect(DISTINCT space.id) AS affected_space_ids,
     collect(DISTINCT equip.id) AS affected_equipment_ids
RETURN
    tenant.id AS tenant_id,
    tenant.name AS tenant_name,
    size(affected_space_ids) AS affected_spaces,
    size(affected_equipment_ids) AS affected_equipment
ORDER BY affected_equipment DESC, tenant_id;
