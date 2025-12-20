-- Q13: Friday Office Comfort (M2/O2 TimescaleDB part)
-- Benchmark: DOW filtering with time_bucket (efficient vs M1 dechunking)
-- Parameters: $POINT_IDS (array from graph), $DATE_START, $DATE_END
-- Note: Graph returns thermostat + occupancy points for office spaces

SELECT
    EXTRACT(DOW FROM time) as day_of_week,
    point_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_count
FROM timeseries
WHERE point_id = ANY($POINT_IDS)
  AND time >= '$DATE_START'::timestamptz
  AND time < '$DATE_END'::timestamptz
  AND EXTRACT(DOW FROM time) = 5  -- Friday
GROUP BY day_of_week, point_id
ORDER BY point_id;
