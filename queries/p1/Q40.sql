-- Q40: Verify Tenant Meters
-- P1 version: uses equipment table
-- Paramètres: %(tenant_id)s
-- Validates: QW9 (Move-In with meter)

SELECT
    e.source_id AS meter_id,
    eq.name AS meter_name,
    eq.equipment_type AS meter_type
FROM p1.edges e
JOIN p1.equipment eq ON eq.id = e.source_id
WHERE e.target_id = %(tenant_id)s
  AND e.rel_type = 'METERS_TENANT'
ORDER BY meter_id;
