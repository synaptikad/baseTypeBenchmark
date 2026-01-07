// Q11: IT Infrastructure Impact
// Parametre: $ups_id

MATCH path = (ups:Equipment {id: $ups_id})-[:FEEDS*1..5]->(target:Equipment)
WHERE target.equipment_type IN ['RackServer', 'NetworkSwitch', 'StorageArray']
WITH target, length(path) AS depth
RETURN
    target.id AS equipment_id,
    target.name AS equipment_name,
    target.equipment_type AS equipment_type,
    depth
ORDER BY depth, equipment_type, equipment_id;
