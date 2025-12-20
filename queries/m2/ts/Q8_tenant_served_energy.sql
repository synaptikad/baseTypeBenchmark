-- Q8: Tenant Energy Consumption (M2/O2 TimescaleDB part)
-- Benchmark: Aggregate energy for points identified by graph query
-- Parameters: $POINT_IDS (array from graph), $DATE_START, $DATE_END
-- Note: Graph query returns point_ids for tenant's power points

SELECT
    SUM(value) as total_energy,
    AVG(value) as avg_power,
    COUNT(DISTINCT point_id) as point_count,
    COUNT(*) as sample_count
FROM timeseries
WHERE point_id = ANY($POINT_IDS)
  AND time >= '$DATE_START'::timestamptz
  AND time < '$DATE_END'::timestamptz;
