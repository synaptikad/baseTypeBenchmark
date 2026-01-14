-- QW22: Cancel Move-Out (Cleanup for QW10)
-- Restaure la relation OCCUPIES supprimee par move-out
-- Parametres: %(tenant_id)s, %(space_id)s
--
-- Use case: Annuler un demenagement (cleanup QW10)
-- Recree OCCUPIES entre tenant et space

INSERT INTO p2.edges (source_id, target_id, rel_type)
VALUES (%(tenant_id)s, %(space_id)s, 'OCCUPIES')
ON CONFLICT DO NOTHING
RETURNING
    source_id AS tenant_id,
    target_id AS space_id,
    1 AS relations_restored;
