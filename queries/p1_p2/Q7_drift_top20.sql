-- Q7: Sensor Drift Detection - Top 20 drifting sensors in building
-- Benchmark: Statistical analysis over time (anomaly detection)
-- Parameters: $BUILDING_ID - building to analyze, $DATE_START/$DATE_END - time range
-- Digital Twin pattern: uses denormalized building_id in timeseries (no JOIN on 30M rows)

WITH sensor_stats AS (
    SELECT
        t.point_id,
        AVG(t.value) as mean_value,
        STDDEV(t.value) as std_value,
        COUNT(*) as sample_count,
        MAX(t.value) - MIN(t.value) as range_value
    FROM timeseries t
    WHERE t.building_id = '$BUILDING_ID'
      AND t.time >= '$DATE_START'::timestamptz
      AND t.time < '$DATE_END'::timestamptz
    GROUP BY t.point_id
    HAVING COUNT(*) > 100
),
drift_score AS (
    SELECT
        point_id,
        mean_value,
        std_value,
        sample_count,
        CASE
            WHEN mean_value != 0 THEN std_value / ABS(mean_value)
            ELSE std_value
        END as coefficient_of_variation
    FROM sensor_stats
)
SELECT
    d.point_id,
    n.name as point_name,
    d.mean_value,
    d.std_value,
    d.coefficient_of_variation as cv,
    d.sample_count
FROM drift_score d
LEFT JOIN nodes n ON n.id = d.point_id
ORDER BY d.coefficient_of_variation DESC
LIMIT 20;
