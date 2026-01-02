-- Q13: Office Hours Comfort (M2/O2 TimescaleDB part)
-- Benchmark: Hour filtering with time_bucket (efficient vs M1 dechunking)
-- Parameters: $POINT_IDS (array from graph), $DATE_START, $DATE_END
-- Note: Graph returns thermostat + occupancy points for office spaces

SELECT
    EXTRACT(DOW FROM time) as office_hour,
    point_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_count
FROM timeseries
WHERE point_id = ANY($POINT_IDS)
  AND time >= '$DATE_START'::timestamptz
  AND time < '$DATE_END'::timestamptz
  AND EXTRACT(HOUR FROM ts.time) BETWEEN 9 AND 17  -- Office hours (9h-17h)
GROUP BY office_hour, point_id
ORDER BY point_id;
