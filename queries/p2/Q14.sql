-- Q14: Protocol Query (BACnet)
-- Status: NATIVE pour P2
-- Paramètres: $1 = DEVICE_ID (integer, ex: 1234)

SELECT
    p.id AS point_id,
    p.name AS point_name,
    p.data->>'equipment_id' AS equipment_id,
    p.data->'protocol'->>'object_type' AS object_type,
    (p.data->'protocol'->>'object_instance')::integer AS object_instance
FROM nodes p
WHERE p.node_type = 'Point'
  AND p.data->'protocol'->>'type' = 'BACnet'
  AND (p.data->'protocol'->>'device_id')::integer = $1
ORDER BY p.data->>'equipment_id', p.id;
