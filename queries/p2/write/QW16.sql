-- QW16: Remove Maintenance Event
-- Supprimer le champ maintenance_history des metadata
-- Parametres: %(equipment_id)s
--
-- Use case: Nettoyer l'historique de maintenance (cleanup de QW4)
-- Supprime entierement le champ maintenance_history

UPDATE p2.nodes
SET data = data #- '{maintenance_history}'
WHERE id = %(equipment_id)s
  AND node_type = 'Equipment'
  AND data ? 'maintenance_history'
RETURNING id, 1 AS maintenance_history_removed;
