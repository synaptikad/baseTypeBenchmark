-- QW23: Revert Space Reassignment (Cleanup for QW11)
-- Annule une reaffectation d'espace: supprime nouveau + insere ancien
-- Parametres: %(space_id)s, %(old_tenant_id)s, %(new_tenant_id)s
--
-- Use case: Annuler une reaffectation (cleanup QW11)
-- Supprime OCCUPIES du nouveau tenant, restaure pour l'ancien

WITH deleted AS (
    DELETE FROM p2.edges
    WHERE source_id = %(new_tenant_id)s
      AND target_id = %(space_id)s
      AND rel_type = 'OCCUPIES'
    RETURNING target_id
),
inserted AS (
    INSERT INTO p2.edges (source_id, target_id, rel_type)
    SELECT %(old_tenant_id)s, %(space_id)s, 'OCCUPIES'
    WHERE EXISTS (SELECT 1 FROM deleted)
    ON CONFLICT DO NOTHING
    RETURNING target_id
)
SELECT
    %(space_id)s AS space_id,
    %(old_tenant_id)s AS restored_tenant_id,
    %(new_tenant_id)s AS removed_tenant_id,
    EXISTS (SELECT 1 FROM inserted) AS reverted;
