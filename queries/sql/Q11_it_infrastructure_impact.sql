-- Q11: IT Infrastructure Impact Analysis
-- Benchmark: Network/IT equipment dependency analysis
-- Pattern: Server room → IT equipment → Network

WITH it_equipment AS (
    SELECT
        n.id,
        n.name,
        n.type,
        n.building_id
    FROM nodes n
    WHERE n.type = 'Equipment'
      AND (n.name ILIKE '%server%'
           OR n.name ILIKE '%network%'
           OR n.name ILIKE '%switch%'
           OR n.name ILIKE '%router%'
           OR n.name ILIKE '%UPS%')
)
SELECT
    sp.id as space_id,
    sp.name as space_name,
    sp.building_id,
    COUNT(DISTINCT it.id) as it_equipment_count,
    ARRAY_AGG(DISTINCT it.name) as equipment_names
FROM nodes sp
JOIN edges e ON e.src_id = sp.id AND e.rel_type = 'CONTAINS'
JOIN it_equipment it ON it.id = e.dst_id
WHERE sp.type = 'Space'
GROUP BY sp.id, sp.name, sp.building_id
HAVING COUNT(DISTINCT it.id) > 0
ORDER BY it_equipment_count DESC
LIMIT 20;
