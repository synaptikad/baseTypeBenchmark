-- Q6: Timeseries Hourly Aggregation (M2/O2 TimescaleDB part)
-- Benchmark: time_bucket aggregation for a single point
-- Parameters: $POINT_ID, $DATE_START, $DATE_END
-- Note: For M2/O2, point_id comes from graph query or is provided directly

SELECT
    time_bucket('1 hour', time) as hour,
    point_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_count
FROM timeseries
WHERE point_id = '$POINT_ID'
  AND time >= '$DATE_START'::timestamptz
  AND time < '$DATE_END'::timestamptz
GROUP BY hour, point_id
ORDER BY hour DESC;
