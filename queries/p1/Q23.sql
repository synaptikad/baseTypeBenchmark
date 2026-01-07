-- Q23: Adjacency Propagation
-- Status: NATIVE pour P1 (CTE avec depth)
-- Parametres: $1 = SPACE_ID, $2 = MAX_HOPS

WITH RECURSIVE propagation AS (
    SELECT
        s.id AS node_id,
        'Space' AS node_type,
        s.name AS node_name,
        0 AS hop_distance,
        ''::text AS via_relation
    FROM spaces s
    WHERE s.id = $1

    UNION ALL

    SELECT
        COALESCE(s2.id, eq.id) AS node_id,
        CASE WHEN s2.id IS NOT NULL THEN 'Space' ELSE 'Equipment' END AS node_type,
        COALESCE(s2.name, eq.name) AS node_name,
        p.hop_distance + 1,
        e.rel_type AS via_relation
    FROM propagation p
    JOIN edges e ON (e.source_id = p.node_id OR e.target_id = p.node_id)
        AND e.rel_type IN ('ADJACENT_TO', 'CONTAINS', 'MONITORS', 'SERVES')
    LEFT JOIN spaces s2 ON s2.id = CASE WHEN e.source_id = p.node_id THEN e.target_id ELSE e.source_id END
    LEFT JOIN equipment eq ON eq.id = CASE WHEN e.source_id = p.node_id THEN e.target_id ELSE e.source_id END
    WHERE p.hop_distance < $2
)
SELECT DISTINCT node_id, node_type, node_name, hop_distance, via_relation
FROM propagation
WHERE hop_distance > 0
ORDER BY hop_distance, node_type, node_id;
