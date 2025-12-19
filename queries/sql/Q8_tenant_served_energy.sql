-- Q8: Tenant Energy Consumption
-- Benchmark: Multi-hop traversal + timeseries aggregation (hybrid query)
-- Parameters: $TENANT_ID - tenant to analyze, $DATE_START/$DATE_END - time range
-- Pattern: Tenant → Spaces → Equipment → Points → Timeseries

WITH tenant_points AS (
    SELECT DISTINCT
        t.id as tenant_id,
        t.name as tenant_name,
        p.id as point_id
    FROM nodes t
    JOIN edges e1 ON e1.src_id = t.id AND e1.rel_type = 'OCCUPIES'
    JOIN nodes sp ON sp.id = e1.dst_id AND sp.type = 'Space'
    JOIN edges e2 ON (e2.src_id = sp.id OR e2.dst_id = sp.id) AND e2.rel_type IN ('SERVES', 'CONTAINS')
    JOIN nodes eq ON (eq.id = e2.dst_id OR eq.id = e2.src_id) AND eq.type = 'Equipment' AND eq.id != sp.id
    JOIN edges e3 ON e3.src_id = eq.id AND e3.rel_type = 'HAS_POINT'
    JOIN nodes p ON p.id = e3.dst_id AND p.type = 'Point'
    JOIN edges e4 ON e4.src_id = p.id AND e4.rel_type = 'MEASURES' AND e4.dst_id = 'Power'
    WHERE t.id = '$TENANT_ID'
)
SELECT
    tp.tenant_id,
    tp.tenant_name,
    SUM(ts.value) as total_energy,
    AVG(ts.value) as avg_power,
    COUNT(DISTINCT tp.point_id) as point_count
FROM tenant_points tp
JOIN timeseries ts ON ts.point_id = tp.point_id
WHERE ts.time >= '$DATE_START'::timestamptz
  AND ts.time < '$DATE_END'::timestamptz
GROUP BY tp.tenant_id, tp.tenant_name
ORDER BY total_energy DESC;
