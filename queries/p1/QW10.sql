-- QW10: Tenant Move-Out
-- Supprimer relation OCCUPIES (METERS_TENANT reste pour historique)
-- Paramètres: %(tenant_id)s, %(space_id)s

DELETE FROM edges
WHERE source_id = %(tenant_id)s
  AND target_id = %(space_id)s
  AND rel_type = 'OCCUPIES'
RETURNING source_id AS tenant_id, target_id AS space_id, 1 AS relations_deleted;
