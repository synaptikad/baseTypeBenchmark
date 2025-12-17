-- Q6: Timeseries Hourly Aggregation
-- Benchmark: TimescaleDB time_bucket + aggregation (key TS query)
-- Pattern: Hourly averages for last 24h

SELECT
    time_bucket('1 hour', time) as hour,
    point_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_count
FROM timeseries
WHERE time >= NOW() - INTERVAL '24 hours'
GROUP BY hour, point_id
ORDER BY hour DESC, point_id
LIMIT 1000;
