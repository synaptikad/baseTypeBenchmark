-- Q7: Sensor Drift Detection (M2/O2 TimescaleDB part)
-- Benchmark: Statistical analysis using TimescaleDB aggregates
-- Parameters: $BUILDING_ID (for point filtering), $DATE_START, $DATE_END
-- Note: Building filter applied via point_ids from graph query

SELECT
    point_id,
    AVG(value) as mean_value,
    STDDEV(value) as std_value,
    CASE
        WHEN ABS(AVG(value)) > 0.001 THEN STDDEV(value) / ABS(AVG(value))
        ELSE STDDEV(value)
    END as coefficient_of_variation,
    COUNT(*) as sample_count
FROM timeseries
WHERE point_id = ANY($POINT_IDS)
  AND time >= '$DATE_START'::timestamptz
  AND time < '$DATE_END'::timestamptz
GROUP BY point_id
HAVING COUNT(*) > 100
ORDER BY coefficient_of_variation DESC
LIMIT 20;
