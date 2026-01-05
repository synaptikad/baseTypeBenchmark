-- Q9: Tenant Carbon Footprint (M2/O2 TimescaleDB part)
-- Benchmark: Aggregate energy consumption for carbon calculation
-- Parameters: $POINT_IDS (array from graph), $DATE_START, $DATE_END
-- Note: Graph returns energy counter points, carbon factor applied here

SELECT
    -- For cumulative energy counters: delta = last - first
    MAX(value) - MIN(value) as total_kwh,
    COUNT(DISTINCT point_id) as meter_count,
    COUNT(*) as sample_count,
    -- French grid carbon intensity: ~52g CO2/kWh (2024 average)
    (MAX(value) - MIN(value)) * 0.052 as carbon_kg,
    (MAX(value) - MIN(value)) * 0.052 / 1000.0 as carbon_tonnes
FROM timeseries
WHERE point_id = ANY($POINT_IDS)
  AND time >= '$DATE_START'::timestamptz
  AND time < '$DATE_END'::timestamptz;
