-- Q6: Timeseries Hourly Aggregation
-- Benchmark: TimescaleDB time_bucket + aggregation (key TS query)
-- Parameters: $POINT_ID - point to aggregate, $DATE_START/$DATE_END - time range

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
