-- QW10: Tenant Move-Out
-- Supprimer TOUTES les relations OCCUPIES et METERS_TENANT pour un tenant
-- Paramètres: %(tenant_id)s
-- Note: OCCUPIES = (tenant)-[:OCCUPIES]->(space), METERS_TENANT = (meter)-[:METERS_TENANT]->(tenant)

WITH deleted_occupies AS (
    DELETE FROM edges
    WHERE source_id = %(tenant_id)s
      AND rel_type = 'OCCUPIES'
    RETURNING 1 AS cnt
),
deleted_meters AS (
    DELETE FROM edges
    WHERE target_id = %(tenant_id)s
      AND rel_type = 'METERS_TENANT'
    RETURNING 1 AS cnt
)
SELECT
    %(tenant_id)s AS tenant_id,
    (SELECT COUNT(*) FROM deleted_occupies) AS occupies_deleted,
    (SELECT COUNT(*) FROM deleted_meters) AS meters_deleted;
