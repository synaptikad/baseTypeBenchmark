-- Q1: Energy Chain - Traverse equipment → meter → point → timeseries
-- Benchmark: Graph traversal + JOIN performance (structural query)
-- Priority: Query execution performance (exploitation)

WITH RECURSIVE energy_chain AS (
    -- Start from equipment nodes
    SELECT
        n.id,
        n.type,
        n.name,
        n.building_id,
        1 as depth,
        ARRAY[n.id] as path
    FROM nodes n
    WHERE n.type = 'Equipment'

    UNION ALL

    -- Follow FEEDS, HAS_POINT, MEASURES relationships
    SELECT
        child.id,
        child.type,
        child.name,
        child.building_id,
        ec.depth + 1,
        ec.path || child.id
    FROM energy_chain ec
    JOIN edges e ON e.src_id = ec.id
    JOIN nodes child ON child.id = e.dst_id
    WHERE ec.depth < 4
      AND e.rel_type IN ('FEEDS', 'HAS_POINT', 'MEASURES')
      AND NOT child.id = ANY(ec.path)
)
SELECT
    building_id,
    type,
    COUNT(*) as node_count,
    MAX(depth) as max_depth
FROM energy_chain
GROUP BY building_id, type
ORDER BY building_id, node_count DESC;
