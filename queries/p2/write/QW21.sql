-- QW21: Cancel Move-In (Cleanup for QW9)
-- Supprime les relations OCCUPIES et METERS_TENANT creees par move-in
-- Parametres: %(tenant_id)s, %(space_id)s, %(meter_id)s (optionnel)
--
-- Use case: Annuler un emmenagement (cleanup QW9)
-- Supprime OCCUPIES entre tenant et space
-- Supprime METERS_TENANT entre meter et tenant si meter_id fourni

WITH deleted_occupies AS (
    DELETE FROM p2.edges
    WHERE source_id = %(tenant_id)s
      AND target_id = %(space_id)s
      AND rel_type = 'OCCUPIES'
    RETURNING 1 AS cnt
),
deleted_meters AS (
    DELETE FROM p2.edges
    WHERE source_id = %(meter_id)s
      AND target_id = %(tenant_id)s
      AND rel_type = 'METERS_TENANT'
      AND %(meter_id)s IS NOT NULL
    RETURNING 1 AS cnt
)
SELECT
    %(tenant_id)s AS tenant_id,
    %(space_id)s AS space_id,
    (SELECT count(*) FROM deleted_occupies) AS occupies_deleted,
    (SELECT count(*) FROM deleted_meters) AS meters_deleted;
