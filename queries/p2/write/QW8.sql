-- QW8: Remove Key (Deprecate Field)
-- Démontre: Suppression d'une clé JSONB
-- Paramètres: %(node_id)s, %(key_to_remove)s
--
-- Use case: Retirer un champ obsolète des metadata
-- Opérateur - supprime la clé

UPDATE p2.nodes
SET data = data #- ARRAY['metadata', %(key_to_remove)s]
WHERE id = %(node_id)s
  AND data->'metadata' ? %(key_to_remove)s
RETURNING
    id,
    data->'metadata' AS cleaned_metadata;
