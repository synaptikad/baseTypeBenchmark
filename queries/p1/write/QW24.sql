-- QW24: Revert Tenant Merge (Cleanup for QW12)
-- Annule une fusion de tenants: transfere les relations du target vers le source
-- Parametres: %(source_tenant_id)s, %(target_tenant_id)s, %(space_ids)s (array), %(meter_ids)s (array)
--
-- Use case: Annuler une fusion de tenants (cleanup QW12)
-- Restaure les OCCUPIES et METERS_TENANT vers le tenant source original
-- Note: Necessite les listes des espaces et meters qui ont ete transferes

WITH occupies_restored AS (
    UPDATE p1.edges
    SET source_id = %(source_tenant_id)s
    WHERE source_id = %(target_tenant_id)s
      AND rel_type = 'OCCUPIES'
      AND target_id = ANY(%(space_ids)s::text[])
    RETURNING 1
),
meters_restored AS (
    UPDATE p1.edges
    SET target_id = %(source_tenant_id)s
    WHERE target_id = %(target_tenant_id)s
      AND rel_type = 'METERS_TENANT'
      AND source_id = ANY(%(meter_ids)s::text[])
    RETURNING 1
)
SELECT
    %(source_tenant_id)s AS source_tenant_id,
    %(target_tenant_id)s AS target_tenant_id,
    (SELECT count(*) FROM occupies_restored) AS spaces_restored,
    (SELECT count(*) FROM meters_restored) AS meters_restored;
