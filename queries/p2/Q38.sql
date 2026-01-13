-- Q38: Validate Property Removal (QW8)
-- Status: NATIVE pour P2 (JSONB data storage)
-- Paramètres: %(node_id)s, %(key_to_remove)s
-- Semantic: Vérifie que la clé a été supprimée des metadata

SELECT
    n.id AS node_id,
    n.name AS node_name,
    NOT (n.data->'metadata' ? %(key_to_remove)s) AS key_removed,
    jsonb_object_keys(COALESCE(n.data->'metadata', '{}'::jsonb)) AS remaining_keys
FROM p2.nodes n
WHERE n.id = %(node_id)s;
