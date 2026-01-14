-- Q20: Shortest HVAC Path (P2 JSONB)
-- Status: DEGRADED pour P2 (CTE explore tout)
-- Parametres: $1 = EQUIPMENT_ID, $2 = SPACE_ID

WITH RECURSIVE paths AS (
    SELECT
        n.id AS node_id,
        n.node_type,
        n.name AS node_name,
        ARRAY[n.id]::text[] AS path,
        ARRAY[n.node_type]::text[] AS path_types,
        ARRAY[n.name]::text[] AS path_names,
        0 AS depth
    FROM nodes n
    WHERE n.id = $1

    UNION ALL

    SELECT
        n.id,
        n.node_type,
        n.name,
        p.path || n.id,
        p.path_types || n.node_type,
        p.path_names || n.name,
        p.depth + 1
    FROM paths p
    JOIN edges e ON e.source_id = p.node_id AND e.rel_type IN ('FEEDS', 'SERVES')
    JOIN nodes n ON n.id = e.target_id
    WHERE p.depth < 10
      AND NOT (n.id = ANY(p.path))
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
