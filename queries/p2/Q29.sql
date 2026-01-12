-- Q29: All Power Paths (P2 JSONB)
-- Status: DEGRADED pour P2 (CTE avec ARRAY accumulation, risque memoire)
-- Semantic: Enumerate all electrical paths from transformer to critical equipment
-- Parametres: $1 = TRANSFORMER_ID

WITH RECURSIVE all_paths AS (
    SELECT
        n.id AS current_id,
        ARRAY[n.id]::text[] AS path_nodes,
        1 AS path_length
    FROM nodes n
    WHERE n.id = $1
      AND n.node_type = 'Equipment'
      AND n.data->>'equipment_type' = 'Transformer_HT_BT'

    UNION ALL

    SELECT
        n.id,
        ap.path_nodes || n.id,
        ap.path_length + 1
    FROM all_paths ap
    JOIN edges e ON e.source_id = ap.current_id AND e.rel_type = 'FEEDS'
    JOIN nodes n ON n.id = e.target_id AND n.node_type = 'Equipment'
    WHERE ap.path_length < 10
      AND NOT (n.id = ANY(ap.path_nodes))
)
SELECT
    ROW_NUMBER() OVER (ORDER BY path_length, path_nodes) AS path_id,
    path_nodes,
    path_length,
    path_nodes[array_length(path_nodes, 1)] AS target_equipment
FROM all_paths ap
JOIN nodes n ON n.id = ap.current_id AND n.node_type = 'Equipment'
WHERE COALESCE((n.data->>'critical')::boolean, false) = true
ORDER BY path_length, path_id
LIMIT 100;
