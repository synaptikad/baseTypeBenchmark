-- Q20: Shortest HVAC Path
-- Status: DEGRADED pour P1 (CTE explore tout)
-- Parametres: $1 = EQUIPMENT_ID, $2 = SPACE_ID

WITH RECURSIVE paths AS (
    -- Base: depart de l'equipement
    SELECT
        eq.id AS node_id,
        'Equipment' AS node_type,
        eq.name AS node_name,
        ARRAY[eq.id]::text[] AS path,
        ARRAY['Equipment']::text[] AS path_types,
        ARRAY[eq.name]::text[] AS path_names,
        0 AS depth
    FROM equipment eq
    WHERE eq.id = $1

    UNION ALL

    -- Recursion via FEEDS et SERVES
    SELECT
        COALESCE(eq2.id, s.id) AS node_id,
        CASE WHEN eq2.id IS NOT NULL THEN 'Equipment' ELSE 'Space' END AS node_type,
        COALESCE(eq2.name, s.name) AS node_name,
        p.path || COALESCE(eq2.id, s.id)::text,
        p.path_types || CASE WHEN eq2.id IS NOT NULL THEN 'Equipment' ELSE 'Space' END,
        p.path_names || COALESCE(eq2.name, s.name),
        p.depth + 1
    FROM paths p
    JOIN edges e ON e.source_id = p.node_id AND e.rel_type IN ('FEEDS', 'SERVES')
    LEFT JOIN equipment eq2 ON eq2.id = e.target_id
    LEFT JOIN spaces s ON s.id = e.target_id
    WHERE p.depth < 10
      AND NOT (COALESCE(eq2.id, s.id)::text = ANY(p.path))
),
shortest AS (
    SELECT path, path_types, path_names
    FROM paths
    WHERE node_id = $2
    ORDER BY depth
    LIMIT 1
)
SELECT
    idx - 1 AS path_index,
    path[idx] AS node_id,
    path_types[idx] AS node_type,
    path_names[idx] AS node_name
FROM shortest,
     LATERAL generate_series(1, array_length(path, 1)) AS idx
ORDER BY path_index;

-- Note: Retourne tous les noeuds du chemin le plus court trouve
