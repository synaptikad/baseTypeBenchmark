-- QW19: Remove Capability (Cleanup for QW7)
-- Retire une capability d'un array JSONB
-- Parametres: %(equipment_id)s, %(capability_to_remove)s
--
-- Use case: Annuler l'ajout d'une capability (cleanup QW7)
-- Utilise array_remove avec conversion JSON

UPDATE p2.nodes
SET data = jsonb_set(
    data,
    '{capabilities}',
    (
        SELECT COALESCE(jsonb_agg(elem), '[]'::jsonb)
        FROM jsonb_array_elements(COALESCE(data->'capabilities', '[]'::jsonb)) AS elem
        WHERE elem::text != to_jsonb(%(capability_to_remove)s::text)::text
    )
)
WHERE id = %(equipment_id)s
  AND node_type = 'Equipment'
  AND data->'capabilities' @> jsonb_build_array(%(capability_to_remove)s::text)
RETURNING
    id,
    data->'capabilities' AS updated_capabilities;
