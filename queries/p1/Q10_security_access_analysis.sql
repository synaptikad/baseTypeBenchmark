-- Q10: Floor Security & Equipment Analysis
-- Benchmark: Access control pattern analysis via floor traversal
-- Parameters: $FLOOR_ID - floor to analyze
-- Pattern: Floor -> Spaces -> Equipment
-- P1: Uses direct column access (equipment_type)

SELECT
    f.id as floor_id,
    f.name as floor_name,
    f.building_id,
    sp.id as space_id,
    sp.name as space_name,
    eq.id as equipment_id,
    eq.name as equipment_name,
    eq.equipment_type
FROM nodes f
JOIN edges e1 ON e1.src_id = f.id AND e1.rel_type = 'CONTAINS'
JOIN nodes sp ON sp.id = e1.dst_id AND sp.type = 'Space'
LEFT JOIN edges e2 ON e2.src_id = sp.id AND e2.rel_type = 'CONTAINS'
LEFT JOIN nodes eq ON eq.id = e2.dst_id AND eq.type = 'Equipment'
WHERE f.id = '$FLOOR_ID'
ORDER BY sp.name, eq.name;
