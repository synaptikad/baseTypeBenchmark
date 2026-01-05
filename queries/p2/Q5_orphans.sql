-- Q5: Orphan Detection - Nodes without relationships
-- Benchmark: Anti-join pattern (data quality query)
-- Pattern: Find disconnected nodes
-- P2: JSONB schema - structural queries are identical to P1

SELECT
    n.type,
    COUNT(*) as orphan_count
FROM nodes n
LEFT JOIN edges e_out ON e_out.src_id = n.id
LEFT JOIN edges e_in ON e_in.dst_id = n.id
WHERE e_out.src_id IS NULL
  AND e_in.dst_id IS NULL
GROUP BY n.type
ORDER BY orphan_count DESC;
