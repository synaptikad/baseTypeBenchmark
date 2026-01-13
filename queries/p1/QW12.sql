-- QW12: Tenant Merge
-- Transférer toutes les relations du source vers le target
-- Paramètres: %(source_tenant_id)s, %(target_tenant_id)s

WITH occupies_transferred AS (
    UPDATE edges
    SET source_id = %(target_tenant_id)s
    WHERE source_id = %(source_tenant_id)s
      AND rel_type = 'OCCUPIES'
    RETURNING 1
),
meters_transferred AS (
    UPDATE edges
    SET target_id = %(target_tenant_id)s
    WHERE target_id = %(source_tenant_id)s
      AND rel_type = 'METERS_TENANT'
    RETURNING 1
)
SELECT %(source_tenant_id)s AS source_tenant_id,
       %(target_tenant_id)s AS target_tenant_id,
       (SELECT count(*) FROM occupies_transferred) AS spaces_transferred,
       (SELECT count(*) FROM meters_transferred) AS meters_transferred;
