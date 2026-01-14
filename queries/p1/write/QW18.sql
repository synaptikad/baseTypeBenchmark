-- QW18: Remove Firmware Info
-- Supprimer les champs firmware_version et last_update des metadata
-- Parametres: %(equipment_id)s
--
-- Use case: Nettoyer les informations firmware (cleanup de QW6)
-- Supprime firmware_version et last_update du bloc metadata

UPDATE p1.nodes
SET data = data #- '{metadata,firmware_version}' #- '{metadata,last_update}'
WHERE id = %(equipment_id)s
  AND (data->'metadata' ? 'firmware_version' OR data->'metadata' ? 'last_update')
RETURNING id, data->'metadata' AS cleaned_metadata;
