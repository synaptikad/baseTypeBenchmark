-- Q31: Rolling Aggregation
-- Status: NATIVE pour P1 (Window functions PostgreSQL)
-- Semantic: Calculate rolling averages and percentiles on timeseries
-- Parametres: $1 = BUILDING_ID, $2 = DATE_START, $3 = DATE_END

WITH building_points AS (
    SELECT DISTINCT p.id AS point_id
    FROM floors f
    JOIN spaces s ON s.floor_id = f.id
    JOIN edges e ON e.target_id = s.id AND e.rel_type = 'SERVES'
    JOIN equipment eq ON eq.id = e.source_id
    JOIN points p ON p.equipment_id = eq.id
    WHERE f.building_id = $1
),
hourly_data AS (
    SELECT
        ts.point_id,
        time_bucket('1 hour', ts.time) AS time_bucket,
        AVG(ts.value) AS avg_value,
        ts.value
    FROM ts.timeseries ts
    JOIN building_points bp ON bp.point_id = ts.point_id
    WHERE ts.time >= $2 AND ts.time <= $3
    GROUP BY ts.point_id, time_bucket('1 hour', ts.time), ts.value
)
SELECT
    point_id,
    time_bucket,
    AVG(avg_value) OVER (
        PARTITION BY point_id
        ORDER BY time_bucket
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) AS rolling_avg,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY avg_value) OVER (
        PARTITION BY point_id
    ) AS p95,
    STDDEV(avg_value) OVER (
        PARTITION BY point_id
    ) AS stddev
FROM hourly_data
ORDER BY point_id, time_bucket
LIMIT 1000;
