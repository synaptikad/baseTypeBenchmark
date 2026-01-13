-- Q39: Verify Tenant Spaces
-- Lister tous les espaces occupés par un locataire donné
-- Paramètres: %(tenant_id)s
-- Validates: QW9 (Move-In), QW10 (Move-Out), QW11 (Reassignment)

SELECT
    e.target_id AS space_id,
    n.name AS space_name,
    n.node_type AS space_type
FROM edges e
JOIN nodes n ON n.id = e.target_id
WHERE e.source_id = %(tenant_id)s
  AND e.rel_type = 'OCCUPIES'
ORDER BY space_id;
