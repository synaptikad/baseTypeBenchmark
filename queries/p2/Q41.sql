-- Q41: Verify Tenant Consolidation
-- Après un merge, vérifier le nombre total de relations du tenant target
-- Paramètres: %(tenant_id)s
-- Validates: QW12 (Tenant Merge)

SELECT
    %(tenant_id)s AS tenant_id,
    COUNT(*) FILTER (WHERE e.rel_type = 'OCCUPIES' AND e.source_id = %(tenant_id)s) AS occupied_spaces,
    COUNT(*) FILTER (WHERE e.rel_type = 'METERS_TENANT' AND e.target_id = %(tenant_id)s) AS associated_meters
FROM edges e
WHERE (e.source_id = %(tenant_id)s AND e.rel_type = 'OCCUPIES')
   OR (e.target_id = %(tenant_id)s AND e.rel_type = 'METERS_TENANT');
