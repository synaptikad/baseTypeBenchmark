-- Q11: IT Infrastructure Impact (M2/O2 TimescaleDB part)
-- Benchmark: Server room environmental monitoring
-- Parameters: $POINT_IDS (array from graph), $DATE_START, $DATE_END
-- Note: Graph returns temp/humidity points for server rooms

SELECT
    point_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    STDDEV(value) as std_value,
    COUNT(*) as sample_count
FROM timeseries
WHERE point_id = ANY($POINT_IDS)
  AND time >= '$DATE_START'::timestamptz
  AND time < '$DATE_END'::timestamptz
GROUP BY point_id;
