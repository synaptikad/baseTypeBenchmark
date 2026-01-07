-- Q20: Shortest HVAC Path (P2 JSONB)
-- Status: DEGRADED pour P2 (CTE explore tout)
-- Parametres: $1 = EQUIPMENT_ID, $2 = SPACE_ID

WITH RECURSIVE paths AS (
    SELECT
        n.id AS node_id,
        n.node_type,
        n.name AS node_name,
        ARRAY[n.id] AS path,
        0 AS depth
    FROM nodes n
    WHERE n.id = $1

    UNION ALL

    SELECT
        n.id,
        n.node_type,
        n.name,
        p.path || n.id,
        p.depth + 1
    FROM paths p
    JOIN edges e ON e.source_id = p.node_id AND e.rel_type IN ('FEEDS', 'SERVES')
    JOIN nodes n ON n.id = e.target_id
    WHERE p.depth < 10
      AND NOT (n.id = ANY(p.path))
)
SELECT
    ROW_NUMBER() OVER (ORDER BY depth) - 1 AS path_index,
    node_id,
    node_type,
    node_name
FROM paths
WHERE node_id = $2
ORDER BY depth
LIMIT 1;

-- Note: Retourne le premier chemin trouve (pas garanti le plus court)
