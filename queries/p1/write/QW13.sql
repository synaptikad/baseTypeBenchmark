-- QW13: Cancel Space Reservation
-- Supprimer une relation OCCUPIES entre un tenant et un espace avec dates
-- Parametres: %(tenant_id)s, %(space_id)s, %(start_date)s, %(end_date)s
--
-- Use case: Annuler une reservation d'espace (cleanup de QW9)
-- Note: P1 n'a pas de proprietes sur edges, on filtre par source/target/type

DELETE FROM p1.edges
WHERE source_id = %(tenant_id)s
  AND target_id = %(space_id)s
  AND rel_type = 'OCCUPIES'
RETURNING source_id AS tenant_id, target_id AS space_id, 1 AS reservations_cancelled;
