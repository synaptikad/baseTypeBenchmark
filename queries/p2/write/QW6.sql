-- QW6: JSONB Merge (Bulk Metadata Update)
-- Démontre: Fusion de plusieurs champs JSONB en une opération
-- Paramètres: %(equipment_id)s, %(metadata_patch)s (jsonb object)
--
-- Use case: Mettre à jour plusieurs champs metadata en une fois
-- Préserve les champs non mentionnés dans le patch
-- Exemple metadata_patch: {"firmware_version": "2.1.0", "last_update": "2024-06-15"}

UPDATE p2.nodes
SET data = jsonb_set(
    COALESCE(data, '{}'::jsonb),
    '{metadata}',
    COALESCE(data->'metadata', '{}'::jsonb) || %(metadata_patch)s::jsonb,
    true
)
WHERE id = %(equipment_id)s
  AND node_type = 'Equipment'
RETURNING
    id,
    data->'metadata' AS merged_metadata;
