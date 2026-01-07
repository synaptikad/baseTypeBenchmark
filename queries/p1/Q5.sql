-- Q5: Orphans
-- Pas de paramètre

SELECT
    eq.id,
    eq.equipment_type AS type,
    eq.name
FROM equipment eq
WHERE NOT EXISTS (
    SELECT 1 FROM edges e
    WHERE e.source_id = eq.id OR e.target_id = eq.id
)
ORDER BY eq.equipment_type, eq.id;
