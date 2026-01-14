-- Q21: Electrical Resilience (SPOF Detection)
-- Status: DEGRADED pour P1 (explosion combinatoire)
-- Parametres: $1 = EQUIPMENT_ID, $2 = SOURCE_TYPE

WITH RECURSIVE all_paths AS (
    SELECT
        eq.id AS current_id,
        ARRAY[eq.id]::text[] AS path,
        0 AS depth
    FROM equipment eq
    WHERE eq.id = $1

    UNION ALL

    SELECT
        eq.id,
        ap.path || eq.id::text,
        ap.depth + 1
    FROM all_paths ap
    JOIN edges e ON e.target_id = ap.current_id AND e.rel_type = 'FEEDS'
    JOIN equipment eq ON eq.id = e.source_id
    WHERE ap.depth < 10
      AND NOT (eq.id::text = ANY(ap.path))
),
complete_paths AS (
    SELECT path
    FROM all_paths ap
    JOIN equipment eq ON eq.id = ap.current_id
    WHERE eq.equipment_type = $2
),
-- Inverser le path pour avoir source->target (comme M1)
reversed_paths AS (
    SELECT array_agg(elem ORDER BY idx DESC) AS path_nodes
    FROM complete_paths,
         LATERAL unnest(path) WITH ORDINALITY AS t(elem, idx)
    GROUP BY path
)
SELECT
    ROW_NUMBER() OVER () AS path_id,
    path_nodes,
    array_length(path_nodes, 1) - 1 AS path_length
FROM reversed_paths
ORDER BY path_length, path_id;

-- Note: SPOF = noeuds presents dans TOUS les chemins (calcul applicatif requis)
