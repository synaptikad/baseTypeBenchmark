-- Q4: Inventory - Temperature points per floor
-- Benchmark: Filtering + aggregation (typical BMS inventory query)
-- Pattern: Filter by type and quantity

SELECT
    f.id as floor_id,
    f.name as floor_name,
    f.building_id,
    COUNT(DISTINCT p.id) as temp_point_count
FROM nodes f
JOIN edges e1 ON e1.src_id = f.id
JOIN nodes sp ON sp.id = e1.dst_id AND sp.type = 'Space'
JOIN edges e2 ON e2.src_id = sp.id
JOIN nodes eq ON eq.id = e2.dst_id AND eq.type = 'Equipment'
JOIN edges e3 ON e3.src_id = eq.id
JOIN nodes p ON p.id = e3.dst_id AND p.type = 'Point'
JOIN edges e4 ON e4.src_id = p.id AND e4.rel_type = 'MEASURES'
WHERE f.type = 'Floor'
  AND e1.rel_type = 'CONTAINS'
  AND e2.rel_type IN ('CONTAINS', 'SERVES')
  AND e3.rel_type = 'HAS_POINT'
  AND e4.dst_id = 'Temperature'
GROUP BY f.id, f.name, f.building_id
ORDER BY temp_point_count DESC;
