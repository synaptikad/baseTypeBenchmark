-- Q12: Full Building Analytics (M2/O2 TimescaleDB part)
-- Benchmark: Building-wide KPI aggregation
-- Parameters: $POINT_IDS (array from graph), $DATE_START, $DATE_END
-- Note: Graph returns all points for building

SELECT
    time_bucket('1 day', time) as day,
    COUNT(DISTINCT point_id) as active_points,
    AVG(value) as avg_value,
    SUM(value) as total_value,
    COUNT(*) as sample_count
FROM timeseries
WHERE point_id = ANY($POINT_IDS)
  AND time >= '$DATE_START'::timestamptz
  AND time < '$DATE_END'::timestamptz
GROUP BY day
ORDER BY day DESC;
