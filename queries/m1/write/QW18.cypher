// QW18: Remove Firmware Info
// Supprimer les proprietes firmware_version et last_update
// Parametres: $equipment_id
//
// Use case: Nettoyer les informations firmware (cleanup de QW6)

MATCH (eq:Equipment {id: $equipment_id})
REMOVE eq.firmware_version,
       eq.firmware_update_date,
       eq.firmware_update_by
RETURN eq.id AS id, 1 AS firmware_info_removed;
