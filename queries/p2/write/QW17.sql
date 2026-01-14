-- QW17: Remove Calibration Info
-- Supprimer le bloc calibration des metadata/properties
-- Parametres: %(point_id)s
--
-- Use case: Nettoyer les informations de calibration (cleanup de QW5)
-- Supprime entierement le bloc calibration

UPDATE p2.nodes
SET data = data #- '{calibration}'
WHERE id = %(point_id)s
  AND node_type = 'Point'
  AND data ? 'calibration'
RETURNING id, 1 AS calibration_removed;
