-- Q40: Verify Tenant Meters
-- Lister tous les compteurs associés à un locataire (via METERS_TENANT)
-- Paramètres: %(q40_tenant_id)s
-- Note: Uses q40_tenant_id (different from QW10's tenant) to persist across runs

SELECT
    e.source_id AS meter_id,
    n.name AS meter_name,
    n.node_type AS meter_type
FROM edges e
JOIN nodes n ON n.id = e.source_id
WHERE e.target_id = %(q40_tenant_id)s
  AND e.rel_type = 'METERS_TENANT'
ORDER BY meter_id;
