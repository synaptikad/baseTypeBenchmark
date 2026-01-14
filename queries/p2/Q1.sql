-- Q1: Energy Chain (P2 JSONB)
-- Paramètre: $1 = METER_ID

WITH RECURSIVE energy_chain AS (
    -- Base: le compteur source (depth=0, sera exclu)
    SELECT
        n.id,
        n.data->>'equipment_type' AS type,
        n.name,
        0 AS depth
    FROM nodes n
    WHERE n.id = $1
      AND n.node_type = 'Equipment'

    UNION ALL

    -- Récursion: suivre FEEDS downstream
    SELECT
        n.id,
        n.data->>'equipment_type' AS type,
        n.name,
        ec.depth + 1
    FROM energy_chain ec
    JOIN edges ed ON ed.source_id = ec.id AND ed.rel_type = 'FEEDS'
    JOIN nodes n ON n.id = ed.target_id
    WHERE ec.depth < 10
)
SELECT id, type, name, depth
FROM energy_chain
WHERE depth > 0
ORDER BY depth, id;
