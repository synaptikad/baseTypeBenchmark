-- QW20: Restore Removed Key (Cleanup for QW8)
-- Restaure une cle JSONB precedemment supprimee
-- Parametres: %(node_id)s, %(key_to_restore)s, %(value_to_restore)s
--
-- Use case: Annuler la suppression d'une cle metadata (cleanup QW8)
-- Utilise jsonb || jsonb_build_object pour ajouter la cle

UPDATE p2.nodes
SET data = jsonb_set(
    COALESCE(data, '{}'::jsonb),
    '{metadata}',
    COALESCE(data->'metadata', '{}'::jsonb) || jsonb_build_object(%(key_to_restore)s, %(value_to_restore)s)
)
WHERE id = %(node_id)s
RETURNING
    id,
    data->'metadata' AS restored_metadata;
