-- Q39: Verify Tenant Spaces
-- P1 version: uses spaces table
-- Paramètres: %(tenant_id)s
-- Validates: QW9 (Move-In), QW10 (Move-Out), QW11 (Reassignment)

SELECT
    e.target_id AS space_id,
    s.name AS space_name,
    'Space' AS space_type
FROM p1.edges e
JOIN p1.spaces s ON s.id = e.target_id
WHERE e.source_id = %(tenant_id)s
  AND e.rel_type = 'OCCUPIES'
ORDER BY space_id;
