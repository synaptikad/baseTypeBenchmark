-- Q7: Sensor Drift Detection - Top 20 drifting sensors
-- Benchmark: Statistical analysis over time (anomaly detection)
-- Pattern: Variance analysis

WITH sensor_stats AS (
    SELECT
        point_id,
        AVG(value) as mean_value,
        STDDEV(value) as std_value,
        COUNT(*) as sample_count,
        MAX(value) - MIN(value) as range_value
    FROM timeseries
    WHERE time >= NOW() - INTERVAL '7 days'
    GROUP BY point_id
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
