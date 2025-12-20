-- Q9: Tenant Carbon Footprint (M2/O2 TimescaleDB part)
-- Benchmark: Aggregate power consumption for carbon calculation
-- Parameters: $POINT_IDS (array from graph), $DATE_START, $DATE_END
-- Note: Graph returns power points, carbon factor applied client-side

SELECT
    point_id,
    SUM(value) as total_kwh,
    AVG(value) as avg_power,
    COUNT(*) as sample_count
FROM timeseries
WHERE point_id = ANY($POINT_IDS)
  AND time >= '$DATE_START'::timestamptz
  AND time < '$DATE_END'::timestamptz
GROUP BY point_id;
