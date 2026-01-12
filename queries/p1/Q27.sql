-- Q27: Evacuation Path
-- Status: DEGRADED pour P1 (CTE avec accumulation poids, non optimal)
-- Semantic: Find shortest evacuation path from space to emergency exit
-- Parametres: $1 = SPACE_ID

WITH RECURSIVE paths AS (
    SELECT
        s.id AS current_id,
        s.name AS current_name,
        ARRAY[s.id]::text[] AS path,
        ARRAY[s.name]::text[] AS path_names,
        0::float AS total_distance,
        0 AS depth
    FROM spaces s
    WHERE s.id = $1 AND NOT COALESCE(s.is_exit, false)

    UNION ALL

    SELECT
        s2.id,
        s2.name,
        p.path || s2.id,
        p.path_names || s2.name,
        p.total_distance + COALESCE(e.distance, 1.0),
        p.depth + 1
    FROM paths p
    JOIN edges e ON e.source_id = p.current_id
        AND e.rel_type IN ('EMERGENCY_EXIT', 'ACCESSIBLE_FROM')
    JOIN spaces s2 ON s2.id = e.target_id
    WHERE p.depth < 15
      AND NOT (s2.id = ANY(p.path))
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
    JOIN spaces exit_space ON exit_space.id = p.current_id
    WHERE exit_space.is_exit = true
    ORDER BY total_distance
    LIMIT 1
) shortest,
LATERAL generate_series(1, array_length(path, 1)) AS idx
ORDER BY path_index;
