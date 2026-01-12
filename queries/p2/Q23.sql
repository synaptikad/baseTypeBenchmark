-- Q23: Failure Impact Analysis (P2 JSONB)
-- Status: NATIVE pour P2 (CTE avec depth)
-- Semantic: If this equipment fails, which spaces/equipment are impacted within N hops?
-- Parametres: $1 = EQUIPMENT_ID, $2 = MAX_HOPS

WITH RECURSIVE propagation AS (
    SELECT
        n.id AS node_id,
        n.node_type,
        n.name AS node_name,
        0 AS hop_distance,
        ''::text AS via_relation
    FROM nodes n
    WHERE n.id = $1

    UNION ALL

    SELECT
        n.id AS node_id,
        n.node_type,
        n.name AS node_name,
        p.hop_distance + 1,
        e.rel_type AS via_relation
    FROM propagation p
    JOIN edges e ON (e.source_id = p.node_id OR e.target_id = p.node_id)
        AND e.rel_type IN ('FEEDS', 'SERVES', 'POWERS')
    JOIN nodes n ON n.id = CASE WHEN e.source_id = p.node_id THEN e.target_id ELSE e.source_id END
    WHERE p.hop_distance < $2
)
SELECT DISTINCT node_id, node_type, node_name, hop_distance, via_relation
FROM propagation
WHERE hop_distance > 0
ORDER BY hop_distance, node_type, node_id;
