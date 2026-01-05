-- Q8: Tenant Energy Consumption (via METERS_TENANT)
-- Benchmark: Direct relationship traversal + timeseries aggregation
-- Parameters: $TENANT_ID - tenant to analyze, $DATE_START/$DATE_END - time range
-- Pattern: Tenant <- METERS_TENANT <- SubMeter -> HAS_POINT -> Point(energy) -> Timeseries
-- P2: Uses JSONB property access (properties->>'quantity')
-- Complexity: 2 hops (vs 5 hops in previous version)

WITH tenant_meter_points AS (
    SELECT DISTINCT
        t.id as tenant_id,
        t.name as tenant_name,
        m.id as meter_id,
        m.name as meter_name,
        p.id as point_id
    FROM nodes t
    -- METERS_TENANT: SubMeter -> Tenant (direction in data)
    JOIN edges e1 ON e1.dst_id = t.id AND e1.rel_type = 'METERS_TENANT'
    JOIN nodes m ON m.id = e1.src_id AND m.type = 'Equipment'
    -- HAS_POINT: SubMeter -> Point
    JOIN edges e2 ON e2.src_id = m.id AND e2.rel_type = 'HAS_POINT'
    JOIN nodes p ON p.id = e2.dst_id AND p.type = 'Point'
    WHERE t.id = '$TENANT_ID'
      AND t.type = 'Tenant'
      AND p.properties->>'quantity' = 'energy'
)
SELECT
    tp.tenant_id,
    tp.tenant_name,
    SUM(ts.value) as total_energy_kwh,
    MAX(ts.value) - MIN(ts.value) as delta_energy_kwh,
    COUNT(DISTINCT tp.meter_id) as meter_count,
    COUNT(DISTINCT tp.point_id) as point_count,
    COUNT(ts.value) as sample_count
FROM tenant_meter_points tp
JOIN timeseries ts ON ts.point_id = tp.point_id
WHERE ts.time >= '$DATE_START'::timestamptz
  AND ts.time < '$DATE_END'::timestamptz
GROUP BY tp.tenant_id, tp.tenant_name
ORDER BY total_energy_kwh DESC;
