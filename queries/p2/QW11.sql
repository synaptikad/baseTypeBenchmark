-- QW11: Space Reassignment
-- Réaffecter un espace d'un tenant à un autre (atomique)
-- Paramètres: %(space_id)s, %(old_tenant_id)s, %(new_tenant_id)s

WITH deleted AS (
    DELETE FROM edges
    WHERE source_id = %(old_tenant_id)s
      AND target_id = %(space_id)s
      AND rel_type = 'OCCUPIES'
    RETURNING target_id
),
inserted AS (
    INSERT INTO edges (source_id, target_id, rel_type)
    SELECT %(new_tenant_id)s, %(space_id)s, 'OCCUPIES'
    WHERE EXISTS (SELECT 1 FROM deleted)
    RETURNING target_id
)
SELECT %(space_id)s AS space_id,
       %(old_tenant_id)s AS old_tenant_id,
       %(new_tenant_id)s AS new_tenant_id,
       EXISTS (SELECT 1 FROM inserted) AS reassigned;
