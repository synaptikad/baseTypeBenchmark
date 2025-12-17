-- Q3: Space Services - What equipment serves each space?
-- Benchmark: Multi-hop traversal with aggregation
-- Pattern: Space → Equipment mapping

SELECT
    s.id as space_id,
    s.name as space_name,
    s.building_id,
    COUNT(DISTINCT eq.id) as equipment_count,
    ARRAY_AGG(DISTINCT eq.type) as equipment_types
FROM nodes s
JOIN edges e1 ON e1.src_id = s.id OR e1.dst_id = s.id
JOIN nodes eq ON (eq.id = e1.src_id OR eq.id = e1.dst_id) AND eq.id != s.id
WHERE s.type = 'Space'
  AND eq.type = 'Equipment'
  AND e1.rel_type IN ('CONTAINS', 'SERVES', 'LOCATED_IN')
GROUP BY s.id, s.name, s.building_id
ORDER BY equipment_count DESC
LIMIT 100;
