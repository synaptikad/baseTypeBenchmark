-- Q9: Tenant Carbon Footprint (via METERS_TENANT)
-- Benchmark: Complex aggregation with carbon factor calculation
-- Parameters: $TENANT_ID - tenant to analyze, $DATE_START/$DATE_END - time range
-- Pattern: Tenant <- METERS_TENANT <- SubMeter -> HAS_POINT -> Point(energy) -> Timeseries
-- P2: Uses JSONB property access (properties->>'quantity')
-- Complexity: 2 hops + carbon calculation

WITH tenant_energy AS (
    SELECT DISTINCT
        t.id as tenant_id,
        t.name as tenant_name,
        t.properties->>'building_id' as building_id,
        m.id as meter_id,
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
),
energy_consumption AS (
    SELECT
        te.tenant_id,
        te.tenant_name,
        te.building_id,
        -- For cumulative energy counters: use last - first value
        MAX(ts.value) - MIN(ts.value) as total_kwh,
        COUNT(DISTINCT te.meter_id) as meter_count
    FROM tenant_energy te
    JOIN timeseries ts ON ts.point_id = te.point_id
    WHERE ts.time >= '$DATE_START'::timestamptz
      AND ts.time < '$DATE_END'::timestamptz
    GROUP BY te.tenant_id, te.tenant_name, te.building_id
)
SELECT
    tenant_id,
    tenant_name,
    building_id,
    total_kwh,
    meter_count,
    -- French grid carbon intensity: ~52g CO2/kWh (2024 average)
    -- Source: RTE eco2mix
    total_kwh * 0.052 as carbon_kg,
    total_kwh * 0.052 / 1000.0 as carbon_tonnes
FROM energy_consumption
ORDER BY carbon_kg DESC;
