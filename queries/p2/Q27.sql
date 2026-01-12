-- Q27: Evacuation Path (P2 JSONB)
-- Status: DEGRADED pour P2 (CTE avec accumulation poids, non optimal)
-- Semantic: Find shortest evacuation path from space to emergency exit
-- Parametres: $1 = SPACE_ID

WITH RECURSIVE paths AS (
    SELECT
        n.id AS current_id,
        n.name AS current_name,
        ARRAY[n.id]::text[] AS path,
        ARRAY[n.name]::text[] AS path_names,
        0::float AS total_distance,
        0 AS depth
    FROM nodes n
    WHERE n.id = $1
      AND n.node_type = 'Space'
      AND NOT COALESCE((n.data->>'is_exit')::boolean, false)

    UNION ALL

    SELECT
        n2.id,
        n2.name,
        p.path || n2.id,
        p.path_names || n2.name,
        p.total_distance + COALESCE((e.data->>'distance')::float, 1.0),
        p.depth + 1
    FROM paths p
    JOIN edges e ON e.source_id = p.current_id
        AND e.rel_type IN ('EMERGENCY_EXIT', 'ACCESSIBLE_FROM')
    JOIN nodes n2 ON n2.id = e.target_id AND n2.node_type = 'Space'
    WHERE p.depth < 15
      AND NOT (n2.id = ANY(p.path))
)
SELECT
    ROW_NUMBER() OVER (ORDER BY idx) - 1 AS path_index,
    path[idx] AS node_id,
    path_names[idx] AS node_name,
    CASE WHEN idx = 1 THEN 0.0
         ELSE total_distance * (idx - 1)::float / array_length(path, 1)
    END AS total_distance
FROM (
    SELECT path, path_names, total_distance
    FROM paths p
    JOIN nodes exit_space ON exit_space.id = p.current_id
    WHERE (exit_space.data->>'is_exit')::boolean = true
    ORDER BY total_distance
    LIMIT 1
) shortest,
LATERAL generate_series(1, array_length(path, 1)) AS idx
ORDER BY path_index;
