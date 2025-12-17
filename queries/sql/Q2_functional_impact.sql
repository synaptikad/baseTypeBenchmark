-- Q2: Functional Impact Analysis
-- What spaces are affected if equipment X fails?
-- Benchmark: Reverse traversal (impact analysis pattern)

WITH RECURSIVE impact_analysis AS (
    -- Start from a single equipment (use subquery to avoid LIMIT in CTE base)
    SELECT
        n.id,
        n.type,
        n.name,
        n.building_id,
        1 as hop_distance,
        ARRAY[n.id] as impact_path
    FROM nodes n
    WHERE n.id = (SELECT id FROM nodes WHERE type = 'Equipment' ORDER BY id LIMIT 1)

    UNION ALL

    -- Traverse reverse relationships to find affected entities
    SELECT
        parent.id,
        parent.type,
        parent.name,
        parent.building_id,
        ia.hop_distance + 1,
        ia.impact_path || parent.id
    FROM impact_analysis ia
    JOIN edges e ON e.dst_id = ia.id
    JOIN nodes parent ON parent.id = e.src_id
    WHERE ia.hop_distance < 5
      AND e.rel_type IN ('CONTAINS', 'SERVES', 'FEEDS')
      AND NOT parent.id = ANY(ia.impact_path)
)
SELECT
    type,
    COUNT(DISTINCT id) as affected_count,
    AVG(hop_distance) as avg_distance
FROM impact_analysis
WHERE type IN ('Space', 'Floor', 'Zone')
GROUP BY type
ORDER BY affected_count DESC;
