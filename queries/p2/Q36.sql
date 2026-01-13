-- Q36: Validate Metadata Tag Update (QW2)
-- Status: NATIVE pour P2 (JSONB data storage)
-- Paramètres: %(node_id)s
-- Semantic: Vérifie que le tag calibration_status a été mis à jour

SELECT
    n.id AS node_id,
    n.name AS node_name,
    n.data->>'calibration_status' AS custom_tag,
    n.node_type AS node_type
FROM p2.nodes n
WHERE n.id = %(node_id)s;
