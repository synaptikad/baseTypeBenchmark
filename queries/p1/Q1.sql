-- Q1: Energy Chain
-- Paramètre: $1 = METER_ID

WITH RECURSIVE energy_chain AS (
    -- Base: le compteur source (depth=0, sera exclu)
    SELECT
        e.id,
        e.equipment_type AS type,
        e.name,
        0 AS depth
    FROM equipment e
    WHERE e.id = $1

    UNION ALL

    -- Récursion: suivre FEEDS downstream
    SELECT
        eq.id,
        eq.equipment_type AS type,
        eq.name,
        ec.depth + 1
    FROM energy_chain ec
    JOIN edges ed ON ed.source_id = ec.id AND ed.rel_type = 'FEEDS'
    JOIN equipment eq ON eq.id = ed.target_id
    WHERE ec.depth < 10
)
SELECT id, type, name, depth
FROM energy_chain
WHERE depth > 0
ORDER BY depth, id;
