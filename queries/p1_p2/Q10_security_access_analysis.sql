-- Q10: Security Access Analysis
-- Benchmark: Access control pattern analysis
-- Parameters: $ZONE_ID - zone to analyze, $DATE_START/$DATE_END (for event TS)
-- Pattern: Zone → Access points → Events

SELECT
    z.id as zone_id,
    z.name as zone_name,
    z.building_id,
    ap.id as access_point_id,
    ap.name as access_point_name,
    eq.id as equipment_id,
    eq.name as equipment_name
FROM nodes z
LEFT JOIN edges e1 ON e1.src_id = z.id AND e1.rel_type = 'CONTAINS'
LEFT JOIN nodes ap ON ap.id = e1.dst_id AND ap.type = 'AccessPoint'
LEFT JOIN edges e2 ON e2.src_id = z.id
LEFT JOIN nodes eq ON eq.id = e2.dst_id AND eq.type = 'Equipment'
WHERE z.id = '$ZONE_ID'
ORDER BY ap.name, eq.name;
