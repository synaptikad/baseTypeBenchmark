-- QW15: Remove Relation
-- Supprimer une relation par source/target/type
-- Parametres: %(source_id)s, %(target_id)s, %(rel_type)s
--
-- Use case: Supprimer une relation specifique entre deux noeuds

DELETE FROM p2.edges
WHERE source_id = %(source_id)s
  AND target_id = %(target_id)s
  AND rel_type = %(rel_type)s
RETURNING source_id, target_id, rel_type, 1 AS relations_deleted;
