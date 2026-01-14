-- Q29: All Power Paths
-- Status: DEGRADED pour P1 (CTE avec ARRAY accumulation, risque memoire)
-- Semantic: Enumerate all electrical paths from transformer to critical equipment
-- Parametres: $1 = TRANSFORMER_ID

WITH RECURSIVE all_paths AS (
    SELECT
        eq.id AS current_id,
        ARRAY[eq.id]::text[] AS path_nodes,
        1 AS path_length
    FROM equipment eq
    WHERE eq.id = $1 AND eq.equipment_type = 'Transformer_HT_BT'

    UNION ALL

    SELECT
        eq.id,
        ap.path_nodes || eq.id,
        ap.path_length + 1
    FROM all_paths ap
    JOIN edges e ON e.source_id = ap.current_id AND e.rel_type = 'FEEDS'
    JOIN equipment eq ON eq.id = e.target_id
    WHERE ap.path_length < 10
      AND NOT (eq.id = ANY(ap.path_nodes))
)
SELECT
    ROW_NUMBER() OVER (ORDER BY path_length, path_nodes) AS path_id,
    path_nodes,
    array_length(path_nodes, 1) AS path_length,
    path_nodes[array_length(path_nodes, 1)] AS target_equipment
FROM all_paths ap
JOIN equipment eq ON eq.id = ap.current_id
WHERE COALESCE(eq.critical, false) = true
  AND ap.path_length > 1  -- Exclure le source (transformer seul)
ORDER BY path_length, path_id
LIMIT 100;
