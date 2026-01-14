-- QW13: Cancel Space Reservation
-- Supprimer une relation OCCUPIES entre un tenant et un espace avec dates
-- Parametres: %(tenant_id)s, %(space_id)s, %(start_date)s, %(end_date)s
--
-- Use case: Annuler une reservation d'espace (cleanup de QW9)
-- P2 peut filtrer sur properties si les dates sont stockees

DELETE FROM p2.edges
WHERE source_id = %(tenant_id)s
  AND target_id = %(space_id)s
  AND rel_type = 'OCCUPIES'
  AND (
    properties->>'start_date' IS NULL
    OR properties->>'start_date' = %(start_date)s
  )
RETURNING source_id AS tenant_id, target_id AS space_id, 1 AS reservations_cancelled;
