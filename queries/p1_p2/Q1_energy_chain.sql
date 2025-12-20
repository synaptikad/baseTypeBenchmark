-- Q1: Energy Chain - Traverse from meter through FEEDS chain
-- Benchmark: Graph traversal + JOIN performance (structural query)
-- Parameter: $METER_ID - starting meter for energy chain traversal
-- Priority: Query execution performance (exploitation)

WITH RECURSIVE energy_chain AS (
    -- Start from specified meter
    SELECT
        n.id,
        n.type,
        n.name,
        n.building_id,
        1 as depth,
        ARRAY[n.id] as path
    FROM nodes n
    WHERE n.id = '$METER_ID'

    UNION ALL

    -- Follow FEEDS relationships downstream (up to 10 hops per spec)
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
    WHERE ec.depth < 10
      AND e.rel_type = 'FEEDS'
      AND NOT child.id = ANY(ec.path)
)
SELECT
    id,
    type,
    name,
    depth,
    path
FROM energy_chain
ORDER BY depth, type;
