-- Q10: Security Access Analysis
-- Benchmark: Access control pattern analysis
-- Pattern: Zone → Access points → Events

SELECT
    z.id as zone_id,
    z.name as zone_name,
    z.building_id,
    COUNT(DISTINCT ap.id) as access_point_count,
    COUNT(DISTINCT eq.id) as security_equipment_count
FROM nodes z
LEFT JOIN edges e1 ON e1.src_id = z.id AND e1.rel_type = 'CONTAINS'
LEFT JOIN nodes ap ON ap.id = e1.dst_id AND ap.type = 'AccessPoint'
LEFT JOIN edges e2 ON e2.src_id = z.id
LEFT JOIN nodes eq ON eq.id = e2.dst_id AND eq.type = 'Equipment'
WHERE z.type = 'Zone'
GROUP BY z.id, z.name, z.building_id
ORDER BY access_point_count DESC, security_equipment_count DESC
LIMIT 50;
