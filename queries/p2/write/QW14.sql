-- QW14: Remove Calibration Tag
-- Supprimer une cle specifique des metadata
-- Parametres: %(node_id)s, %(key_to_remove)s
--
-- Use case: Retirer un tag de calibration obsolete
-- Utilise l'operateur #- pour supprimer la cle

UPDATE p2.nodes
SET data = data #- ARRAY['metadata', %(key_to_remove)s]
WHERE id = %(node_id)s
  AND data->'metadata' ? %(key_to_remove)s
RETURNING id, data->'metadata' AS cleaned_metadata;
