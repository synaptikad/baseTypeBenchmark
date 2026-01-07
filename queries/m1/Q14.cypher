// Q14: Protocol Query (BACnet)
// Status: DEGRADED pour M1/M2
// Note: Suppose que protocol_device_id est exporté comme propriété
// Paramètre: $device_id

MATCH (p:Point)
WHERE p.protocol_type = 'BACnet'
  AND p.protocol_device_id = $device_id
RETURN
    p.id AS point_id,
    p.name AS point_name,
    p.equipment_id AS equipment_id,
    p.protocol_object_type AS object_type,
    p.protocol_object_instance AS object_instance
ORDER BY equipment_id, point_id;

// Si protocol n'est pas exporté, retourner vide avec message
// RETURN "DEGRADED: Requiert protocol exporté comme propriété" AS warning;
